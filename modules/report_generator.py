import io,json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Preformatted
from reportlab.lib.styles import getSampleStyleSheet
def make_pdf_report(p):
 b=io.BytesIO();d=SimpleDocTemplate(b,pagesize=A4);s=getSampleStyleSheet()
 story=[Paragraph("Chemical Reaction Mechanism Automation V6.0.2",s["Title"]),Paragraph(str(p.get("analysis",{}).get("route_summary","")),s["BodyText"])]
 for x in p.get("mechanisms",[]):story.append(Preformatted(json.dumps(x,indent=2),s["Code"]))
 d.build(story);return b.getvalue()
