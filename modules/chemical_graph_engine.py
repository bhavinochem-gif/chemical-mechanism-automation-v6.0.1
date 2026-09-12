from rdkit import Chem
from rdkit.Chem import rdFMCS

def mol_from_smiles(smiles):
    return Chem.MolFromSmiles(smiles or "")

def graph_summary(smiles):
    m=mol_from_smiles(smiles)
    if not m:return {"valid":False,"smiles":smiles or ""}
    return {"valid":True,"smiles":Chem.MolToSmiles(m,isomericSmiles=True),"atoms":m.GetNumAtoms(),"bonds":m.GetNumBonds(),"formula":_formula(m)}

def _formula(m):
    from collections import Counter
    c=Counter(a.GetSymbol() for a in m.GetAtoms())
    return " ".join(f"{k}{v if v>1 else ''}" for k,v in sorted(c.items()))

def mcs_map(reactant_smiles, product_smiles):
    r,p=mol_from_smiles(reactant_smiles),mol_from_smiles(product_smiles)
    if not r or not p:return {"status":"invalid_structure","mapping":{},"confidence":0.0}
    res=rdFMCS.FindMCS([r,p],atomCompare=rdFMCS.AtomCompare.CompareElements,bondCompare=rdFMCS.BondCompare.CompareOrder,ringMatchesRingOnly=True,completeRingsOnly=True,timeout=10)
    if res.canceled or not res.smartsString:return {"status":"mcs_failed","mapping":{},"confidence":0.0}
    q=Chem.MolFromSmarts(res.smartsString)
    mr=r.GetSubstructMatch(q); mp=p.GetSubstructMatch(q)
    mapping={int(a):int(b) for a,b in zip(mr,mp)}
    conf=len(mapping)/max(1,min(r.GetNumAtoms(),p.GetNumAtoms()))
    return {"status":"ok","mapping":mapping,"mcs_atoms":len(mapping),"confidence":round(conf,3),"mcs_smarts":res.smartsString}
