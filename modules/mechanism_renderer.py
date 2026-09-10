"""Graphical chemistry mechanism rendering helpers for V6.2.1."""
from typing import Any, Dict, List, Optional
from rdkit import Chem
from rdkit.Chem import Draw


def mol_from_smiles(smiles: str):
    if not smiles:
        return None
    try:
        return Chem.MolFromSmiles(smiles)
    except Exception:
        return None


def render_structure(smiles: str, highlight_atoms: Optional[List[int]] = None, size=(760, 430)):
    mol = mol_from_smiles(smiles)
    if mol is None:
        return None
    return Draw.MolToImage(mol, size=size, kekulize=True, wedgeBonds=True,
                           highlightAtoms=highlight_atoms or [])


def simple_mechanism_cards() -> List[Dict[str, str]]:
    return [
        {"step": "1", "title": "Enolate formation",
         "description": "NaOtBu removes the hydrogen next to the ketone and generates the ketone enolate."},
        {"step": "2", "title": "Aryl–palladium formation",
         "description": "The palladium catalyst undergoes oxidative addition into the aryl C–Br bond."},
        {"step": "3", "title": "C–C bond formation",
         "description": "The ketone alpha-carbon couples with the 2,3-difluorophenyl group to form the new C–C bond."},
        {"step": "4", "title": "Product formation",
         "description": "Reductive elimination releases the alpha-aryl ketone and regenerates the palladium catalyst."},
    ]
