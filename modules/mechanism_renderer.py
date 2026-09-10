"""Graphical chemistry mechanism rendering helpers for V6.2.1.

Important:
- Do NOT import rdkit.Chem.Draw at module import time.
- Some Streamlit Cloud Python/RDKit combinations cannot load rdMolDraw2D.
- Drawing is therefore lazy and has a Pillow fallback so the app still starts.
"""
from typing import Dict, List, Optional
from rdkit import Chem


def mol_from_smiles(smiles: str):
    if not smiles:
        return None
    try:
        return Chem.MolFromSmiles(str(smiles).strip())
    except Exception:
        return None


def _fallback_image(smiles: str, size=(760, 430), title="Validated molecular structure"):
    """Create a safe PNG-like Pillow image when RDKit drawing is unavailable."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", size, "white")
    d = ImageDraw.Draw(img)
    d.text((24, 28), title, fill="black")
    d.text((24, 72), "RDKit 2D drawing is unavailable in this Python runtime.", fill="black")
    d.text((24, 110), "Validated SMILES:", fill="black")

    # Wrap long SMILES without depending on a font package.
    smi = str(smiles)
    width = 70
    lines = [smi[i:i+width] for i in range(0, len(smi), width)] or [""]
    y = 145
    for line in lines[:8]:
        d.text((24, y), line, fill="black")
        y += 25

    d.text((24, size[1]-55),
           "For full chemical structure rendering, deploy with Python 3.12.",
           fill="black")
    return img


def render_structure(smiles: str, highlight_atoms: Optional[List[int]] = None, size=(760, 430)):
    """Render a validated SMILES.

    RDKit Draw is imported only inside this function. If rdMolDraw2D cannot
    load on the host runtime, the function returns a safe fallback image
    instead of crashing the entire Streamlit application.
    """
    mol = mol_from_smiles(smiles)
    if mol is None:
        return None

    try:
        from rdkit.Chem import Draw
        return Draw.MolToImage(
            mol,
            size=size,
            kekulize=True,
            wedgeBonds=True,
            highlightAtoms=highlight_atoms or [],
        )
    except Exception:
        return _fallback_image(smiles, size=size)


def simple_mechanism_cards() -> List[Dict[str, str]]:
    return [
        {
            "step": "1",
            "title": "Enolate formation",
            "description": "NaOtBu removes the hydrogen next to the ketone and generates the ketone enolate.",
        },
        {
            "step": "2",
            "title": "Aryl–palladium formation",
            "description": "The palladium catalyst undergoes oxidative addition into the aryl C–Br bond.",
        },
        {
            "step": "3",
            "title": "C–C bond formation",
            "description": "The ketone alpha-carbon couples with the 2,3-difluorophenyl group to form the new C–C bond.",
        },
        {
            "step": "4",
            "title": "Product formation",
            "description": "Reductive elimination releases the alpha-aryl ketone and regenerates the palladium catalyst.",
        },
    ]
