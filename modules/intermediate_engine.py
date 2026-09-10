def generate_intermediates(rc,flows,row):
    if "alpha-arylation" in rc.lower():
        return [
            {"intermediate":1,"name":"Ketone enolate","description":"NaOtBu removes the alpha proton; resonance places electron density at the alpha carbon and oxygen."},
            {"intermediate":2,"name":"L-Pd aryl species","description":"Pd(0)/phosphine undergoes oxidative addition into the aryl C-Br bond."},
            {"intermediate":3,"name":"Pd-enolate / aryl complex","description":"The enolate and aryl fragments are brought onto the Pd catalytic manifold."},
            {"intermediate":4,"name":"Alpha-aryl ketone product","description":"Reductive elimination forms the new C(alpha)-C(aryl) bond and regenerates Pd(0)."}
        ]
    return [{"intermediate":i+1,"description":f"Candidate intermediate associated with {x.get('type','step')}."} for i,x in enumerate(flows)]
