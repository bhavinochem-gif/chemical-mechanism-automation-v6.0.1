from .electron_flow_engine import infer_electron_flow
from .intermediate_engine import generate_intermediates
from .stereochemistry_engine import analyze_stereochemistry
from .plausibility_engine import assess
from .mechanism_verifier import verify
from .named_reaction_engine import rank_named_reactions
from .mechanism_rules import RULES
class MechanismEngine:
 def __init__(self,db):self.db=db
 def analyze_step(self,row,center,classification):
  rs=str(row.get("Starting Material","") or "");ps=str(row.get("Product","") or "");rc=classification.get("reaction_class","");flows=infer_electron_flow(rc,center.get("bond_changes",[]))
  m={"step":row.get("Step"),"reaction":row.get("Reaction",""),"reaction_center":center,"classification":classification,"named_reaction_candidates":rank_named_reactions(rc,row,self.db),"mechanistic_rules":RULES.get(rc,["Structure-specific mechanism review required."]),"electron_flow":flows,"intermediates":generate_intermediates(rc,flows,row),"stereochemistry":analyze_stereochemistry(rs,ps),"plausibility":assess(center,classification,row)}
  m["verification"]=verify(m);m["confidence"]=round(.35*center.get("confidence",0)+.2*classification.get("confidence",0)+.2*m["plausibility"]["score"]+.25*m["verification"]["confidence"],3);return m
