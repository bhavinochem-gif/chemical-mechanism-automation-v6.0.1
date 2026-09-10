from rdkit import Chem
def normalize_smiles(s):
 m=Chem.MolFromSmiles(s or "");return Chem.MolToSmiles(m) if m else ""
