def rules_for(reaction_class):
    rc = (reaction_class or "").lower()
    templates = [
        ("suzuki", ["Oxidative addition to Pd.", "Base-assisted organoboron activation/transmetalation.", "Reductive elimination forms the new C-C bond."]),
        ("buchwald", ["Oxidative addition to Pd.", "Amine coordination and deprotonation.", "Reductive elimination forms the C-N bond."]),
        ("amide", ["Activate the carboxyl component.", "Amine nucleophilic attack at the acyl carbon.", "Collapse/proton transfer affords the amide."]),
        ("reductive amination", ["Carbonyl/amine condensation gives an imine or iminium species.", "Hydride transfer reduces the C=N unit.", "Proton transfer affords the amine."]),
        ("hydrogenation", ["Substrate and H2 interact with the catalyst.", "Hydrogen is added across the reducible bond.", "Reduced product is released."]),
        ("alpha-arylation", ["Base generates an enolate.", "Pd activates the aryl leaving-group bond.", "Enolate enters the Pd cycle.", "Reductive elimination forms the alpha-aryl C-C bond."]),
    ]
    for key, rules in templates:
        if key in rc:
            return rules
    return ["Use the validated bond changes and functional groups to construct a structure-specific mechanism."]

RULES = {}
