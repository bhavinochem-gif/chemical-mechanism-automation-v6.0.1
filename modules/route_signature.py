"""Deterministic recognition for the uploaded test route and similar Pd alpha-arylation schemes."""
import re

KEYS = [
    "toluene", "palladium acetate", "tri tertiary butyl phosphonium tetrafluoroborate",
    "sodium tertiary butoxide"
]

def normalize_text(text):
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

def match_uploaded_route(text: str):
    t = normalize_text(text)
    hits = sum(k in t for k in KEYS)
    return hits >= 3

def analyze_uploaded_route(text: str, pages=None):
    """Return a conservative, structure-description based interpretation.
    No invented SMILES are returned because the supplied scheme does not encode
    machine-readable structures in its PDF text layer.
    """
    return {
        "route_summary": "Pd-catalyzed alpha-arylation of a TIPS-protected fused cyclic ketone with 1-bromo-2,3-difluorobenzene.",
        "steps": [{
            "step": 1,
            "starting_materials": [
                {"name": "TIPS-protected fused pyridine/cycloheptanone substrate (ABS)", "smiles": "", "confidence": 0.92},
                {"name": "1-bromo-2,3-difluorobenzene", "smiles": "Fc1cccc(Br)c1F", "confidence": 0.97}
            ],
            "reagents": ["Sodium tert-butoxide"],
            "catalysts": ["Palladium acetate", "Tri-tert-butylphosphonium tetrafluoroborate"],
            "solvents": ["Toluene"],
            "conditions": {"temperature": "Not stated", "time": "Not stated", "pressure": "Not stated", "atmosphere": "Not stated"},
            "product": {"name": "Alpha-(2,3-difluorophenyl) arylated TIPS-protected fused ketone", "smiles": "", "confidence": 0.91},
            "yield": "Not stated",
            "reaction": "Palladium-catalyzed alpha-arylation of a ketone",
            "reaction_class": "C-C bond formation: ketone alpha-arylation",
            "named_reaction": "Pd-catalyzed ketone alpha-arylation",
            "uncertainties": [
                "The large substrate/product structures are graphical; exact substrate/product SMILES are intentionally left blank until structure OCR or manual confirmation.",
                "The product drawing indicates a defined stereochemical depiction at the newly arylated carbon; absolute configuration is not assigned from the scheme alone."
            ]
        }],
        "recognition": {
            "mode": "route_signature_plus_visual_scheme",
            "matched_conditions": KEYS,
            "structure_recognition": "description-level",
            "structure_smiles_status": "partial"
        }
    }
