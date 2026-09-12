"""Optional reagent-signature evidence.

V6.4 never uses a signature as a default/fallback reaction assignment. A signature
is only supplementary evidence for the CURRENT upload and requires strong matching.
"""
import re

SIGNATURES = {
    "Pd-catalyzed ketone alpha-arylation": {
        "terms": [
            ("palladium acetate", "pd(oac)2"),
            ("sodium tertiary butoxide", "sodium tert-butoxide", "naotbu"),
            ("tri tertiary butyl phosphonium tetrafluoroborate", "tri-tert-butylphosphonium", "t-bu3p"),
            ("toluene",),
        ],
        "min_groups": 4,
    }
}

def _norm(text):
    t = (text or "").lower().replace("₂", "2").replace("–", "-").replace("—", "-")
    t = re.sub(r"\s+", " ", t)
    return t

def signature_hits(text):
    t = _norm(text)
    out = []
    for name, cfg in SIGNATURES.items():
        matched = []
        for aliases in cfg["terms"]:
            if any(a in t for a in aliases):
                matched.append(aliases[0])
        if len(matched) >= cfg["min_groups"]:
            out.append({"name":name, "matched":matched, "score":len(matched)/len(cfg["terms"])})
    return sorted(out, key=lambda x:x["score"], reverse=True)

def match_uploaded_route(text):
    """Backward-compatible boolean; true only for a complete strong signature."""
    return bool(signature_hits(text))
