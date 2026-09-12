from __future__ import annotations

from typing import Dict
from PIL import Image, ImageOps, ImageFilter


def trim_whitespace(image: Image.Image, threshold: int = 248, pad: int = 10) -> Image.Image:
    img = ImageOps.exif_transpose(image).convert("RGB")
    gray = ImageOps.grayscale(img)
    inv = gray.point(lambda p: 255 if p < threshold else 0)
    box = inv.getbbox()
    if not box:
        return img
    x1, y1, x2, y2 = box
    x1 = max(0, x1 - pad); y1 = max(0, y1 - pad)
    x2 = min(img.width, x2 + pad); y2 = min(img.height, y2 + pad)
    return img.crop((x1, y1, x2, y2))


def make_ocrs_variants(image: Image.Image, min_width: int = 1100) -> Dict[str, Image.Image]:
    """Create complementary OCSR views without changing molecular connectivity.

    The variants are deliberately conservative: upscale, contrast/sharpen, and
    threshold. No line reconstruction or OCR-driven atom replacement occurs here.
    """
    base = trim_whitespace(image)
    scale = max(1.0, min_width / max(1, base.width))
    if scale > 1.0:
        base = base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)

    contrast = ImageOps.autocontrast(base.convert("L"), cutoff=1).convert("RGB")
    contrast = contrast.filter(ImageFilter.UnsharpMask(radius=1.3, percent=170, threshold=2))

    gray = ImageOps.autocontrast(base.convert("L"), cutoff=1)
    bw = gray.point(lambda p: 255 if p > 190 else 0).convert("RGB")

    return {"original": base, "contrast": contrast, "binary": bw}
