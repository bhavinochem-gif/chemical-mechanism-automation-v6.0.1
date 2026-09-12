from __future__ import annotations
from typing import Dict, List, Any
from .reaction_step_model import ReactionStep
from .direct_graph_engine import validate_structure

def validate_step(step: ReactionStep) -> Dict[str, Any]:
    reactants = [validate_structure(x) for x in step.reactants if x]
    products = [validate_structure(x) for x in step.products if x]
    return {
        "valid": bool(reactants and products and all(x.get("valid") for x in reactants + products)),
        "reactants": reactants,
        "products": products,
    }

def validate_route(steps: List[ReactionStep]) -> Dict[str, Any]:
    checks = [validate_step(s) for s in steps]
    return {
        "valid": bool(steps and all(c.get("valid") for c in checks)),
        "steps": checks,
        "step_count": len(steps),
    }

def route_as_dicts(steps: List[ReactionStep]) -> List[Dict[str, Any]]:
    return [s.to_dict() for s in steps]

def suggested_next_substrate(steps: List[ReactionStep]) -> str:
    if not steps:
        return ""
    last = steps[-1]
    return last.products[0] if last.products else ""
