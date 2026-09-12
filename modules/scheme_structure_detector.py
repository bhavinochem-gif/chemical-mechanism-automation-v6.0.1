from __future__ import annotations

from typing import List, Dict
from PIL import Image, ImageOps

from .vision_json import call_vision_json

DETECT_PROMPT = r'''
Detect the individual CHEMICAL STRUCTURE drawings in this reaction scheme. Exclude reagent text, reaction arrows, yields, labels such as Formula-4, and prose.
Return JSON only:
{
  "structures":[
    {"role":"reactant|reagent_structure|product|unknown","label":"short label if visible","box":[x1,y1,x2,y2],"confidence":0.0}
  ]
}
Coordinates must be normalized integers from 0 to 1000 relative to the full image.
Boxes should tightly include the molecular drawing itself, including wedge/dash bonds and atom labels, with a small margin.
Do not merge two molecules separated by a plus sign.
'''


def _crop(image: Image.Image, box):
    w, h = image.size
    x1, y1, x2, y2 = [max(0, min(1000, int(v))) for v in box]
    px = (int(w*x1/1000), int(h*y1/1000), int(w*x2/1000), int(h*y2/1000))
    # small safety margin
    mx, my = max(4, int(w*0.01)), max(4, int(h*0.02))
    px = (max(0,px[0]-mx), max(0,px[1]-my), min(w,px[2]+mx), min(h,px[3]+my))
    return image.crop(px), px


def heuristic_regions(image: Image.Image) -> List[Dict]:
    """Conservative fallback for common left-to-right single-step schemes."""
    img = ImageOps.exif_transpose(image).convert("RGB")
    w, h = img.size
    specs = [
        ("reactant", "left structure", (0.00,0.00,0.25,0.78)),
        ("reagent_structure", "middle structure", (0.18,0.00,0.48,0.78)),
        ("product", "right structure", (0.67,0.00,1.00,0.88)),
    ]
    out=[]
    for role,label,(a,b,c,d) in specs:
        box=(int(w*a),int(h*b),int(w*c),int(h*d))
        out.append({"role":role,"label":label,"box":box,"confidence":0.35,"image":img.crop(box),"source":"heuristic"})
    return out


def detect_structure_regions(image: Image.Image, provider: str = "gemini", use_ai: bool = True) -> List[Dict]:
    img = ImageOps.exif_transpose(image).convert("RGB")
    if use_ai:
        try:
            obj = call_vision_json(DETECT_PROMPT, [img], provider)
            out=[]
            for i,s in enumerate((obj.get("structures") or [])[:12]):
                if not isinstance(s,dict) or not isinstance(s.get("box"),list) or len(s["box"]) != 4:
                    continue
                crop, px = _crop(img, s["box"])
                if crop.width < 30 or crop.height < 30:
                    continue
                out.append({
                    "role":s.get("role","unknown"),
                    "label":s.get("label") or f"structure {i+1}",
                    "box":px,
                    "confidence":float(s.get("confidence",0) or 0),
                    "image":crop,
                    "source":"vision_layout",
                })
            if len(out) >= 2:
                return out
        except Exception:
            pass
    return heuristic_regions(img)
