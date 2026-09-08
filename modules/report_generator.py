import io,json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted
from reportlab.lib.styles import getSampleStyleSheet
def make_pdf_report(r):
 b=io.BytesIO();d=SimpleDocTemplate(b,pagesize=A4);s=getSampleStyleSheet();x=[Paragraph("Chemical Reaction Mechanism Automation V6.0.3",s["Title"]),Spacer(1,12)]
 for m in r.get("mechanisms",[]):x += [Paragraph(f"Step {m.get('step','')}: {m.get('reaction','')}",s["Heading2"]),Preformatted(json.dumps(m,indent=2,default=str),s["Code"])]
 d.build(x);return b.getvalue()
