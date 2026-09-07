class MechanismEngine:
 def __init__(self,db): self.db=db
 def analyze(self,ros,analysis=None):
  out=[]
  for r in ros:
   t=(str(r.get("Reaction",""))+" "+str(r.get("Reagent",""))).lower(); named="None identified"; cls="Requires structure verification"
   for x in self.db.get("named_reactions",{}).get("reactions",[]):
    if x.get("name","").lower() in t:named=x["name"];break
   for x in self.db.get("reaction_classes",{}).get("classes",[]):
    if any(k.lower() in t for k in x.get("keywords",[])):cls=x["name"];break
   out.append({"step":r["Step"],"reaction":r.get("Reaction","Unspecified"),"reaction_class":cls,"named_reaction":named,"mechanism":"Candidate only; validate structures and atom mapping.","electron_flow":"Validate electron-rich/electron-poor sites and bond changes.","confidence":0.55 if cls!="Requires structure verification" else 0.25})
  return out
