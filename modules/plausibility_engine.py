def assess(center,classification,row):
 s=.2;r=[]
 if center.get("status")=="ok":s+=.4;r.append("Structures passed reaction-center analysis.")
 if center.get("bond_changes"):s+=.15;r.append("Bond changes detected.")
 if "Requires" not in classification.get("reaction_class",""):s+=.15;r.append("Reaction class assigned.")
 if row.get("Reagent") or row.get("Reaction"):s+=.1;r.append("Operational context available.")
 return{"score":round(min(s,.99),3),"reasons":r}
