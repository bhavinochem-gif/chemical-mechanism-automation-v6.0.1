"""Compatibility wrapper around V6.5 Advanced OCSR."""
from .advanced_ocrs import recognize_candidates
from .smiles_verifier import validate_candidate


def validate_smiles(smiles):
    v = validate_candidate(smiles)
    return {
        "valid": v.get("valid", False),
        "smiles": v.get("canonical_smiles", "") or v.get("input", ""),
        "reason": v.get("reason", ""),
        "atoms": v.get("atoms", 0),
        "bonds": v.get("bonds", 0),
        "formula": v.get("formula", ""),
    }


def recognize_structure(image, role_hint="unknown", provider="gemini", use_ai=True):
    r = recognize_candidates(image, role_hint, provider, use_ai)
    top = r.get("accepted") or (r.get("candidates") or [None])[0]
    if not top:
        return {
            "role":r.get("role", role_hint),"name":r.get("name","Structure recognition incomplete"),
            "smiles":"","confidence":0.0,"visual_features":r.get("visible_features",[]),
            "uncertainties":r.get("global_uncertainties",[]),"validation":validate_smiles(""),
            "ocrs":r,
        }
    return {
        "role":r.get("role", role_hint),"name":top.get("name") or r.get("name",""),
        "smiles":top.get("canonical_smiles","") if top.get("valid") else "",
        "confidence":top.get("score", top.get("confidence",0)),
        "visual_features":r.get("visible_features",[]),
        "uncertainties":top.get("uncertainties",[])+r.get("global_uncertainties",[]),
        "validation":validate_smiles(top.get("canonical_smiles", "")),
        "ocrs":r,
    }
