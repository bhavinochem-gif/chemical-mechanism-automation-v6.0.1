"""Direct molecular graph utilities for V6.6.

Unlike OCSR, this module starts from an explicit molecule supplied by a drawing
editor, SMILES, Molfile or RXN file. RDKit sanitization remains a graph-quality
check, not an image-recognition step.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors
    RDKIT_OK = True
except Exception:
    Chem = None
    Descriptors = None
    rdMolDescriptors = None
    RDKIT_OK = False


def mol_from_any(value: Any):
    if not RDKIT_OK or value is None:
        return None
    if hasattr(value, "GetAtoms") and hasattr(value, "GetBonds"):
        try:
            return Chem.Mol(value)
        except Exception:
            return None
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8", errors="ignore")
        except Exception:
            return None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None

    # Molfile first when it looks like one.
    if "M  END" in text or "V2000" in text or "V3000" in text:
        try:
            m = Chem.MolFromMolBlock(text, sanitize=True, removeHs=False)
            if m is not None:
                return m
        except Exception:
            pass

    try:
        return Chem.MolFromSmiles(text)
    except Exception:
        return None


def canonical_smiles(value: Any, isomeric: bool = True) -> str:
    mol = mol_from_any(value)
    if mol is None:
        return ""
    try:
        Chem.SanitizeMol(mol)
        return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=isomeric)
    except Exception:
        return ""


def validate_structure(value: Any) -> Dict[str, Any]:
    if not RDKIT_OK:
        return {"valid": False, "error": "RDKit is unavailable."}
    mol = mol_from_any(value)
    if mol is None:
        return {"valid": False, "error": "No valid molecular graph could be created."}
    try:
        Chem.SanitizeMol(mol)
        smi = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
        formula = rdMolDescriptors.CalcMolFormula(mol)
        mw = float(Descriptors.MolWt(mol))
        return {
            "valid": True,
            "canonical_smiles": smi,
            "formula": formula,
            "mw": mw,
            "atoms": int(mol.GetNumAtoms()),
            "bonds": int(mol.GetNumBonds()),
            "formal_charge": int(sum(a.GetFormalCharge() for a in mol.GetAtoms())),
        }
    except Exception as exc:
        return {"valid": False, "error": str(exc)}


def molecular_graph(value: Any) -> Dict[str, Any]:
    mol = mol_from_any(value)
    if mol is None:
        return {"valid": False, "atoms": [], "bonds": []}
    try:
        Chem.SanitizeMol(mol)
    except Exception as exc:
        return {"valid": False, "error": str(exc), "atoms": [], "bonds": []}

    atoms: List[Dict[str, Any]] = []
    for atom in mol.GetAtoms():
        atoms.append({
            "index": int(atom.GetIdx()),
            "element": atom.GetSymbol(),
            "atomic_number": int(atom.GetAtomicNum()),
            "formal_charge": int(atom.GetFormalCharge()),
            "is_aromatic": bool(atom.GetIsAromatic()),
            "chiral_tag": str(atom.GetChiralTag()),
            "hybridization": str(atom.GetHybridization()),
            "explicit_h": int(atom.GetNumExplicitHs()),
            "implicit_h": int(atom.GetNumImplicitHs()),
        })

    bonds: List[Dict[str, Any]] = []
    for bond in mol.GetBonds():
        bonds.append({
            "index": int(bond.GetIdx()),
            "begin": int(bond.GetBeginAtomIdx()),
            "end": int(bond.GetEndAtomIdx()),
            "bond_type": str(bond.GetBondType()),
            "order": float(bond.GetBondTypeAsDouble()),
            "is_aromatic": bool(bond.GetIsAromatic()),
            "stereo": str(bond.GetStereo()),
        })

    return {
        "valid": True,
        "smiles": Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True),
        "atoms": atoms,
        "bonds": bonds,
    }


def combine_smiles(smiles_list: List[str]) -> str:
    cleaned = [canonical_smiles(x) for x in smiles_list if str(x or "").strip()]
    return ".".join([x for x in cleaned if x])


def molblock(value: Any) -> str:
    mol = mol_from_any(value)
    if mol is None:
        return ""
    try:
        return Chem.MolToMolBlock(mol)
    except Exception:
        return ""
