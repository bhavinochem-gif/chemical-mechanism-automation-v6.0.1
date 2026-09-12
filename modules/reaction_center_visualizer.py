"""Reaction-center image helper for V6.4."""
from .mechanism_renderer import render_structure


def reaction_center_images(reactant_smiles, product_smiles, center):
    ra=set(); pa=set()
    for ch in (center or {}).get('bond_changes',[]) or []:
        ra.update(ch.get('reactant_atoms',[]) or [])
        pa.update(ch.get('product_atoms',[]) or [])
    return {
        'reactant': render_structure(reactant_smiles,sorted(ra)) if reactant_smiles else None,
        'product': render_structure(product_smiles,sorted(pa)) if product_smiles else None,
        'reactant_atoms':sorted(ra),'product_atoms':sorted(pa)
    }
