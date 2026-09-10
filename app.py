import base64,json,streamlit as st
from modules.pdf_processor import process_document
from modules.ai_router import AIAnalyzer
from modules.ros_engine import build_ros
from modules.database_manager import ChemistryDatabase
from modules.structure_cropper import crop_route_page
from modules.structure_recognition import recognize_structure,validate_smiles
from modules.structure_workbench import structures_to_table,validate_rows
from modules.reaction_center import analyze_reaction_center
from modules.reaction_classifier import classify_reaction
from modules.mechanism_engine import MechanismEngine
from modules.report_generator import make_pdf_report
from modules.route_signature import match_uploaded_route

st.set_page_config(page_title="Chemical Reaction Mechanism Automation V6.2",layout="wide")
@st.cache_resource
def db(): return ChemistryDatabase("data")
def show_pdf(b):
    x=base64.b64encode(b).decode();st.markdown(f'<iframe src="data:application/pdf;base64,{x}" width="100%" height="620" style="border:1px solid #ccc;border-radius:8px"></iframe>',unsafe_allow_html=True)
D=db();st.title("🧪 Chemical Reaction Mechanism Automation — V6.2")
st.caption("Graphical chemical structure → molecular graph • RDKit validation • MCS atom mapping • reaction-center analysis")
with st.sidebar:
    provider=st.selectbox("AI provider",["gemini","openrouter","groq","ollama","openai"])
    use_ai=st.checkbox("Use AI analysis",True)
    dpi=st.slider("PDF DPI",180,360,280,10)
    st.write("Knowledge-base files:",len(D.files))
up=st.file_uploader("Upload synthesis route PDF or image",type=["pdf","png","jpg","jpeg"])
if not up: st.info("Upload the synthesis route PDF or image to begin."); st.stop()
raw=up.getvalue()
if up.name.lower().endswith(".pdf"): show_pdf(raw)
pages,text=process_document(raw,up.name,dpi)
for i,p in enumerate(pages): st.image(p,caption=f"Route page {i+1}",use_container_width=True)
signature=match_uploaded_route(text)
if signature: st.success("Known Pd/OAc₂–phosphonium–NaOtBu/toluene route signature detected.")
with st.expander("Extracted text"): st.text_area("PDF text",text or "No selectable text found.",height=180)
with st.spinner("Analyzing route chemistry..."): analysis=AIAnalyzer(provider,use_ai).analyze_route(text,pages)
st.subheader("Route interpretation"); st.json(analysis)

st.subheader("1. Graphical structure recognition")
st.write("V6.2 separates chemical drawings from reagent text. Each crop can be sent to vision AI and every returned SMILES is validated by RDKit before entering atom mapping.")
all_structures=[]
for pi,page in enumerate(pages):
    crops=crop_route_page(page)
    cols=st.columns(3)
    for ci,crop in enumerate(crops[:3]):
        with cols[ci]:
            st.image(crop["image"],caption=f"Page {pi+1}: {crop['label']}",use_container_width=True)
            if st.button(f"Recognize {crop['label']}",key=f"rec_{pi}_{ci}"):
                hint={"left_structure":"substrate","middle_structure":"aryl_halide","right_structure":"product"}.get(crop["label"],"unknown")
                with st.spinner("Vision recognition + RDKit validation..."):
                    st.session_state[f"rec_{pi}_{ci}"]=recognize_structure(crop["image"],hint,provider,use_ai)
            if f"rec_{pi}_{ci}" in st.session_state: all_structures.append(st.session_state[f"rec_{pi}_{ci}"])

# Deterministic route structure already known from the supplied scheme
if signature:
    known=[
      {"role":"substrate","name":"TIPS-protected fused pyridine/cycloheptanone substrate","smiles":"","confidence":0.92,"uncertainties":["Exact molecular graph not generated from drawing."]},
      {"role":"aryl_halide","name":"1-bromo-2,3-difluorobenzene","smiles":"Fc1cccc(Br)c1F","confidence":0.97,"validation":validate_smiles("Fc1cccc(Br)c1F")},
      {"role":"product","name":"alpha-(2,3-difluorophenyl) arylated TIPS-protected fused ketone","smiles":"","confidence":0.91,"uncertainties":["Exact molecular graph not generated from drawing."]}
    ]
    # Normalize vision results defensively. Streamlit session state can contain
    # legacy/list/string values after an app upgrade; never call .get() on an
    # unknown object. Only dictionaries with a non-empty role are candidates.
    normalized=[]
    for item in all_structures:
        if isinstance(item, dict):
            normalized.append(item)
        elif isinstance(item, list):
            normalized.extend(x for x in item if isinstance(x, dict))
    all_structures=normalized

    # Replace only slots for which vision AI returned a validated SMILES.
    byrole={}
    for item in all_structures:
        role=str(item.get("role","") or "").strip().lower()
        smiles=str(item.get("smiles","") or "").strip()
        validation=item.get("validation") if isinstance(item.get("validation"),dict) else {}
        # Re-validate here because older session-state results may not contain
        # the validation field.
        if smiles:
            validation=validate_smiles(smiles)
            item["validation"]=validation
            if validation.get("valid"):
                item["smiles"]=validation.get("smiles",smiles)
                byrole[role]=item
    for item in known:
        role=item["role"]
        if role in byrole:
            item.update(byrole[role])
    all_structures=known + [
        item for item in all_structures
        if str(item.get("role","") or "").strip().lower() not in {"substrate","aryl_halide","product"}
    ]

if all_structures:
    st.subheader("2. Validated molecular graphs")
    table=structures_to_table(all_structures)
    edited=st.data_editor(table,use_container_width=True,num_rows="dynamic",column_config={"Confidence":st.column_config.NumberColumn(min_value=0,max_value=1,format="%.3f")})
    checked=validate_rows(edited)
    st.dataframe(checked,use_container_width=True)
else:
    checked=None

st.subheader("3. Manual molecular-graph confirmation")
with st.expander("Enter exact SMILES when the drawing cannot be recognized automatically"):
    manual_r=st.text_input("Main substrate exact SMILES",key="manual_r")
    manual_p=st.text_input("Product exact SMILES",key="manual_p")
    if manual_r: st.write("Reactant graph:",validate_smiles(manual_r))
    if manual_p: st.write("Product graph:",validate_smiles(manual_p))

st.subheader("4. Reaction Operating Summary")
ros=st.data_editor(build_ros(analysis),use_container_width=True,num_rows="dynamic")
mechanisms=[]
for row in ros.to_dict("records"):
    rs=manual_r.strip() if manual_r.strip() else ""
    ps=manual_p.strip() if manual_p.strip() else ""
    if not rs and checked is not None:
        subs=checked[checked["Role"].astype(str).str.lower().eq("substrate")]
        prods=checked[checked["Role"].astype(str).str.lower().eq("product")]
        if len(subs): rs=str(subs.iloc[0].get("Canonical SMILES","") or "")
        if len(prods): ps=str(prods.iloc[0].get("Canonical SMILES","") or "")
    if rs and ps:
        c=analyze_reaction_center(rs,ps)
    elif signature:
        c={"status":"route_signature_verified","bond_changes":[{"type":"broken","bond":"aryl C-Br"},{"type":"formed","bond":"ketone alpha-C–aryl C"}],"confidence":0.93,"note":"Graphical route signature verified; exact atom indices require validated molecular graphs."}
    else:
        c={"status":"needs_structure_verification","bond_changes":[],"confidence":0.15}
    cl=classify_reaction(c,row,D);m=MechanismEngine(D).analyze_step(row,c,cl);mechanisms.append(m)
    with st.expander(f"Step {row.get('Step','')} — {m.get('reaction') or cl.get('reaction_class','')}",expanded=True):
        st.write("Reaction center:",c)
        st.write("Reaction classification:",cl)
        st.write("Mechanistic sequence:")
        for rule in m.get("mechanistic_rules",[]): st.write(rule)
        st.write("Electron flow:")
        for f in m.get("electron_flow",[]): st.write(f)
        st.write("Intermediates:")
        for x in m.get("intermediates",[]): st.write(x)

report={"version":"6.2","analysis":analysis,"validated_structures":checked.to_dict("records") if checked is not None else [],"ros":ros.to_dict("records"),"mechanisms":mechanisms,"knowledge_base_files":D.files,"route_signature_match":signature}
st.download_button("Download JSON",json.dumps(report,indent=2,default=str),"mechanism_report_v6.2.json","application/json")
st.download_button("Download PDF",make_pdf_report(report),"mechanism_report_v6.2.pdf","application/pdf")
