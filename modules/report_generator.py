import io, json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet

def make_pdf_report(report):
    b=io.BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4); styles=getSampleStyleSheet()
    flow=[Paragraph("Chemical Reaction Mechanism Automation V6.4",styles["Title"]),Spacer(1,12)]
    flow.append(Paragraph(str(report.get("analysis",{}).get("route_summary","")),styles["BodyText"])); flow.append(Spacer(1,10))
    for m in report.get("mechanisms",[]):
        flow += [Paragraph(f"Step {m.get('step','')}: {m.get('classification',{}).get('reaction_class','')}",styles["Heading2"]), Preformatted(json.dumps(m,indent=2,default=str),styles["Code"]), Spacer(1,8)]
    doc.build(flow); return b.getvalue()
