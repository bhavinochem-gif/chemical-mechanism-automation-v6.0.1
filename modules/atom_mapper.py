from rdkit import Chem
def _sig(a):return(a.GetAtomicNum(),a.GetFormalCharge(),a.GetIsAromatic(),a.GetTotalDegree())
def map_atoms(rs,ps):
 r,p=Chem.MolFromSmiles(rs or ""),Chem.MolFromSmiles(ps or "")
 if not r or not p:return{"status":"needs_structure_verification","mapping":{},"confidence":0}
 u=set(range(p.GetNumAtoms()));m={}
 for a in r.GetAtoms():
  c=[i for i in u if _sig(a)==_sig(p.GetAtomWithIdx(i))]
  if len(c)==1:m[a.GetIdx()]=c[0];u.remove(c[0])
 return{"status":"ok","mapping":m,"unmapped_reactant_atoms":sorted(set(range(r.GetNumAtoms()))-set(m)),"unmapped_product_atoms":sorted(u),"confidence":round(len(m)/max(1,r.GetNumAtoms()),3)}
