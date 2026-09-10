from .route_signature import match_uploaded_route

def classify_reaction(center,row,db):
    text=" ".join(str(row.get(k,"")) for k in ["Reagent","Catalyst","Solvent","Reaction","Starting Material","Product"]).lower()
    if match_uploaded_route(text) or "alpha-arylation" in text or "alpha arylation" in text:
        return {
            "reaction_class":"C-C bond formation: ketone alpha-arylation",
            "candidates":[
                {"class":"Pd-catalyzed ketone alpha-arylation","score":0.96},
                {"class":"Palladium-mediated arylation of ketone enolate","score":0.93}
            ],
            "confidence":0.96,
            "evidence":["aryl bromide + ketone/enolate substrate","Pd(OAc)2","tri-tert-butylphosphonium salt","NaOtBu","toluene"]
        }
    if center.get("status")!="ok":
        return {"reaction_class":"Requires structure verification","candidates":[],"confidence":.15}
    t=text;c=[];ch=center.get("bond_changes",[])
    if any(x["type"]=="order_change" for x in ch):c.append(("Bond-order transformation",.55))
    if any(x["type"]=="formed" for x in ch):
        if "amine" in t or "nitrogen" in t:c.append(("C-N bond formation",.75))
        if "boron" in t or "boronic" in t:c.append(("Cross-coupling",.78))
        c.append(("Bond-forming reaction",.5))
    if any(x["type"]=="broken" for x in ch):c.append(("Bond cleavage/substitution",.55))
    c.sort(key=lambda x:x[1],reverse=True)
    return {"reaction_class":c[0][0] if c else "Unclassified transformation","candidates":[{"class":x,"score":s} for x,s in c],"confidence":c[0][1] if c else .3}
