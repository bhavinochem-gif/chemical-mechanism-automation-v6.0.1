from .electron_flow_engine import infer_electron_flow
from .intermediate_engine import generate_intermediates
from .stereochemistry_engine import analyze_stereochemistry
from .plausibility_engine import assess
from .named_reaction_engine import rank_named_reactions
from .mechanism_rules import rules_for

class MechanismEngine:
    def __init__(self, db):
        self.db = db

    def analyze_step(self, row, center, classification):
        rc = classification.get("reaction_class", "Requires structure verification")
        flows = infer_electron_flow(rc, center.get("bond_changes", []))
        structure_verified = center.get("status") == "ok"
        classified = rc.lower() not in {"requires structure verification", "unclassified transformation", ""}
        confidence = float(classification.get("confidence", 0.0) or 0.0)
        if not structure_verified:
            confidence = min(confidence, 0.80)
        m = {
            "step": row.get("Step"),
            "reaction": row.get("Reaction", ""),
            "reaction_center": center,
            "classification": classification,
            "named_reaction_candidates": rank_named_reactions(rc, row, self.db),
            "mechanistic_rules": rules_for(rc),
            "electron_flow": flows,
            "intermediates": generate_intermediates(rc, flows, row),
            "stereochemistry": analyze_stereochemistry(str(row.get("Starting Material", "") or ""), str(row.get("Product", "") or "")),
            "plausibility": assess(center, classification, row),
            "verification": {
                "structure_verified": structure_verified,
                "bond_changes_present": bool(center.get("bond_changes")),
                "reaction_classified": classified,
                "exact_atom_mapping_complete": structure_verified and bool(center.get("atom_mapping")),
            },
            "confidence": round(confidence, 3),
        }
        if not structure_verified:
            m["limitations"] = ["Exact atom mapping and structure-derived mechanism await validated reactant and product molecular graphs."]
        return m
