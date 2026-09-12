def verify(m):
 c={"structure_verified":m.get("reaction_center",{}).get("status")=="ok","bond_changes_present":bool(m.get("reaction_center",{}).get("bond_changes")),"reaction_classified":"Requires" not in m.get("classification",{}).get("reaction_class",""),"electron_flow_present":bool(m.get("electron_flow"))}
 return{"checks":c,"confidence":round(sum(c.values())/len(c),3)}
