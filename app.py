import hashlib, json
import streamlit as st
from modules.pdf_processor import process_document
from modules.ai_router import AIAnalyzer
from modules.ros_engine import build_ros
from modules.database_manager import ChemistryDatabase
from modules.structure_cropper import crop_route_page
from modules.structure_recognition import recognize_structure, validate_smiles
from modules.structure_workbench import structures_to_table, validate_rows
from modules.reaction_center import analyze_reaction_center
from modules.reaction_classifier import classify_reaction
from modules.mechanism_engine import MechanismEngine
from modules.report_generator import make_pdf_report
from modules.mechanism_renderer import render_structure, cards_from_mechanism, drawing_backend
from modules.route_signature import signature_hits
from modules.intermediate_structure_generator import generate_intermediate_structures
from modules.mechanism_path_renderer import render_mechanism_pathway
from modules.reaction_center_visualizer import reaction_center_images

st.set_page_config(page_title="Chemical Reaction Mechanism Automation V6.4", layout="wide")

@st.cache_resource
def db(): return ChemistryDatabase("data")
D=db()

st.title("🧪 Chemical Reaction Mechanism Automation — V6.4")
st.caption("General ROS recognition + Graphical Mechanism Engine. Validated structures are rendered as a mechanism pathway with reaction-center highlighting.")

with st.sidebar:
    provider=st.selectbox("AI provider",["gemini","openrouter","groq","ollama","openai"])
    use_ai=st.checkbox("Use AI route + structure recognition",True)
    dpi=st.slider("PDF rendering DPI",180,420,320,10)
    st.caption(f"Structure renderer: {drawing_backend()}")
    st.caption(f"Knowledge-base files: {len(D.files)}")

up=st.file_uploader("Upload a synthesis route (ROS) PDF or image",type=["pdf","png","jpg","jpeg"])
if not up:
    st.info("Upload a reaction/synthesis scheme to begin."); st.stop()
raw=up.getvalue(); file_hash=hashlib.sha256(raw).hexdigest()[:20]

# Critical V6.4 fix: clear prior-upload recognition state automatically.
if st.session_state.get("active_file_hash") != file_hash:
    for k in list(st.session_state.keys()):
        if k.startswith("rec_") or k.startswith("manual_") or k in {"analysis_cache","checked_cache"}:
            del st.session_state[k]
    st.session_state["active_file_hash"] = file_hash

pages,text=process_document(raw,up.name,dpi)
st.subheader("1. Uploaded ROS")
if up.name.lower().endswith(".pdf"):
    st.download_button("Download original PDF",raw,file_name=up.name,mime="application/pdf")
for i,p in enumerate(pages): st.image(p,caption=f"ROS page {i+1}",use_container_width=True)

with st.expander("Extracted text"):
    st.text_area("Text",text or "No selectable text found.",height=150)

st.subheader("2. Independent reaction interpretation")
with st.spinner("Analyzing this ROS independently..."):
    analysis=AIAnalyzer(provider,use_ai).analyze_route(text,pages)

st.markdown("### Reaction summary")
st.write(analysis.get("route_summary","Reaction interpretation requires verification."))
steps=analysis.get("steps",[]) if isinstance(analysis,dict) else []
for s in steps:
    cols=st.columns(4)
    mats=s.get("starting_materials",[]) or []
    with cols[0]:
        st.markdown("**Starting material(s)**")
        st.write("; ".join((x.get("name") or x.get("smiles") or "Unrecognized") for x in mats) or "Unrecognized")
    with cols[1]:
        st.markdown("**Reagents / catalysts**")
        st.write(", ".join((s.get("reagents",[]) or [])+(s.get("catalysts",[]) or [])) or "Not recognized")
    with cols[2]:
        st.markdown("**Product**")
        p=s.get("product",{}) or {}; st.write(p.get("name") or p.get("smiles") or "Unrecognized")
    with cols[3]:
        st.markdown("**Proposed reaction**")
        st.write(s.get("reaction") or s.get("reaction_class") or "Unclassified transformation")

sigs=signature_hits(text)
if sigs:
    with st.expander("Supplementary reagent-signature evidence"):
        st.json(sigs)

st.subheader("3. Graphical structure recognition")
st.caption("Recognize each structure independently. A SMILES is accepted only after RDKit validation.")
all_structures=[]
for pi,page in enumerate(pages):
    crops=crop_route_page(page)
    st.markdown(f"**Page {pi+1} candidate regions**")
    cols=st.columns(3)
    for ci,crop in enumerate(crops[:3]):
        with cols[ci]:
            st.image(crop["image"],caption=crop["label"],use_container_width=True)
            hint={"left_structure":"substrate","middle_structure":"unknown","right_structure":"product"}.get(crop["label"],"unknown")
            key=f"rec_{file_hash}_{pi}_{ci}"
            if st.button(f"Recognize {crop['label']}",key="btn_"+key):
                with st.spinner("Recognizing structure..."):
                    st.session_state[key]=recognize_structure(crop["image"],hint,provider,use_ai)
            result=st.session_state.get(key)
            if isinstance(result,dict):
                all_structures.append(result)
                st.write(result.get("name",""))
                if result.get("smiles"):
                    st.code(result["smiles"])
                elif result:
                    st.warning("Exact structure not validated; SMILES withheld.")

checked=None
if all_structures:
    st.subheader("4. Molecular graph validation")
    table=structures_to_table(all_structures)
    edited=st.data_editor(table,use_container_width=True,num_rows="dynamic",key="structure_editor_"+file_hash)
    checked=validate_rows(edited)
    st.dataframe(checked,use_container_width=True)
    for _,row in checked.iterrows():
        smi=str(row.get("Canonical SMILES","") or "")
        if smi:
            img=render_structure(smi)
            if img is not None: st.image(img,caption=f"Validated {row.get('Role','structure')}",width=520)
else:
    st.info("No validated graphical structures yet. You can still review/edit the AI reaction interpretation below.")

st.subheader("5. Exact structure confirmation (recommended when OCR is incomplete)")
with st.expander("Enter validated reactant/product SMILES"):
    manual_r=st.text_input("Main reactant/substrate SMILES",key="manual_r_"+file_hash)
    manual_p=st.text_input("Product SMILES",key="manual_p_"+file_hash)
    if manual_r: st.write(validate_smiles(manual_r))
    if manual_p: st.write(validate_smiles(manual_p))

st.subheader("6. Reaction table and mechanism")
ros=st.data_editor(build_ros(analysis),use_container_width=True,num_rows="dynamic",key="ros_"+file_hash)
mechanisms=[]
for row in ros.to_dict("records"):
    rs=manual_r.strip(); ps=manual_p.strip()
    if checked is not None:
        try:
            if not rs:
                q=checked[checked["Role"].astype(str).str.lower().isin(["substrate","reactant","starting_material"])]
                if len(q): rs=str(q.iloc[0].get("Canonical SMILES","") or "")
            if not ps:
                q=checked[checked["Role"].astype(str).str.lower().eq("product")]
                if len(q): ps=str(q.iloc[0].get("Canonical SMILES","") or "")
        except Exception: pass
    center=analyze_reaction_center(rs,ps) if rs and ps else {"status":"needs_structure_verification","bond_changes":[],"confidence":0.0}
    classification=classify_reaction(center,row,D)
    mech=MechanismEngine(D).analyze_step(row,center,classification)
    mechanisms.append(mech)

    st.markdown(f"### Step {row.get('Step','')} — {classification.get('reaction_class','Requires structure verification')}")
    st.write(f"Confidence: {classification.get('confidence',0):.0%}")
    if classification.get("evidence"):
        st.caption("Evidence: " + "; ".join(map(str,classification["evidence"])))
    if center.get("status") != "ok":
        st.warning("Molecular-graph confirmation is incomplete. The mechanism below is provisional and is not treated as an exact atom-mapped mechanism.")
    # V6.4 graphical mechanism engine
    st.markdown("#### Graphical mechanism pathway")
    nodes=generate_intermediate_structures(classification.get("reaction_class",""),rs,ps,mech)
    pathway=render_mechanism_pathway(nodes,classification.get("reaction_class",""),center.get("bond_changes",[]))
    if pathway is not None:
        st.image(pathway,use_container_width=True)
    else:
        st.info("A graphical pathway will appear once molecular structures are validated.")

    if rs or ps:
        rcimgs=reaction_center_images(rs,ps,center)
        if rcimgs.get("reactant") is not None or rcimgs.get("product") is not None:
            with st.expander("Reaction-center highlighting"):
                c1,c2=st.columns(2)
                with c1:
                    if rcimgs.get("reactant") is not None: st.image(rcimgs["reactant"],caption="Reactant reaction center",use_container_width=True)
                with c2:
                    if rcimgs.get("product") is not None: st.image(rcimgs["product"],caption="Product reaction center",use_container_width=True)

    st.markdown("#### Written mechanism")
    for card in cards_from_mechanism(mech):
        st.markdown(f"**{card['step']}. {card['title']}**")
        st.write(card["description"])
    if center.get("bond_changes"):
        with st.expander("Detected bond changes / atom-mapping evidence"):
            st.json(center["bond_changes"])

report={
    "version":"6.4",
    "file_hash":file_hash,
    "analysis":analysis,
    "validated_structures":checked.to_dict("records") if checked is not None else [],
    "ros":ros.to_dict("records"),
    "mechanisms":mechanisms,
    "knowledge_base_files":D.files,
    "design":"general_ros_recognition_plus_graphical_mechanism_engine",
}
st.subheader("7. Reports")
st.download_button("Download JSON report",json.dumps(report,indent=2,default=str),"mechanism_report_v6.4.json","application/json")
st.download_button("Download PDF report",make_pdf_report(report),"mechanism_report_v6.4.pdf","application/pdf")
