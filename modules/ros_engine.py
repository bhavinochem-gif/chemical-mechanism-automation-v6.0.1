import pandas as pd
C=["Step","Starting Material","Reagent","Catalyst","Solvent","Temperature","Time","Pressure","Atmosphere","Product","Yield","Reaction","Reaction Class","Named Reaction","Confidence"]
def build_ros(a):
 r=[]
 for s in a.get("steps",[]):
  st=s.get("starting_materials",[]);p=s.get("product",{});c=s.get("conditions",{})
  r.append({"Step":s.get("step",""),"Starting Material":(st[0].get("smiles") or st[0].get("name","")) if st else "","Reagent":", ".join(s.get("reagents",[])),"Catalyst":", ".join(s.get("catalysts",[])),"Solvent":", ".join(s.get("solvents",[])),"Temperature":c.get("temperature",""),"Time":c.get("time",""),"Pressure":c.get("pressure",""),"Atmosphere":c.get("atmosphere",""),"Product":p.get("smiles") or p.get("name",""),"Yield":s.get("yield",""),"Reaction":s.get("reaction",""),"Reaction Class":s.get("reaction_class",""),"Named Reaction":s.get("named_reaction",""),"Confidence":p.get("confidence",0)})
 return pd.DataFrame(r,columns=C)
