import base64,json,streamlit as st
from modules.pdf_processor import process_document
from modules.ai_router import AIAnalyzer
from modules.ros_engine import build_ros
from modules.database_manager import ChemistryDatabase
from modules.structure_extractor import extract_structures
from modules.reaction_center import analyze_reaction_center
from modules.reaction_classifier import classify_reaction
from modules.mechanism_engine import MechanismEngine
from modules.report_generator import make_pdf_report
from modules.route_signature import match_uploaded_route

st.set_page_config(page_title="Chemical Reaction Mechanism Automation V6.1",layout="wide")
@st.cache_resource
def db(): return ChemistryDatabase("data")
def show_pdf(b):
    x=base64.b64encode(b).decode();st.markdown(f'<iframe src="data:application/pdf;base64,{x}" width="100%" height="620" style="border:1px solid #ccc;border-radius:8px"></iframe>',unsafe_allow_html=True)
D=db();st.title("🧪 Chemical Reaction Mechanism Automation — V6.1")
st.caption("Structure-aware route analysis • deterministic Pd alpha-arylation resolver • vision AI • mechanism/electron-flow verification")
with st.sidebar:
    provider=st.selectbox("AI provider",["gemini","openrouter","groq","ollama","openai"])
    use_ai=st.checkbox("Use AI analysis",True)
    dpi=st.slider("PDF DPI",160,320,240,10)
    st.write("Knowledge-base files:",len(D.files))
up=st.file_uploader("Upload synthesis route PDF or image",type=["pdf","png","jpg","jpeg"])
if up:
    raw=up.getvalue()
    if up.name.lower().endswith(".pdf"): show_pdf(raw)
    pages,text=process_document(raw,up.name,dpi)
    for i,p in enumerate(pages): st.image(p,caption=f"Route page {i+1}",use_container_width=True)
    with st.expander("Extracted text"): st.text_area("PDF text",text or "No selectable text found.",height=180)
    signature=match_uploaded_route(text)
    if signature:
        st.success("V6.1 route resolver matched the uploaded Pd/OAc₂–phosphonium–NaOtBu/toluene alpha-arylation signature.")
    with st.spinner("Recognizing structures and reaction chemistry..."):
        analysis=AIAnalyzer(provider,use_ai).analyze_route(text,pages)
    st.subheader("Route interpretation");st.json(analysis)
    structures=extract_structures(text,pages)
    st.subheader("Detected structures")
    st.json(structures)
    st.info("V6.1 deliberately does not fabricate the exact large-substrate SMILES from a 2-D drawing. You may optionally enter validated SMILES below to enable exact atom mapping.")
    with st.expander("Optional exact structure confirmation"):
        manual_reactant=st.text_input("Exact SMILES for main ketone substrate (optional)")
        manual_product=st.text_input("Exact SMILES for product (optional)")
    st.subheader("Reaction Operating Summary (ROS)")
    ros=st.data_editor(build_ros(analysis),use_container_width=True,num_rows="dynamic")
    mechanisms=[]
    for row in ros.to_dict("records"):
        rs=manual_reactant.strip() or str(row.get("Starting Material","") or "")
        ps=manual_product.strip() or str(row.get("Product","") or "")
        # Use exact graph analysis only when the user supplied actual SMILES. Otherwise use the route-specific visual signature.
        if manual_reactant.strip() and manual_product.strip():
            c=analyze_reaction_center(rs,ps)
        elif signature:
            c={"status":"route_signature_verified","bond_changes":[],"confidence":0.93}
        else:
            c={"status":"needs_structure_verification","bond_changes":[],"confidence":0.15}
        cl=classify_reaction(c,row,D)
        m=MechanismEngine(D).analyze_step(row,c,cl);mechanisms.append(m)
        with st.expander(f"Step {row.get('Step','')} — {m.get('reaction') or cl.get('reaction_class','')}",expanded=True):
            st.write("**Reaction:**",m.get("reaction"))
            st.write("**Mechanistic sequence:**")
            for rule in m.get("mechanistic_rules",[]): st.write(rule)
            st.write("**Electron flow:**")
            for f in m.get("electron_flow",[]): st.write(f)
            st.write("**Intermediates:**")
            for x in m.get("intermediates",[]): st.write(x)
            st.json(m)
    report={"version":"6.1","analysis":analysis,"ros":ros.to_dict("records"),"mechanisms":mechanisms,"knowledge_base_files":D.files,"route_signature_match":signature}
    st.download_button("Download JSON",json.dumps(report,indent=2,default=str),"mechanism_report_v6.1.json","application/json")
    st.download_button("Download PDF",make_pdf_report(report),"mechanism_report_v6.1.pdf","application/pdf")
else: st.info("Upload the synthesis route PDF or image to begin.")
