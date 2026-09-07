COLS=["Step","Starting material","Reagent","Solvent","Temperature","Time","Product","Yield","Reaction"]
KEY={"Starting material":"starting_material","Reagent":"reagent","Solvent":"solvent","Temperature":"temperature","Time":"time","Product":"product","Yield":"yield","Reaction":"reaction"}
def build_ros(a):
    out=[]
    for i,s in enumerate(a.get("steps",[]),1):
        r={c:s.get(KEY[c],"") for c in COLS}; r["Step"]=s.get("step",i); out.append(r)
    return out or [{c:(1 if c=="Step" else "") for c in COLS}]
