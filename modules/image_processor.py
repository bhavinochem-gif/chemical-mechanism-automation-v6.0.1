from PIL import ImageEnhance,ImageOps,ImageFilter
def preprocess(im):
 x=ImageEnhance.Contrast(ImageOps.grayscale(im.convert("RGB"))).enhance(1.5);return x.filter(ImageFilter.SHARPEN).convert("RGB")
