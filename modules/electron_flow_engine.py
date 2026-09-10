def infer_electron_flow(rc,changes):
    if "alpha-arylation" in rc.lower():
        return [
            {"step":1,"arrow":"Base abstracts the alpha-H next to the ketone","from":"alpha C-H bond","to":"tert-butoxide oxygen","purpose":"generate the ketone enolate"},
            {"step":2,"arrow":"Enolate pi electrons coordinate/capture the Pd electrophilic center","from":"enolate alpha-carbon / enolate electron density","to":"Pd center","purpose":"form a Pd-enolate species"},
            {"step":3,"arrow":"C-C bond formation by reductive elimination","from":"Pd-C(enolate) bond","to":"aryl carbon bearing the leaving group","purpose":"form the alpha-aryl C-C bond and release Pd(0)"},
            {"step":4,"arrow":"Catalytic cycle regeneration","from":"Pd(0)","to":"oxidative-addition cycle","purpose":"regenerate active catalyst"}
        ]
    out=[]
    for c in changes:
        out.append({"type":"bond_formation" if c["type"]=="formed" else "bond_cleavage" if c["type"]=="broken" else "bond_order_change","source":"reaction-center site","destination":"electrophilic atom/leaving group","evidence":c})
    return out
