import io
import pymupdf
from PIL import Image

def process_document(data,filename,dpi=220):
    filename=filename or ""
    if filename.lower().endswith(".pdf"):
        doc=pymupdf.open(stream=data,filetype="pdf");pages=[];texts=[]
        for page in doc:
            texts.append(page.get_text("text"));pix=page.get_pixmap(dpi=dpi,alpha=False);pages.append(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
        doc.close();return pages,"\n\n".join(texts)
    return [Image.open(io.BytesIO(data)).convert("RGB")],""

def process_pdf(data,dpi=220): return process_document(data,"route.pdf",dpi)
