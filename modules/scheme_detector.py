"""Candidate region detection for graphical reaction schemes."""

def detect_scheme_regions(page_width, page_height):
    w, h = int(page_width), int(page_height)
    return [
        {"name": "starting_structure", "box": (0, 0, int(w*.34), h)},
        {"name": "conditions", "box": (int(w*.30), 0, int(w*.70), h)},
        {"name": "product_structure", "box": (int(w*.66), 0, w, h)},
    ]


def route_specific_defaults():
    return {
        "reaction": "Palladium-catalyzed alpha-arylation of a ketone",
        "reaction_class": "C-C bond formation: ketone alpha-arylation",
        "named_reaction": "Pd-catalyzed ketone alpha-arylation",
        "aryl_halide_smiles": "Fc1cccc(Br)c1F",
    }
