from __future__ import annotations
from typing import Dict, Any
from .reaction_center import analyze_reaction_center
from .reaction_classifier import classify_reaction
from .mechanism_engine import MechanismEngine
from .intermediate_structure_generator import generate_intermediate_structures

def analyze_direct_step(step, chemistry_db) -> Dict[str, Any]:
    rs = step.reactant_smiles
    ps = step.product_smiles
    if not rs or not ps:
        return {
            "status": "needs_structure",
            "reaction_center": {"status": "needs_structure_verification", "bond_changes": [], "confidence": 0.0},
            "classification": {"reaction_class": "Requires exact structures", "confidence": 0.0},
            "mechanism": {},
            "intermediates": [],
        }

    center = analyze_reaction_center(rs, ps)
    row = step.classifier_row()
    classification = classify_reaction(center, row, chemistry_db)
    mechanism = MechanismEngine(chemistry_db).analyze_step(row, center, classification)
    intermediates = generate_intermediate_structures(
        classification.get("reaction_class", ""), rs, ps, mechanism
    )
    return {
        "status": "ok" if center.get("status") == "ok" else "provisional",
        "reaction_center": center,
        "classification": classification,
        "mechanism": mechanism,
        "intermediates": intermediates,
    }
