from rdkit import Chem
def analyze_stereochemistry(rs,ps):
 def f(s):
  m=Chem.MolFromSmiles(s or "");return{"valid":bool(m),"centers":[{"atom":a,"label":b} for a,b in Chem.FindMolChiralCenters(m,includeUnassigned=True,includeCIP=True)]} if m else{"valid":False,"centers":[]}
 return{"reactant":f(rs),"product":f(ps)}
