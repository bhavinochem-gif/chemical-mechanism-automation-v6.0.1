from rdkit import Chem
from rdkit.Chem import Draw
def render_structure(s,size=(500,350)):
 m=Chem.MolFromSmiles(s or "");return Draw.MolToImage(m,size=size) if m else None
