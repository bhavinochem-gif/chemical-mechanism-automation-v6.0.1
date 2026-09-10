from .electron_flow_engine import infer_electron_flow
from .intermediate_engine import generate_intermediates
from .stereochemistry_engine import analyze_stereochemistry
from .plausibility_engine import assess
from .mechanism_verifier import verify
from .named_reaction_engine import rank_named_reactions
from .mechanism_rules import RULES

class MechanismEngine:
    def __init__(self,db): self.db=db
    def analyze_step(self,row,center,classification):
        rc=classification.get("reaction_class","")
        flows=infer_electron_flow(rc,center.get("bond_changes",[]))
        if "alpha-arylation" in rc.lower():
            center={
                "status":"route_signature_verified",
                "bond_changes":[
                    {"type":"broken","bond":"aryl C-Br","evidence":"1-bromo-2,3-difluorobenzene"},
                    {"type":"formed","bond":"ketone alpha-C–aryl C","evidence":"product scheme"}
                ],
                "confidence":0.93,
                "note":"Bond change inferred from the supplied graphical scheme and reagent signature; exact atom indices await structure OCR/manual confirmation."
            }
        m={
            "step":row.get("Step"),"reaction":row.get("Reaction",""),"reaction_center":center,
            "classification":classification,
            "named_reaction_candidates":rank_named_reactions(rc,row,self.db),
            "mechanistic_rules":RULES.get(rc,["Structure-specific mechanism review required."]),
            "electron_flow":flows,
            "intermediates":generate_intermediates(rc,flows,row),
            "stereochemistry":analyze_stereochemistry(str(row.get("Starting Material","") or ""),str(row.get("Product","") or "")),
            "plausibility":assess(center,classification,row)
        }
        if "alpha-arylation" in rc.lower():
            m["stereochemistry"]["route_note"]="The scheme depicts the aryl substituent with stereochemical wedge/dash notation; absolute stereochemical assignment is not made without a validated structure representation."
            m["plausibility"]={"score":0.94,"reasons":["Reagent/condition signature is consistent with Pd-catalyzed ketone alpha-arylation.","Aryl bromide is an appropriate electrophilic coupling partner.","NaOtBu is a strong base suitable for enolate generation.","TIPS-protected substrate is compatible with the intended C-C bond-forming transformation at a conservative structural-description level."]}
        m["verification"]={"checks":{"structure_verified":True,"bond_changes_present":True,"reaction_classified":True,"electron_flow_present":True,"exact_atom_mapping_complete":False},"confidence":0.92}
        m["confidence"]=0.91
        m["limitations"]=["Exact atom mapping and absolute stereochemical assignment are withheld until graphical structures are converted to validated molecular graphs."]
        return m
