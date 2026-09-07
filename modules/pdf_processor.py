import io,fitz
from PIL import Image
def process_pdf(pdf_bytes,dpi=170):
    doc=fitz.open(stream=pdf_bytes,filetype="pdf"); pages=[]; texts=[]
    for page in doc:
        texts.append(page.get_text("text"))
        pix=page.get_pixmap(dpi=dpi,alpha=False)
        pages.append(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
    doc.close(); return pages,"\n\n".join(texts)
