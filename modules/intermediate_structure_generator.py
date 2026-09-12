"""Conservative intermediate-structure generator for V6.4.

The engine never fabricates a full intermediate molecular graph from a text
reaction name. It returns renderable structures only when they are supplied
as validated SMILES or can be represented safely from verified endpoints.
"""
from rdkit import Chem


def _valid(s):
    try:
        return bool(s) and Chem.MolFromSmiles(str(s)) is not None
    except Exception:
        return False


def generate_intermediate_structures(reaction_class, reactant_smiles, product_smiles, mechanism):
    rc=(reaction_class or '').lower()
    nodes=[]
    if _valid(reactant_smiles):
        nodes.append({"title":"Reactant", "smiles":reactant_smiles, "status":"verified endpoint"})

    # Some transformations can safely show a substrate-derived conceptual state,
    # but the exact graph is withheld unless a validated SMILES is supplied.
    for f in (mechanism or {}).get('electron_flow',[]) or []:
        nodes.append({
            "title":str(f.get('event','Intermediate')).replace('_',' ').title(),
            "smiles":"",
            "status":"conceptual mechanistic stage",
            "description":f.get('description','')
        })

    if _valid(product_smiles):
        nodes.append({"title":"Product", "smiles":product_smiles, "status":"verified endpoint"})
    return nodes
