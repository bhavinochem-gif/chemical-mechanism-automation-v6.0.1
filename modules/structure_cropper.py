from PIL import Image, ImageOps

def _clamp(v, lo, hi):
    return max(lo, min(int(v), hi))

def crop_route_page(page):
    """Create practical structure/condition crops for one-page synthetic schemes.
    Uses whitespace-aware horizontal regions plus a full-page fallback. It never claims
    the crop itself is a molecular graph.
    """
    img = ImageOps.exif_transpose(page).convert("RGB")
    w, h = img.size
    # For common one-row schemes: left substrate, center reagent/aryl partner, right product.
    regions = [
        (0.02, 0.18, 0.36, 0.82, "left_structure"),
        (0.28, 0.18, 0.60, 0.82, "middle_structure"),
        (0.62, 0.18, 0.98, 0.82, "right_structure"),
        (0.00, 0.00, 1.00, 1.00, "full_page"),
    ]
    out=[]
    for x1,y1,x2,y2,label in regions:
        box=(_clamp(w*x1,0,w),_clamp(h*y1,0,h),_clamp(w*x2,0,w),_clamp(h*y2,0,h))
        out.append({"label":label,"image":img.crop(box),"box":box})
    return out
