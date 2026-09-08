from rdkit import Chem
def validate_smiles(s):
 if not s:return{"valid":False,"confidence":0}
 try:m=Chem.MolFromSmiles(s);Chem.SanitizeMol(m);return{"valid":True,"canonical_smiles":Chem.MolToSmiles(m),"confidence":.95}
 except Exception as e:return{"valid":False,"reason":str(e),"confidence":0}
