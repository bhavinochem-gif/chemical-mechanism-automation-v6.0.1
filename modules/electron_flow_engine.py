def infer_electron_flow(reaction_class, changes):
    rc = (reaction_class or "").lower()
    templates = {
        "suzuki": [
            {"step":1,"event":"oxidative addition","description":"Pd inserts into the aryl/vinyl leaving-group bond."},
            {"step":2,"event":"transmetalation","description":"The organoboron partner transfers its carbon group to palladium."},
            {"step":3,"event":"reductive elimination","description":"The two carbon groups couple and Pd(0) is regenerated."},
        ],
        "buchwald": [
            {"step":1,"event":"oxidative addition","description":"Pd activates the aryl/vinyl leaving-group bond."},
            {"step":2,"event":"amine coordination/deprotonation","description":"The amine enters the Pd coordination sphere and is deprotonated."},
            {"step":3,"event":"reductive elimination","description":"C-N bond formation releases the coupled product."},
        ],
        "amide": [
            {"step":1,"event":"carboxyl activation","description":"The carboxyl component is activated by the coupling reagent."},
            {"step":2,"event":"nucleophilic attack","description":"The amine attacks the activated acyl carbon."},
            {"step":3,"event":"collapse/proton transfer","description":"The tetrahedral intermediate collapses to the amide product."},
        ],
        "reductive amination": [
            {"step":1,"event":"imine/iminium formation","description":"The amine and carbonyl compound condense."},
            {"step":2,"event":"hydride transfer","description":"The reducing reagent delivers hydride to the imine/iminium carbon."},
            {"step":3,"event":"proton transfer","description":"Protonation/deprotonation gives the amine product."},
        ],
        "hydrogenation": [
            {"step":1,"event":"surface coordination","description":"The unsaturated substrate and hydrogen interact with the catalyst."},
            {"step":2,"event":"hydrogen addition","description":"Hydrogen is delivered across the reducible unsaturation."},
            {"step":3,"event":"product release","description":"The reduced product leaves the catalyst surface."},
        ],
        "alpha-arylation": [
            {"step":1,"event":"enolate formation","description":"Base generates the ketone enolate."},
            {"step":2,"event":"oxidative addition","description":"Pd activates the aryl leaving-group bond."},
            {"step":3,"event":"Pd-enolate formation","description":"The enolate enters the Pd catalytic manifold."},
            {"step":4,"event":"reductive elimination","description":"The new alpha-C–aryl C-C bond forms and Pd(0) is regenerated."},
        ],
    }
    for key, flow in templates.items():
        if key in rc:
            return flow
    out = []
    for i, c in enumerate(changes or [], 1):
        typ = c.get("type", "change")
        desc = {
            "formed":"A new bond is formed at the mapped reaction center.",
            "broken":"A bond is cleaved at the mapped reaction center.",
            "order_change":"A bond order changes at the mapped reaction center.",
            "formed_or_new_atom_bond":"A product bond involving a new/unmapped atom is formed.",
        }.get(typ, "A mapped structural change occurs.")
        out.append({"step":i, "event":typ, "description":desc, "evidence":c})
    return out
