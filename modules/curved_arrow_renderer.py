"""Curved-arrow primitives for V6.4.

These functions draw *visual electron-flow annotations* on a PIL image.
They only draw arrows when a start/end position is supplied by a verified
or user-confirmed molecular graph workflow. They do not infer chemistry.
"""
from PIL import ImageDraw
import math


def _bezier(p0, p1, p2, t):
    u=1-t
    return (u*u*p0[0]+2*u*t*p1[0]+t*t*p2[0], u*u*p0[1]+2*u*t*p1[1]+t*t*p2[1])


def draw_curved_arrow(image, start, end, bend=0.28, width=4, head=14):
    """Draw a quadratic Bezier curved arrow onto a PIL image."""
    d=ImageDraw.Draw(image)
    sx,sy=start; ex,ey=end
    mx,my=(sx+ex)/2,(sy+ey)/2
    dx,dy=ex-sx,ey-sy
    L=max((dx*dx+dy*dy)**0.5,1.0)
    nx,ny=-dy/L,dx/L
    ctrl=(mx+nx*L*bend,my+ny*L*bend)
    pts=[_bezier(start,ctrl,end,i/36) for i in range(37)]
    d.line(pts,fill=(25,25,25),width=width)
    p_prev=pts[-3]
    ang=math.atan2(ey-p_prev[1],ex-p_prev[0])
    a1=(ex-head*math.cos(ang-0.55),ey-head*math.sin(ang-0.55))
    a2=(ex-head*math.cos(ang+0.55),ey-head*math.sin(ang+0.55))
    d.polygon([end,a1,a2],fill=(25,25,25))
    return image
