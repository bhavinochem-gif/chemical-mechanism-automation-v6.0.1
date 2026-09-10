from rdkit import Chem
from .atom_mapper import map_atoms

def _bonds(m):
    out={}
    for b in m.GetBonds():
        a,c=b.GetBeginAtomIdx(),b.GetEndAtomIdx()
        out[tuple(sorted((a,c)))]=b.GetBondTypeAsDouble()
    return out

def analyze_reaction_center(rs,ps):
    r,p=Chem.MolFromSmiles(rs or ""),Chem.MolFromSmiles(ps or "")
    if not r or not p:return {"status":"needs_structure_verification","bond_changes":[],"confidence":0.0}
    mp=map_atoms(rs,ps); mapping=mp.get("mapping",{}); inv={v:k for k,v in mapping.items()}
    rb,pb=_bonds(r),_bonds(p); changes=[]
    for (a,b),order in rb.items():
        if a in mapping and b in mapping:
            k=tuple(sorted((mapping[a],mapping[b])))
            if k not in pb: changes.append({"type":"broken","reactant_atoms":[a,b],"product_atoms":[mapping[a],mapping[b]],"order":order})
            elif pb[k]!=order: changes.append({"type":"order_change","reactant_atoms":[a,b],"product_atoms":[mapping[a],mapping[b]],"from":order,"to":pb[k]})
    for (a,b),order in pb.items():
        if a in inv and b in inv:
            k=tuple(sorted((inv[a],inv[b])))
            if k not in rb: changes.append({"type":"formed","reactant_atoms":[inv[a],inv[b]],"product_atoms":[a,b],"order":order})
        else:
            changes.append({"type":"formed_or_new_atom_bond","product_atoms":[a,b],"order":order})
    return {"status":"ok","bond_changes":changes,"atom_mapping":mp,"confidence":round(min(.995,.45+.55*mp.get("confidence",0)),3)}
