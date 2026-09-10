def rank_named_reactions(rc,row,db):
 t=" ".join(str(row.get(k,"")) for k in ["Reagent","Catalyst","Reaction"]).lower();c=[]
 if "cross-coupling" in rc.lower() and ("boron" in t or "boronic" in t):c.append({"name":"Suzuki coupling","score":.88})
 if "c–n" in rc.lower() or "amine" in t:c.append({"name":"Buchwald–Hartwig amination","score":.65})
 return sorted(c,key=lambda x:x["score"],reverse=True)
