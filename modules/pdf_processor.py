import io
import pymupdf
from PIL import Image
def process_document(data,filename,dpi=220):
    if (filename or "").lower().endswith(".pdf"):
        d=pymupdf.open(stream=data,filetype="pdf"); pages=[]; texts=[]
        for p in d:
            texts.append(p.get_text("text")); pix=p.get_pixmap(dpi=dpi,alpha=False); pages.append(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
        d.close(); return pages,"\n\n".join(texts)
    return [Image.open(io.BytesIO(data)).convert("RGB")],""
def process_pdf(data,dpi=220): return process_document(data,"route.pdf",dpi)
