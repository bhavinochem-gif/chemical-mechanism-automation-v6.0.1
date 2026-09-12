from __future__ import annotations

from typing import Dict, List
from PIL import Image

from .ocrs_preprocessor import make_ocrs_variants
from .smiles_verifier import validate_candidate
from .vision_json import call_vision_json
from .mechanism_renderer import render_structure

OCSR_PROMPT = r'''
You are performing optical chemical structure recognition (OCSR) on ONE isolated chemical drawing.
The attached images are alternative renderings of the SAME structure crop, not different molecules.
Read the molecular graph from the drawing. Do NOT infer the reaction and do NOT use reagent knowledge to invent the structure.

Return JSON only:
{
  "role":"substrate|reagent_structure|product|unknown",
  "name":"short visual/chemical description",
  "visible_features":["heteroatoms, carbonyls, rings, halogens, protecting groups, wedge/dash information actually visible"],
  "candidates":[
    {
      "smiles":"candidate isomeric SMILES",
      "confidence":0.0,
      "stereo_confidence":0.0,
      "evidence":["drawing features supporting this candidate"],
      "uncertainties":["specific ambiguous atom/bond/stereo items"]
    }
  ],
  "global_uncertainties":["..." ]
}

Rules:
- Generate up to 4 candidates only when genuinely useful.
- Preserve all visible heteroatoms, halogens, charges, carbonyls, ring fusions, protecting groups, and wedge/dash stereochemistry.
- A wedge/dash bond must not be converted into a confident @/@@ assignment unless its local connectivity is unambiguous.
- Do not simplify a complex fused/bicyclic scaffold into a text description.
- Do not guess invisible hydrogens or substituents to make a familiar drug intermediate.
- If exact connectivity is unreadable, candidates may be empty; state precisely what prevents recognition.
'''

VERIFY_PROMPT = r'''
You are verifying OCSR, not predicting a reaction.
Image 1 is the ORIGINAL chemical structure crop.
Image 2 is a 2D rendering generated from ONE candidate SMILES.
Compare them atom-by-atom and bond-by-bond as far as visible.
Return JSON only:
{
  "match_score":0.0,
  "connectivity_match":0.0,
  "stereo_match":0.0,
  "protecting_group_match":0.0,
  "mismatches":["specific mismatch"],
  "verdict":"match|possible|reject"
}
A high score requires the same ring topology, heteroatom positions, substitution pattern, multiple bonds, protecting groups and stereochemical depiction. Do not reward mere visual similarity.
'''

REPAIR_PROMPT = r'''
You are repairing OCSR candidates that failed RDKit parsing. Use ONLY the original structure crop and the supplied invalid strings.
Correct transcription/syntax only when the drawing supports the corrected molecular graph. Never invent missing rings, substituents, or stereochemistry.
Return JSON only: {"candidates":[{"smiles":"","confidence":0.0,"repair_reason":""}]}.
If no defensible correction exists, return an empty candidates array.
Invalid candidates:
'''


def _normalize_candidates(obj: Dict, role_hint: str) -> List[Dict]:
    out = []
    for c in (obj.get("candidates") or [])[:6]:
        if not isinstance(c, dict):
            continue
        v = validate_candidate(c.get("smiles", ""))
        out.append({
            "smiles": c.get("smiles", ""),
            "canonical_smiles": v.get("canonical_smiles", ""),
            "valid": bool(v.get("valid")),
            "validation": v,
            "confidence": float(c.get("confidence", 0) or 0),
            "stereo_confidence": float(c.get("stereo_confidence", 0) or 0),
            "evidence": c.get("evidence", []) or [],
            "uncertainties": c.get("uncertainties", []) or [],
            "role": obj.get("role") or role_hint,
            "name": obj.get("name", ""),
            "verification": {},
            "score": 0.0,
        })
    return out


def recognize_candidates(image: Image.Image, role_hint: str = "unknown", provider: str = "gemini", use_ai: bool = True, accept_threshold: float = 0.78) -> Dict:
    if not use_ai:
        return {"role": role_hint, "name": "OCSR disabled", "candidates": [], "accepted": None, "status": "disabled"}
    variants = make_ocrs_variants(image)
    prompt = OCSR_PROMPT + f"\nRole hint from page layout only: {role_hint}. The hint is not chemical evidence."
    try:
        raw = call_vision_json(prompt, list(variants.values()), provider)
        candidates = _normalize_candidates(raw if isinstance(raw, dict) else {}, role_hint)
    except Exception as exc:
        return {"role": role_hint, "name": "OCSR failed", "candidates": [], "accepted": None, "status": "error", "error": str(exc)}

    invalid = [c.get("smiles", "") for c in candidates if c.get("smiles") and not c.get("valid")]
    if invalid:
        try:
            repaired = call_vision_json(REPAIR_PROMPT + "\n" + "\n".join(invalid[:4]), [variants["original"], variants["contrast"]], provider)
            extra = _normalize_candidates({"role": raw.get("role", role_hint), "name": raw.get("name", ""), "candidates": repaired.get("candidates", [])}, role_hint)
            # only add genuinely new candidates
            seen = {c.get("canonical_smiles") or c.get("smiles") for c in candidates}
            for c in extra:
                key = c.get("canonical_smiles") or c.get("smiles")
                if key and key not in seen:
                    candidates.append(c); seen.add(key)
        except Exception:
            pass

    original = variants["original"]
    # Verify only the strongest three valid candidates to keep cloud/API cost bounded.
    candidates.sort(key=lambda x: (x.get("valid", False), x.get("confidence", 0)), reverse=True)
    valid_budget = 3
    verified_count = 0
    for c in candidates:
        if not c.get("valid"):
            c["score"] = round(0.25 * c.get("confidence", 0), 3)
            continue
        if verified_count >= valid_budget:
            c["score"] = round(0.45 * c.get("confidence", 0) + 0.05, 3)
            c["verification"] = {"match_score": 0.0, "verdict": "not_run", "mismatches": ["verification budget reached"]}
            continue
        verified_count += 1
        rendered = render_structure(c.get("canonical_smiles", ""), size=(760, 430))
        if rendered is None:
            c["score"] = round(0.55 * c.get("confidence", 0) + 0.1, 3)
            continue
        try:
            verification = call_vision_json(VERIFY_PROMPT, [original, rendered], provider)
        except Exception as exc:
            verification = {"match_score": 0.0, "verdict": "unverified", "mismatches": [str(exc)]}
        c["verification"] = verification if isinstance(verification, dict) else {}
        vm = float(c["verification"].get("match_score", 0) or 0)
        conn = float(c["verification"].get("connectivity_match", vm) or 0)
        c["score"] = round(0.35 * c.get("confidence", 0) + 0.50 * vm + 0.10 * conn + 0.05, 3)

    candidates.sort(key=lambda x: (x.get("valid", False), x.get("score", 0)), reverse=True)
    accepted = None
    if candidates:
        top = candidates[0]
        vm = float(top.get("verification", {}).get("match_score", 0) or 0)
        if top.get("valid") and top.get("score", 0) >= float(accept_threshold) and vm >= 0.72:
            accepted = top
    return {
        "role": raw.get("role") or role_hint if isinstance(raw, dict) else role_hint,
        "name": raw.get("name", "") if isinstance(raw, dict) else "",
        "visible_features": raw.get("visible_features", []) if isinstance(raw, dict) else [],
        "global_uncertainties": raw.get("global_uncertainties", []) if isinstance(raw, dict) else [],
        "candidates": candidates,
        "accepted": accepted,
        "status": "auto_accepted" if accepted else ("needs_confirmation" if candidates else "unrecognized"),
    }
