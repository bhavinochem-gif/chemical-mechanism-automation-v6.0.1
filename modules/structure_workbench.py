import pandas as pd
from .chemical_graph_engine import graph_summary

def structures_to_table(structures):
    rows=[]
    for s in structures:
        v=s.get("validation",{})
        rows.append({"Role":s.get("role",""),"Name":s.get("name",""),"SMILES":s.get("smiles",""),"Valid":v.get("valid",False),"Confidence":s.get("confidence",0)})
    return pd.DataFrame(rows)

def validate_rows(df):
    out=[]
    for r in df.to_dict("records"):
        g=graph_summary(str(r.get("SMILES","") or "").strip())
        r["Valid"]=g.get("valid",False)
        r["Canonical SMILES"]=g.get("smiles","") if g.get("valid") else ""
        r["Graph atoms"]=g.get("atoms",0)
        r["Graph bonds"]=g.get("bonds",0)
        out.append(r)
    return pd.DataFrame(out)
