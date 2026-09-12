"""Graphical mechanism pathway renderer for V6.4.

Produces a PNG pathway using validated chemical structures where available,
reaction arrows, step labels, and concise descriptions. No browser SVG/HTML.
"""
from PIL import Image, ImageDraw, ImageFont
from .mechanism_renderer import render_structure
from .curved_arrow_renderer import draw_curved_arrow


def _font(size=18,bold=False):
    paths=[
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
    ]
    for p in paths:
        try:return ImageFont.truetype(p,size)
        except Exception:pass
    return ImageFont.load_default()


def _wrap(text, n=48):
    words=str(text or '').split(); lines=[]; cur=[]
    for w in words:
        if len(' '.join(cur+[w]))>n and cur:
            lines.append(' '.join(cur)); cur=[w]
        else:cur.append(w)
    if cur: lines.append(' '.join(cur))
    return lines[:5]


def _arrow(draw,x1,y,x2):
    draw.line((x1,y,x2,y),fill=(30,30,30),width=4)
    draw.polygon([(x2,y),(x2-14,y-8),(x2-14,y+8)],fill=(30,30,30))


def render_mechanism_pathway(nodes, reaction_class='', bond_changes=None, canvas_width=1500):
    nodes=list(nodes or [])
    if not nodes:return None
    card_w=330; card_h=410; gap=80; margin=35
    n=len(nodes)
    rows=[]
    # maximum 4 cards per row keeps output readable on mobile/Streamlit
    for i in range(0,n,4): rows.append(nodes[i:i+4])
    W=canvas_width
    H=margin+len(rows)*(card_h+70)+80
    img=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(img)
    titlef=_font(26,True); headf=_font(19,True); bodyf=_font(15,False); smallf=_font(13,False)
    d.text((margin,15),f'Graphical mechanism pathway — {reaction_class or "reaction"}',fill=(20,20,20),font=titlef)
    y0=65
    global_index=0
    for row in rows:
        count=len(row)
        total=count*card_w+(count-1)*gap
        x0=(W-total)//2
        for j,node in enumerate(row):
            x=x0+j*(card_w+gap); y=y0
            d.rounded_rectangle((x,y,x+card_w,y+card_h),radius=16,outline=(145,145,145),width=2,fill=(250,250,250))
            d.text((x+14,y+12),f'{global_index+1}. {node.get("title","Stage")}',fill=(15,15,15),font=headf)
            smi=node.get('smiles','')
            if smi:
                molimg=render_structure(smi,size=(300,225))
                if molimg is not None:
                    molimg.thumbnail((300,225))
                    img.paste(molimg,(x+15,y+55))
                else:
                    d.text((x+18,y+120),'Structure rendering unavailable',fill=(90,90,90),font=bodyf)
            else:
                d.rounded_rectangle((x+20,y+70,x+card_w-20,y+245),radius=12,outline=(180,180,180),width=2)
                d.text((x+48,y+135),'Structure pending\nverification',fill=(90,90,90),font=headf)
            desc=node.get('description') or node.get('status','')
            ty=y+292
            for line in _wrap(desc,42):
                d.text((x+14,ty),line,fill=(45,45,45),font=smallf); ty+=19
            if j<count-1:
                _arrow(d,x+card_w+10,y+190,x+card_w+gap-10)
            global_index+=1
        y0 += card_h+70
    # legend
    d.text((margin,H-55),'Only validated molecular graphs are drawn. Conceptual stages are clearly marked pending verification.',fill=(70,70,70),font=smallf)
    return img
