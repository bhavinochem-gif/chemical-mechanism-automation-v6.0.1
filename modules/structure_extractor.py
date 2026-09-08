from rdkit import Chem
def parse_smiles(s):
 m=Chem.MolFromSmiles(s or "");return(m,{"valid":True,"canonical_smiles":Chem.MolToSmiles(m)}) if m else(None,{"valid":False})
