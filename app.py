import hashlib, json
import pandas as pd
import streamlit as st

from modules.pdf_processor import process_document
from modules.ai_router import AIAnalyzer
from modules.ros_engine import build_ros
from modules.database_manager import ChemistryDatabase
from modules.scheme_structure_detector import detect_structure_regions
from modules.advanced_ocrs import recognize_candidates
from modules.smiles_verifier import validate_candidate
from modules.reaction_center import analyze_reaction_center
from modules.reaction_classifier import classify_reaction
from modules.mechanism_engine import MechanismEngine
from modules.report_generator import make_pdf_report
from modules.mechanism_renderer import render_structure, cards_from_mechanism, drawing_backend
from modules.intermediate_structure_generator import generate_intermediate_structures
from modules.mechanism_path_renderer import render_mechanism_pathway
from modules.reaction_center_visualizer import reaction_center_images
from modules.pairwise_structure_verifier import scaffold_conservation

st.set_page_config(page_title="Chemical Reaction Mechanism Automation V6.5", layout="wide")

@st.cache_resource
def db():
    return ChemistryDatabase("data")

D = db()

st.title("🧪 Chemical Reaction Mechanism Automation — V6.5")
st.caption("Advanced OCSR + Structure Verification Engine + V6.4 Graphical Mechanism Engine. Every uploaded ROS is analyzed independently.")

with st.sidebar:
    provider = st.selectbox("AI / vision provider", ["gemini", "openrouter", "groq", "ollama", "openai"])
    use_ai = st.checkbox("Use AI route + OCSR recognition", True)
    dpi = st.slider("PDF rendering DPI", 200, 480, 360, 20)
    auto_threshold = st.slider("OCSR auto-accept threshold", 0.70, 0.95, 0.78, 0.01)
    st.caption(f"Structure renderer: {drawing_backend()}")
    st.caption(f"Knowledge-base files: {len(D.files)}")

up = st.file_uploader("Upload a synthesis route (ROS) PDF or image", type=["pdf", "png", "jpg", "jpeg"])
if not up:
    st.info("Upload a reaction/synthesis scheme to begin.")
    st.stop()

raw = up.getvalue()
file_hash = hashlib.sha256(raw).hexdigest()[:20]

# Clear all OCSR/analysis choices when a different file is uploaded.
if st.session_state.get("active_file_hash") != file_hash:
    for k in list(st.session_state.keys()):
        if k.startswith(("ocrs_", "region_", "selected_", "manual_", "ros_", "analysis_", "confirm_", "role_")) or k in {"analysis_cache", "checked_cache"}:
            del st.session_state[k]
    st.session_state["active_file_hash"] = file_hash

pages, text = process_document(raw, up.name, dpi)

st.subheader("1. Uploaded ROS")
if up.name.lower().endswith(".pdf"):
    st.download_button("Download original PDF", raw, file_name=up.name, mime="application/pdf")
for i, p in enumerate(pages):
    st.image(p, caption=f"ROS page {i+1}", use_container_width=True)

with st.expander("Extracted text"):
    st.text_area("Text", text or "No selectable text found.", height=160)

st.subheader("2. Independent reaction interpretation")
analysis_key = f"analysis_{file_hash}_{provider}_{int(use_ai)}"
if analysis_key not in st.session_state:
    with st.spinner("Analyzing this ROS independently..."):
        st.session_state[analysis_key] = AIAnalyzer(provider, use_ai).analyze_route(text, pages)
analysis = st.session_state[analysis_key]

st.markdown("### Reaction summary")
st.write(analysis.get("route_summary", "Reaction interpretation requires verification."))
steps = analysis.get("steps", []) if isinstance(analysis, dict) else []
for s in steps:
    cols = st.columns(4)
    mats = s.get("starting_materials", []) or []
    with cols[0]:
        st.markdown("**Starting material(s)**")
        st.write("; ".join((x.get("name") or x.get("smiles") or "Unrecognized") for x in mats) or "Unrecognized")
    with cols[1]:
        st.markdown("**Reagents / catalysts**")
        st.write(", ".join((s.get("reagents", []) or []) + (s.get("catalysts", []) or [])) or "Not recognized")
    with cols[2]:
        st.markdown("**Product**")
        p = s.get("product", {}) or {}
        st.write(p.get("name") or p.get("smiles") or "Unrecognized")
    with cols[3]:
        st.markdown("**Proposed reaction**")
        st.write(s.get("reaction") or s.get("reaction_class") or "Unclassified transformation")

st.subheader("3. Advanced OCSR — structure-by-structure")
st.caption(
    "V6.5 first detects each molecular drawing, then performs OCSR on that isolated crop. "
    "Each candidate must pass RDKit validation and image-vs-render verification before auto-acceptance."
)

selected_structures = []
region_records = []

for pi, page in enumerate(pages):
    detect_key = f"region_{file_hash}_{pi}"
    if detect_key not in st.session_state:
        with st.spinner(f"Detecting molecular drawings on page {pi+1}..."):
            st.session_state[detect_key] = detect_structure_regions(page, provider, use_ai)
    regions = st.session_state.get(detect_key, []) or []

    st.markdown(f"### Page {pi+1}: detected molecular drawings")
    if not regions:
        st.warning("No structure regions detected on this page.")
        continue

    for ri, region in enumerate(regions):
        detected_role = str(region.get("role", "unknown") or "unknown")
        label = str(region.get("label", f"structure {ri+1}"))
        crop = region.get("image")
        key = f"ocrs_{file_hash}_{pi}_{ri}"
        role_options = ["reactant", "reagent_structure", "product", "unknown"]
        default_role_idx = role_options.index(detected_role) if detected_role in role_options else 3
        role = st.selectbox(
            f"Role for {label}", role_options, index=default_role_idx,
            key=f"role_{file_hash}_{pi}_{ri}",
            help="Correct the page-layout role if automatic structure detection assigned it incorrectly.",
        )

        st.markdown(f"#### {label} — role: `{role}`")
        c1, c2 = st.columns([1, 1.45])
        with c1:
            if crop is not None:
                st.image(crop, caption=f"Isolated crop • source: {region.get('source','')}", use_container_width=True)
            st.caption(f"Region confidence: {float(region.get('confidence',0) or 0):.0%}")
            if st.button("Run Advanced OCSR", key="btn_" + key, use_container_width=True):
                with st.spinner("Generating, validating, and visually verifying structure candidates..."):
                    st.session_state[key] = recognize_candidates(crop, role, provider, use_ai, accept_threshold=auto_threshold)

        with c2:
            result = st.session_state.get(key)
            if not isinstance(result, dict):
                st.info("Run Advanced OCSR for this structure crop.")
                continue

            if result.get("error"):
                st.error(result["error"])
            if result.get("visible_features"):
                st.write("**Visible features:** " + "; ".join(map(str, result.get("visible_features", []))))
            if result.get("global_uncertainties"):
                st.caption("Uncertainties: " + "; ".join(map(str, result.get("global_uncertainties", []))))

            candidates = result.get("candidates", []) or []
            if not candidates:
                st.warning("No defensible molecular-graph candidate was produced. Use manual SMILES/molfile confirmation instead of forcing a structure.")
                continue

            rows = []
            for idx, cand in enumerate(candidates):
                ver = cand.get("verification", {}) or {}
                rows.append({
                    "#": idx + 1,
                    "Valid": bool(cand.get("valid")),
                    "OCSR confidence": round(float(cand.get("confidence",0) or 0), 3),
                    "Image match": round(float(ver.get("match_score",0) or 0), 3),
                    "Combined score": round(float(cand.get("score",0) or 0), 3),
                    "SMILES": cand.get("canonical_smiles") or cand.get("smiles") or "",
                    "Verdict": ver.get("verdict", "unverified"),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            default_idx = 0
            auto = result.get("accepted")
            if auto:
                for idx, cand in enumerate(candidates):
                    if (cand.get("canonical_smiles") or "") == (auto.get("canonical_smiles") or ""):
                        default_idx = idx
                        break
                st.success("Top candidate passed V6.5 auto-verification.")
            else:
                st.warning("Candidate requires user confirmation; V6.5 will not silently treat it as exact.")

            chosen_idx = st.selectbox(
                "Candidate to inspect / use",
                options=list(range(len(candidates))),
                index=default_idx,
                format_func=lambda x: f"Candidate {x+1} • score {candidates[x].get('score',0):.2f}",
                key=f"selected_{file_hash}_{pi}_{ri}",
            )
            chosen = candidates[int(chosen_idx)]
            chosen_smiles = chosen.get("canonical_smiles") or ""

            if chosen_smiles:
                img = render_structure(chosen_smiles)
                if img is not None:
                    st.image(img, caption="Candidate rendered from validated molecular graph", width=620)
                st.code(chosen_smiles, language=None)
                ver = chosen.get("verification", {}) or {}
                if ver.get("mismatches"):
                    st.caption("Verifier mismatches: " + "; ".join(map(str, ver.get("mismatches", []))))

            edit_key = f"manual_{file_hash}_{pi}_{ri}"
            corrected = st.text_input(
                "Confirmed / corrected SMILES",
                value=chosen_smiles,
                key=edit_key,
                help="Edit only if you can confirm the molecular structure. RDKit validates the graph, not whether the drawing was read correctly.",
            ).strip()
            v = validate_candidate(corrected)
            if corrected and v.get("valid"):
                score = float(chosen.get("score",0) or 0)
                auto_ok = auto is not None and corrected == chosen_smiles
                edited_by_user = corrected != chosen_smiles
                confirm_key = f"confirm_{file_hash}_{pi}_{ri}"
                if auto_ok:
                    user_ok = True
                    st.success("Auto-verified structure accepted.")
                else:
                    user_ok = st.checkbox(
                        "I confirm this molecular structure matches the uploaded drawing",
                        key=confirm_key,
                        value=False,
                    )
                st.success(f"RDKit valid • {v.get('formula','')} • {v.get('atoms',0)} atoms")
                if auto_ok or user_ok:
                    status = "user_confirmed" if (user_ok and not auto_ok) else "auto_verified"
                    selected_structures.append({
                        "page": pi+1,
                        "region": ri+1,
                        "role": role,
                        "label": label,
                        "name": result.get("name", ""),
                        "smiles": v.get("canonical_smiles", ""),
                        "valid": True,
                        "ocrs_score": score,
                        "verification_match": float(chosen.get("verification",{}).get("match_score",0) or 0),
                        "status": status,
                        "confirmed": True,
                    })
                else:
                    st.info("Valid SMILES is shown for review but is not used in atom mapping until confirmed.")
            elif corrected:
                st.error("SMILES is not RDKit-valid. It will not be used for reaction-center analysis.")

        region_records.append({
            "page": pi+1,
            "region": ri+1,
            "role": role,
            "label": label,
            "box": region.get("box"),
            "source": region.get("source"),
            "ocrs": st.session_state.get(key),
        })

st.subheader("4. Structure verification workbench")
if selected_structures:
    verify_df = pd.DataFrame(selected_structures)
    st.dataframe(verify_df, use_container_width=True, hide_index=True)
else:
    verify_df = pd.DataFrame()
    st.info("No RDKit-valid OCSR structure has been selected yet.")

# Choose primary substrate/product only from valid selected structures.
reactants = [x for x in selected_structures if x.get("role") in {"reactant", "substrate", "starting_material"}]
partner_structures = [x for x in selected_structures if x.get("role") == "reagent_structure"]
products = [x for x in selected_structures if x.get("role") == "product"]
main_scaffold_r = reactants[0]["smiles"] if reactants else ""
reactant_side = [x["smiles"] for x in reactants + partner_structures if x.get("smiles")]
main_r = ".".join(dict.fromkeys(reactant_side))
main_p = products[0]["smiles"] if products else ""

if main_scaffold_r and main_p:
    pair = scaffold_conservation(main_scaffold_r, main_p)
    st.markdown("### Reactant ↔ product scaffold verification")
    c1, c2, c3 = st.columns(3)
    c1.metric("MCS atoms", pair.get("mcs_atoms", 0))
    c2.metric("Scaffold conservation", f"{pair.get('score',0):.0%}")
    c3.write(pair.get("interpretation", ""))
    if pair.get("score", 0) < 0.40:
        st.warning("Low scaffold conservation: inspect OCSR assignments before mechanism generation.")

st.subheader("5. Manual exact-structure override")
with st.expander("Enter main reactant/product SMILES when OCSR is incomplete"):
    manual_r = st.text_input("Reactant side SMILES (dot-separated reactants allowed)", value=main_r, key="manual_main_r_" + file_hash).strip()
    manual_p = st.text_input("Main product SMILES", value=main_p, key="manual_main_p_" + file_hash).strip()
    vr = validate_candidate(manual_r) if manual_r else {"valid": False}
    vp = validate_candidate(manual_p) if manual_p else {"valid": False}
    if manual_r:
        st.write("Reactant validation:", vr)
    if manual_p:
        st.write("Product validation:", vp)
    if manual_r and not vr.get("valid"):
        manual_r = ""
    if manual_p and not vp.get("valid"):
        manual_p = ""

st.subheader("6. Reaction table + graphical mechanism")
ros = st.data_editor(build_ros(analysis), use_container_width=True, num_rows="dynamic", key="ros_" + file_hash)
mechanisms = []
centers = []
classifications = []

for row in ros.to_dict("records"):
    rs = manual_r or main_r
    ps = manual_p or main_p
    center = analyze_reaction_center(rs, ps) if rs and ps else {"status":"needs_structure_verification","bond_changes":[],"confidence":0.0}
    classification = classify_reaction(center, row, D)
    mech = MechanismEngine(D).analyze_step(row, center, classification)
    centers.append(center); classifications.append(classification); mechanisms.append(mech)

    st.markdown(f"### Step {row.get('Step','')} — {classification.get('reaction_class','Requires structure verification')}")
    st.write(f"Confidence: {classification.get('confidence',0):.0%}")
    if classification.get("evidence"):
        st.caption("Evidence: " + "; ".join(map(str, classification["evidence"])))
    if center.get("status") != "ok":
        st.warning("Exact reactant/product molecular graphs are not both confirmed. Detailed mechanism remains provisional.")

    st.markdown("#### Graphical mechanism pathway")
    nodes = generate_intermediate_structures(classification.get("reaction_class", ""), rs, ps, mech)
    pathway = render_mechanism_pathway(nodes, classification.get("reaction_class", ""), center.get("bond_changes", []))
    if pathway is not None:
        st.image(pathway, use_container_width=True)
    else:
        st.info("Graphical pathway requires validated reactant/product structures.")

    if rs or ps:
        rcimgs = reaction_center_images(rs, ps, center)
        if rcimgs.get("reactant") is not None or rcimgs.get("product") is not None:
            with st.expander("Reaction-center highlighting"):
                a,b = st.columns(2)
                with a:
                    if rcimgs.get("reactant") is not None:
                        st.image(rcimgs["reactant"], caption="Reactant reaction center", use_container_width=True)
                with b:
                    if rcimgs.get("product") is not None:
                        st.image(rcimgs["product"], caption="Product reaction center", use_container_width=True)

    st.markdown("#### Written mechanism")
    for card in cards_from_mechanism(mech):
        st.markdown(f"**{card['step']}. {card['title']}**")
        st.write(card["description"])
    if center.get("bond_changes"):
        with st.expander("Detected bond changes / mapping evidence"):
            st.json(center["bond_changes"])

report = {
    "version":"6.5",
    "file_hash":file_hash,
    "analysis":analysis,
    "detected_structure_regions":region_records,
    "selected_structures":selected_structures,
    "main_reactant_smiles":manual_r or main_r,
    "main_product_smiles":manual_p or main_p,
    "ros":ros.to_dict("records"),
    "reaction_centers":centers,
    "classifications":classifications,
    "mechanisms":mechanisms,
    "knowledge_base_files":D.files,
    "design":"advanced_ocrs_structure_verification_plus_graphical_mechanism_engine",
}

st.subheader("7. Reports")
st.download_button("Download JSON report", json.dumps(report, indent=2, default=str), "mechanism_report_v6.5.json", "application/json")
st.download_button("Download PDF report", make_pdf_report(report), "mechanism_report_v6.5.pdf", "application/pdf")
