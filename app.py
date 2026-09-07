import base64,json,streamlit as st
from modules.pdf_processor import process_pdf
from modules.ai_router import AIAnalyzer
from modules.ros_engine import build_ros
from modules.database_manager import ChemistryDatabase
from modules.mechanism_engine import MechanismEngine
from modules.report_generator import make_pdf_report

st.set_page_config(page_title="Chemical Reaction Mechanism Automation V6.0.2",layout="wide")
def display_pdf(b,height=650):
    x=base64.b64encode(b).decode()
    st.markdown(f'<iframe src="data:application/pdf;base64,{x}" width="100%" height="{height}" style="border:1px solid #ccc;border-radius:8px"></iframe>',unsafe_allow_html=True)
@st.cache_resource
def db(): return ChemistryDatabase("data")
D=db()
st.title("🧪 Chemical Reaction Mechanism Automation — V6.0.2")
st.caption("Cloud-safe PDF viewer • PDF vision pages • ROS • chemistry knowledge base")
with st.sidebar:
    provider=st.selectbox("AI provider",["gemini","openrouter","groq","ollama","openai"])
    use_ai=st.checkbox("Use AI analysis",True)
    st.write("Knowledge-base files:",len(D.files))
up=st.file_uploader("Upload synthesis route PDF",type=["pdf"])
if up:
    raw=up.getvalue(); display_pdf(raw)
    pages,text=process_pdf(raw)
    with st.expander("Extracted PDF text"): st.text_area("Text",text or "No selectable text found.",height=200)
    st.subheader("Rendered route pages")
    for i,p in enumerate(pages): st.image(p,caption=f"Page {i+1}",use_container_width=True)
    with st.spinner("Analyzing route..."): analysis=AIAnalyzer(provider,use_ai).analyze_route(text,pages)
    st.subheader("Route interpretation"); st.json(analysis)
    st.subheader("Reaction Operating Summary (ROS)")
    ros=st.data_editor(build_ros(analysis),use_container_width=True,num_rows="dynamic")
    mech=MechanismEngine(D).analyze(ros,analysis)
    st.subheader("Mechanism candidates")
    for m in mech:
        with st.expander(f"Step {m['step']} — {m['reaction']}"):
            st.write(m)
    report={"version":"6.0.2","analysis":analysis,"ros":ros,"mechanisms":mech,"knowledge_base_files":D.files}
    st.download_button("Download JSON",json.dumps(report,indent=2,default=str),"mechanism_report_v6.0.2.json","application/json")
    st.download_button("Download PDF",make_pdf_report(report),"mechanism_report_v6.0.2.pdf","application/pdf")
else: st.info("Upload a synthesis route PDF to begin.")
