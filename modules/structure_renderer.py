"""Safe molecular structure renderer for Streamlit Cloud."""
from rdkit import Chem


def render_smiles(smiles: str, size=(700, 420)):
    if not smiles:
        return None
    try:
        mol = Chem.MolFromSmiles(str(smiles).strip())
    except Exception:
        mol = None
    if mol is None:
        return None

    try:
        from rdkit.Chem import Draw
        return Draw.MolToImage(mol, size=size, wedgeBonds=True)
    except Exception:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", size, "white")
        d = ImageDraw.Draw(img)
        d.text((20, 25), "Validated structure", fill="black")
        d.text((20, 65), "2D renderer unavailable on this Python runtime.", fill="black")
        d.text((20, 105), "SMILES:", fill="black")
        smi = str(smiles)
        y = 135
        for i in range(0, len(smi), 68):
            d.text((20, y), smi[i:i+68], fill="black")
            y += 24
        d.text((20, size[1]-45), "Use Python 3.12 for RDKit drawing.", fill="black")
        return img


# Backward-compatible aliases used by older modules.
def render_structure(smiles: str, size=(700, 420)):
    return render_smiles(smiles, size=size)


def smiles_to_image(smiles: str, size=(700, 420)):
    return render_smiles(smiles, size=size)
