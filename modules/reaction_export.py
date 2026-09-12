from __future__ import annotations

def reaction_to_rxn_block(step) -> str:
    try:
        from rdkit import Chem
        from rdkit.Chem import rdChemReactions
        rxn = rdChemReactions.ChemicalReaction()
        for smi in step.reactants:
            m = Chem.MolFromSmiles(smi)
            if m is not None:
                rxn.AddReactantTemplate(m)
        for smi in step.products:
            m = Chem.MolFromSmiles(smi)
            if m is not None:
                rxn.AddProductTemplate(m)
        if not rxn.GetNumReactantTemplates() or not rxn.GetNumProductTemplates():
            return ""
        return rdChemReactions.ReactionToRxnBlock(rxn)
    except Exception:
        return ""
