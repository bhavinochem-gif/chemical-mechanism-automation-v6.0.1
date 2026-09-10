from rdkit import Chem
from .atom_mapper import map_atoms
def _b(m):return{(min(x.GetBeginAtomIdx(),x.GetEndAtomIdx()),max(x.GetBeginAtomIdx(),x.GetEndAtomIdx())):x.GetBondTypeAsDouble() for x in m.GetBonds()}
def analyze_reaction_center(rs,ps):
 r,p=Chem.MolFromSmiles(rs or ""),Chem.MolFromSmiles(ps or "")
 if not r or not p:return{"status":"needs_structure_verification","bond_changes":[],"confidence":0}
 mp=map_atoms(rs,ps);inv=mp["mapping"];rb,pb=_b(r),_b(p);ch=[]
 for (a,b),o in rb.items():
  if a in inv and b in inv:
   k=tuple(sorted((inv[a],inv[b])))
   if k not in pb:ch.append({"type":"broken","reactant_atoms":[a,b],"product_atoms":[inv[a],inv[b]],"order":o})
   elif pb[k]!=o:ch.append({"type":"order_change","reactant_atoms":[a,b],"product_atoms":[inv[a],inv[b]],"from":o,"to":pb[k]})
 rv=set(inv.values())
 for (a,b),o in pb.items():
  if a not in rv or b not in rv:ch.append({"type":"formed","product_atoms":[a,b],"order":o})
 return{"status":"ok","bond_changes":ch,"atom_mapping":mp,"confidence":round(min(.99,.45+.55*mp["confidence"]),3)}
