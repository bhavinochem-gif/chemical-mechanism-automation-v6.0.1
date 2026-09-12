def rank_named_reactions(reaction_class, row, db):
    rc=(reaction_class or "").lower(); text=" ".join(str(row.get(k,"")) for k in ["Reagent","Catalyst","Reaction","Named Reaction"]).lower(); out=[]
    pairs=[
        ("suzuki", "Suzuki-Miyaura coupling", .92),
        ("buchwald", "Buchwald-Hartwig amination", .90),
        ("sonogashira", "Sonogashira coupling", .92),
        ("heck", "Heck reaction", .90),
        ("reductive amination", "Reductive amination", .90),
    ]
    for key,name,score in pairs:
        if key in rc or key in text: out.append({"name":name,"score":score})
    nr=str(row.get("Named Reaction","") or "").strip()
    if nr and nr.lower() not in {"none identified","none",""} and not any(x["name"].lower()==nr.lower() for x in out):
        out.append({"name":nr,"score":.70})
    return sorted(out,key=lambda x:x["score"],reverse=True)
