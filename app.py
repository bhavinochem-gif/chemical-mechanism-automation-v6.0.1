import base64,json,streamlit as st
from modules.pdf_processor import process_document
from modules.ai_router import AIAnalyzer
from modules.ros_engine import build_ros
from modules.database_manager import ChemistryDatabase
from modules.reaction_center import analyze_reaction_center
from modules.reaction_classifier import classify_reaction
from modules.mechanism_engine import MechanismEngine
from modules.report_generator import make_pdf_report
st.set_page_config(page_title="Chemical Reaction Mechanism Automation V6.0.3",layout="wide")
@st.cache_resource
def db(): return ChemistryDatabase("data")
def show_pdf(b):
    x=base64.b64encode(b).decode()
    st.markdown(f'<iframe src="data:application/pdf;base64,{x}" width="100%" height="600" style="border:1px solid #ccc"></iframe>',unsafe_allow_html=True)
D=db(); st.title("🧪 Chemical Reaction Mechanism Automation — V6.0.3")
with st.sidebar:
    provider=st.selectbox("AI provider",["gemini","openrouter","groq","ollama","openai"]); use_ai=st.checkbox("Use AI analysis",True); dpi=st.slider("PDF DPI",120,300,220,10); st.write("KB files:",len(D.files))
up=st.file_uploader("Upload synthesis route PDF or image",type=["pdf","png","jpg","jpeg"])
if up:
    raw=up.getvalue()
    if up.name.lower().endswith(".pdf"): show_pdf(raw)
    pages,text=process_document(raw,up.name,dpi)
    st.subheader("Route pages")
    for i,p in enumerate(pages): st.image(p,caption=f"Page {i+1}",use_container_width=True)
    with st.expander("Extracted text"): st.text_area("PDF text",text or "No selectable text found.",height=160)
    with st.spinner("Recognizing structures and reactions..."): analysis=AIAnalyzer(provider,use_ai).analyze_route(text,pages)
    st.subheader("Route interpretation"); st.json(analysis)
    st.subheader("Reaction Operating Summary"); ros=st.data_editor(build_ros(analysis),use_container_width=True,num_rows="dynamic")
    mechanisms=[]
    for row in ros.to_dict("records"):
        with st.expander(f"Step {row.get('Step','')} — {row.get('Reaction','') or 'Reaction under analysis'}",expanded=True):
            rs=str(row.get("Starting Material","") or ""); ps=str(row.get("Product","") or "")
            c=analyze_reaction_center(rs,ps) if rs and ps else {"status":"needs_structure_verification","bond_changes":[],"confidence":.15}
            cl=classify_reaction(c,row,D); m=MechanismEngine(D).analyze_step(row,c,cl); mechanisms.append(m)
            st.json(m)
    report={"version":"6.0.3","analysis":analysis,"ros":ros.to_dict("records"),"mechanisms":mechanisms,"knowledge_base_files":D.files}
    st.download_button("Download JSON",json.dumps(report,indent=2,default=str),"mechanism_report_v6.0.3.json","application/json")
    st.download_button("Download PDF",make_pdf_report(report),"mechanism_report_v6.0.3.pdf","application/pdf")
else: st.info("Upload a synthesis route PDF or image to begin.")
