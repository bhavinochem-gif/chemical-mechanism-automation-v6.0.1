from __future__ import annotations
from typing import Dict, Any, List
from .reaction_step_model import ReactionStep
from .direct_graph_engine import canonical_smiles

def parse_reaction_smiles(text: str, step_no: int = 1) -> ReactionStep:
    raw = (text or "").strip()
    if ">>" in raw:
        left, right = raw.split(">>", 1)
        middle = ""
    elif raw.count(">") >= 2:
        left, middle, right = raw.split(">", 2)
    else:
        raise ValueError("Use reaction SMILES as reactants>>products or reactants>reagents>products.")

    reactants = [canonical_smiles(x) for x in left.split(".") if x.strip()]
    products = [canonical_smiles(x) for x in right.split(".") if x.strip()]
    reactants = [x for x in reactants if x]
    products = [x for x in products if x]
    return ReactionStep(
        step_no=step_no,
        reactants=reactants,
        products=products,
        reagents=middle.strip(),
    )

def parse_rxn_block(block: str, step_no: int = 1) -> ReactionStep:
    try:
        from rdkit.Chem import rdChemReactions
        from rdkit import Chem
    except Exception as exc:
        raise ValueError(f"RDKit reaction support unavailable: {exc}")

    rxn = rdChemReactions.ReactionFromRxnBlock(block, sanitize=True, removeHs=False)
    if rxn is None:
        raise ValueError("Could not parse RXN block.")
    reactants = [
        Chem.MolToSmiles(m, canonical=True, isomericSmiles=True)
        for m in rxn.GetReactants()
    ]
    products = [
        Chem.MolToSmiles(m, canonical=True, isomericSmiles=True)
        for m in rxn.GetProducts()
    ]
    return ReactionStep(step_no=step_no, reactants=reactants, products=products)
