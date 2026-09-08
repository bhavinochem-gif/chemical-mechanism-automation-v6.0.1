def classify_reaction(center,row,db):
 if center.get("status")!="ok":return{"reaction_class":"Requires structure verification","candidates":[],"confidence":.15}
 t=" ".join(str(row.get(k,"")) for k in ["Reagent","Catalyst","Solvent","Reaction"]).lower();c=[];ch=center.get("bond_changes",[])
 if any(x["type"]=="order_change" for x in ch):c.append(("Bond-order transformation",.55))
 if any(x["type"]=="formed" for x in ch):
  if "amine" in t or "nitrogen" in t:c.append(("C–N bond formation",.75))
  if "boron" in t or "boronic" in t:c.append(("Cross-coupling",.78))
  c.append(("Bond-forming reaction",.5))
 if any(x["type"]=="broken" for x in ch):c.append(("Bond cleavage/substitution",.55))
 c.sort(key=lambda x:x[1],reverse=True)
 return{"reaction_class":c[0][0] if c else "Unclassified transformation","candidates":[{"class":x,"score":s} for x,s in c],"confidence":c[0][1] if c else .3}
