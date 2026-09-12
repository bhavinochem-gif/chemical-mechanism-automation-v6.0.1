"""Structure rendering and general mechanism-card helpers for V6.4."""
from __future__ import annotations
from typing import Dict, List, Optional
from rdkit import Chem
from modules.pillow_molecule_renderer import render_molecule_pillow

def mol_from_smiles(smiles: str):
    if not smiles: return None
    try: return Chem.MolFromSmiles(str(smiles).strip())
    except Exception: return None

def _rdkit_png(smiles: str, highlight_atoms=None, size=(760,430)):
    mol = mol_from_smiles(smiles)
    if mol is None: return None
    from io import BytesIO
    from PIL import Image
    from rdkit.Chem.Draw import rdMolDraw2D
    try:
        from rdkit.Chem import rdDepictor
        rdDepictor.Compute2DCoords(mol)
    except Exception:
        pass
    drawer = rdMolDraw2D.MolDraw2DCairo(int(size[0]), int(size[1]))
    drawer.drawOptions().addStereoAnnotation = True
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol, highlightAtoms=list(highlight_atoms or []))
    drawer.FinishDrawing()
    return Image.open(BytesIO(drawer.GetDrawingText())).convert("RGB")

def render_structure(smiles: str, highlight_atoms: Optional[List[int]]=None, size=(760,430)):
    if mol_from_smiles(smiles) is None: return None
    try: return _rdkit_png(smiles, highlight_atoms, size)
    except Exception: return render_molecule_pillow(smiles, size=size, highlight_atoms=highlight_atoms)

def drawing_backend():
    try:
        from rdkit.Chem.Draw import rdMolDraw2D  # noqa
        return "RDKit rdMolDraw2D"
    except Exception:
        return "Pure-Pillow molecular graph fallback"

def cards_from_mechanism(mechanism: Dict) -> List[Dict[str,str]]:
    cards=[]
    flows=mechanism.get("electron_flow",[]) or []
    for i, f in enumerate(flows,1):
        cards.append({"step":str(f.get("step",i)), "title":str(f.get("event",f.get("type","Mechanistic step"))).replace("_"," ").title(), "description":f.get("description", f.get("purpose", "Mechanistic event inferred from current reaction evidence."))})
    if not cards:
        cards=[{"step":"1", "title":"Mechanism pending verification", "description":"Validate reactant and product structures before assigning a detailed mechanism."}]
    return cards
