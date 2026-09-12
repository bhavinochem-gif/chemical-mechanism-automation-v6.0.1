"""Pure-Pillow molecular graph renderer.

V6.2.2 fallback for hosts where RDKit's rdMolDraw2D binary extension is not
available. It uses RDKit only for molecule parsing / optional 2D coordinates,
then draws bonds and atom labels with Pillow. No SVG, HTML, browser iframe,
or rdkit.Chem.Draw import is required.
"""
from __future__ import annotations

from math import cos, sin, pi
from typing import Iterable, Optional, Sequence

from PIL import Image, ImageDraw, ImageFont
from rdkit import Chem


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _coords(mol):
    """Return simple 2D coordinates; prefer RDKit depiction, then conformer,
    then deterministic circular graph layout."""
    work = Chem.Mol(mol)
    try:
        from rdkit.Chem import rdDepictor
        rdDepictor.Compute2DCoords(work)
        conf = work.GetConformer()
        return work, [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y) for i in range(work.GetNumAtoms())]
    except Exception:
        pass

    try:
        conf = work.GetConformer()
        pts = [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y) for i in range(work.GetNumAtoms())]
        if len({(round(x, 3), round(y, 3)) for x, y in pts}) > 1:
            return work, pts
    except Exception:
        pass

    n = max(1, work.GetNumAtoms())
    pts = [(cos(2*pi*i/n), sin(2*pi*i/n)) for i in range(n)]
    return work, pts


def _scale(points, size, margin=65):
    w, h = size
    xs = [p[0] for p in points] or [0.0]
    ys = [p[1] for p in points] or [0.0]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    dx = max(maxx-minx, 1.0)
    dy = max(maxy-miny, 1.0)
    scale = min((w-2*margin)/dx, (h-2*margin)/dy)
    ox = (w - scale*(minx+maxx))/2
    oy = (h + scale*(miny+maxy))/2
    # flip y for image coordinates
    return [(ox + scale*x, oy - scale*y) for x, y in points]


def _unit_perp(x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1
    d = max((dx*dx+dy*dy)**0.5, 1e-9)
    return -dy/d, dx/d


def render_molecule_pillow(smiles: str, size=(760, 430), highlight_atoms: Optional[Sequence[int]] = None,
                           title: Optional[str] = None):
    mol = Chem.MolFromSmiles(str(smiles).strip()) if smiles else None
    if mol is None:
        return None

    mol, raw = _coords(mol)
    pts = _scale(raw, size)
    highlights = set(highlight_atoms or [])

    img = Image.new("RGB", size, "white")
    d = ImageDraw.Draw(img)
    bond_width = max(2, int(min(size)/180))
    sep = max(4, int(min(size)/100))

    # Bonds first.
    for bond in mol.GetBonds():
        a = bond.GetBeginAtomIdx(); b = bond.GetEndAtomIdx()
        x1, y1 = pts[a]; x2, y2 = pts[b]
        px, py = _unit_perp(x1, y1, x2, y2)
        bt = bond.GetBondType()
        if bt == Chem.BondType.TRIPLE:
            offsets = (-sep, 0, sep)
        elif bt == Chem.BondType.DOUBLE:
            offsets = (-sep/2, sep/2)
        else:
            offsets = (0,)
        for off in offsets:
            d.line((x1+px*off, y1+py*off, x2+px*off, y2+py*off), fill="black", width=bond_width)
        if bond.GetIsAromatic():
            # light dashed center hint for aromatic bonds
            segments = 8
            for k in range(0, segments, 2):
                t1 = k/segments; t2 = (k+1)/segments
                xa=x1+(x2-x1)*t1; ya=y1+(y2-y1)*t1
                xb=x1+(x2-x1)*t2; yb=y1+(y2-y1)*t2
                d.line((xa,ya,xb,yb), fill="black", width=1)

    # Atom labels. Carbon is hidden except terminal/charged/highlighted carbon.
    font = _font(max(16, int(min(size)/21)))
    small = _font(max(12, int(min(size)/28)))
    for i, atom in enumerate(mol.GetAtoms()):
        sym = atom.GetSymbol()
        charge = atom.GetFormalCharge()
        isotope = atom.GetIsotope()
        show = sym != "C" or charge != 0 or isotope or atom.GetDegree() == 0
        x, y = pts[i]
        if i in highlights:
            r = max(10, int(min(size)/35))
            d.ellipse((x-r,y-r,x+r,y+r), outline="black", width=2)
            show = True
        if not show:
            continue
        label = (str(isotope) if isotope else "") + sym
        if charge:
            label += ("+" if charge == 1 else "-" if charge == -1 else f"{abs(charge)}{'+' if charge>0 else '-'}")
        bbox = d.textbbox((0,0), label, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        pad = 3
        d.rectangle((x-tw/2-pad, y-th/2-pad, x+tw/2+pad, y+th/2+pad), fill="white")
        d.text((x-tw/2, y-th/2), label, fill="black", font=font)

    if title:
        d.text((18, 12), title, fill="black", font=small)
    return img
