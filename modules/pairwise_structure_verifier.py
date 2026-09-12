from __future__ import annotations

from typing import Dict
from rdkit import Chem
from rdkit.Chem import rdFMCS


def scaffold_conservation(reactant_smiles: str, product_smiles: str) -> Dict:
    r = Chem.MolFromSmiles(reactant_smiles or "")
    p = Chem.MolFromSmiles(product_smiles or "")
    if not r or not p:
        return {"valid":False,"score":0.0,"mcs_atoms":0,"reactant_atoms":0,"product_atoms":0}
    try:
        res = rdFMCS.FindMCS(
            [r,p],
            atomCompare=rdFMCS.AtomCompare.CompareElements,
            bondCompare=rdFMCS.BondCompare.CompareOrder,
            ringMatchesRingOnly=True,
            completeRingsOnly=True,
            timeout=10,
        )
        n = int(res.numAtoms or 0)
        score = n / max(1, min(r.GetNumAtoms(), p.GetNumAtoms()))
        return {
            "valid":True,
            "score":round(float(score),3),
            "mcs_atoms":n,
            "reactant_atoms":r.GetNumAtoms(),
            "product_atoms":p.GetNumAtoms(),
            "mcs_smarts":res.smartsString,
            "interpretation":"high scaffold conservation" if score >= .75 else "partial scaffold conservation" if score >= .45 else "low scaffold conservation",
        }
    except Exception as exc:
        return {"valid":False,"score":0.0,"error":str(exc)}
