from __future__ import annotations

import re
from typing import Dict
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors


def sanitize_smiles_text(value: str) -> str:
    """Only repair formatting noise. Never alter chemical connectivity."""
    s = str(value or "").strip()
    s = s.replace("```smiles", "").replace("```", "").strip()
    s = s.strip('"\'` ')
    s = re.sub(r"\s+", "", s)
    return s


def validate_candidate(smiles: str) -> Dict:
    s = sanitize_smiles_text(smiles)
    if not s:
        return {"valid": False, "input": "", "canonical_smiles": "", "reason": "empty"}
    try:
        mol = Chem.MolFromSmiles(s)
    except Exception as exc:
        return {"valid": False, "input": s, "canonical_smiles": "", "reason": f"RDKit exception: {exc}"}
    if mol is None:
        return {"valid": False, "input": s, "canonical_smiles": "", "reason": "RDKit parse/sanitization failed"}
    try:
        Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
        canonical = Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
        formula = rdMolDescriptors.CalcMolFormula(mol)
        mw = rdMolDescriptors.CalcExactMolWt(mol)
        chiral = Chem.FindMolChiralCenters(mol, includeUnassigned=True, useLegacyImplementation=False)
        return {
            "valid": True,
            "input": s,
            "canonical_smiles": canonical,
            "reason": "ok",
            "atoms": mol.GetNumAtoms(),
            "bonds": mol.GetNumBonds(),
            "formula": formula,
            "exact_mw": round(float(mw), 4),
            "chiral_centers": [(int(i), str(tag)) for i, tag in chiral],
        }
    except Exception as exc:
        return {"valid": False, "input": s, "canonical_smiles": "", "reason": f"RDKit sanitization failed: {exc}"}
