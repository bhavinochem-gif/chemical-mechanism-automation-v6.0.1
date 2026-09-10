from .pdf_processor import process_document
def analyze_document(data,filename,dpi=220):
 p,t=process_document(data,filename,dpi);return{"pages":p,"text":t}
