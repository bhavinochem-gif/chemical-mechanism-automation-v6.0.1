"""Structure and mechanism rendering helpers for V6.2.2.

Rendering order:
1. RDKit rdMolDraw2D PNG when that binary extension is available.
2. Pure-Pillow molecular graph renderer when rdMolDraw2D is unavailable.

This means Streamlit Cloud can still show a real molecular structure rather
than a blank/text-only placeholder.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from rdkit import Chem
from modules.pillow_molecule_renderer import render_molecule_pillow


def mol_from_smiles(smiles: str):
    if not smiles:
        return None
    try:
        return Chem.MolFromSmiles(str(smiles).strip())
    except Exception:
        return None


def _rdkit_png(smiles: str, highlight_atoms=None, size=(760, 430)):
    """Use rdMolDraw2D directly; never import rdkit.Chem.Draw."""
    mol = mol_from_smiles(smiles)
    if mol is None:
        return None
    from io import BytesIO
    from PIL import Image
    from rdkit.Chem.Draw import rdMolDraw2D
    try:
        from rdkit.Chem import rdDepictor
        rdDepictor.Compute2DCoords(mol)
    except Exception:
        pass
    drawer = rdMolDraw2D.MolDraw2DCairo(int(size[0]), int(size[1]))
    opts = drawer.drawOptions()
    opts.addStereoAnnotation = True
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol, highlightAtoms=list(highlight_atoms or []))
    drawer.FinishDrawing()
    return Image.open(BytesIO(drawer.GetDrawingText())).convert("RGB")


def render_structure(smiles: str, highlight_atoms: Optional[List[int]] = None, size=(760, 430)):
    """Render a molecular structure as a PIL image without crashing the app."""
    if mol_from_smiles(smiles) is None:
        return None
    try:
        return _rdkit_png(smiles, highlight_atoms=highlight_atoms, size=size)
    except Exception:
        # Real molecular graph fallback—not a text-only error card.
        return render_molecule_pillow(smiles, size=size, highlight_atoms=highlight_atoms)


def drawing_backend() -> str:
    """Return the drawing backend available on this runtime."""
    try:
        from rdkit.Chem.Draw import rdMolDraw2D  # noqa: F401
        return "RDKit rdMolDraw2D"
    except Exception:
        return "Pure-Pillow molecular graph fallback"


def simple_mechanism_cards() -> List[Dict[str, str]]:
    return [
        {"step":"1", "title":"Enolate formation", "description":"NaOtBu removes the hydrogen next to the ketone and generates the ketone enolate."},
        {"step":"2", "title":"Aryl–palladium formation", "description":"The palladium catalyst undergoes oxidative addition into the aryl C–Br bond."},
        {"step":"3", "title":"C–C bond formation", "description":"The ketone alpha-carbon couples with the 2,3-difluorophenyl group to form the new C–C bond."},
        {"step":"4", "title":"Product formation", "description":"Reductive elimination releases the alpha-aryl ketone and regenerates the palladium catalyst."},
    ]
