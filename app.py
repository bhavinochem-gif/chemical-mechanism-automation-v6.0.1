import json
import streamlit as st

from modules.database_manager import ChemistryDatabase
from modules.drawing_workspace import draw_structure, editor_backend
from modules.direct_graph_engine import molecular_graph, validate_structure
from modules.reaction_step_model import ReactionStep
from modules.route_builder import validate_route, suggested_next_substrate
from modules.direct_reaction_analyzer import analyze_direct_step
from modules.mechanism_path_renderer import render_mechanism_pathway
from modules.mechanism_renderer import cards_from_mechanism, render_structure
from modules.reaction_center_visualizer import reaction_center_images
from modules.reaction_input_adapter import parse_reaction_smiles, parse_rxn_block
from modules.reaction_export import reaction_to_rxn_block

st.set_page_config(
    page_title="Chemical Reaction Mechanism Automation V6.6",
    layout="wide",
)

@st.cache_resource
def chemistry_db():
    return ChemistryDatabase("data")

D = chemistry_db()

def conditions_ui(prefix: str):
    c1, c2 = st.columns(2)
    with c1:
        reagents = st.text_input("Reagents / bases", key=f"{prefix}_reagents")
        catalysts = st.text_input("Catalysts / ligands", key=f"{prefix}_catalysts")
        solvents = st.text_input("Solvent(s)", key=f"{prefix}_solvents")
    with c2:
        temperature = st.text_input("Temperature", key=f"{prefix}_temperature")
        time = st.text_input("Time", key=f"{prefix}_time")
        atmosphere = st.text_input("Atmosphere", key=f"{prefix}_atmosphere")
    return {
        "reagents": reagents,
        "catalysts": catalysts,
        "solvents": solvents,
        "temperature": temperature,
        "time": time,
        "atmosphere": atmosphere,
    }

def show_analysis(step: ReactionStep, result: dict, prefix: str):
    cls = result.get("classification", {})
    center = result.get("reaction_center", {})
    mech = result.get("mechanism", {})

    st.markdown("### Reaction interpretation")
    a, b, c = st.columns(3)
    a.metric("Reaction class", cls.get("reaction_class", "Unclassified"))
    b.metric("Confidence", f"{float(cls.get('confidence', 0) or 0):.0%}")
    c.metric("Bond changes", len(center.get("bond_changes", []) or []))

    if cls.get("evidence"):
        st.caption("Evidence: " + "; ".join(map(str, cls.get("evidence", []))))

    if center.get("status") != "ok":
        st.warning("Reaction-center mapping is incomplete. Review structures before accepting the mechanism.")

    st.markdown("### Graphical mechanism pathway")
    pathway = render_mechanism_pathway(
        result.get("intermediates", []),
        cls.get("reaction_class", ""),
        center.get("bond_changes", []) or [],
    )
    if pathway is not None:
        st.image(pathway, use_container_width=True)
    else:
        st.info("A graphical pathway could not be generated for this transformation yet.")

    rc = reaction_center_images(step.reactant_smiles, step.product_smiles, center)
    if rc.get("reactant") is not None or rc.get("product") is not None:
        with st.expander("Reaction-center structures"):
            x, y = st.columns(2)
            with x:
                if rc.get("reactant") is not None:
                    st.image(rc["reactant"], caption="Reactant side", use_container_width=True)
            with y:
                if rc.get("product") is not None:
                    st.image(rc["product"], caption="Product side", use_container_width=True)

    st.markdown("### Written mechanism")
    cards = cards_from_mechanism(mech)
    if cards:
        for card in cards:
            st.markdown(f"**{card.get('step','')}. {card.get('title','Mechanism step')}**")
            st.write(card.get("description", ""))
    else:
        st.info("No mechanism rules matched with enough confidence.")

    with st.expander("Direct molecular graphs and atom/bond data"):
        st.markdown("**Reactant molecular graph**")
        st.json(molecular_graph(step.reactant_smiles))
        st.markdown("**Product molecular graph**")
        st.json(molecular_graph(step.product_smiles))
        st.markdown("**Detected bond changes**")
        st.json(center.get("bond_changes", []))

    payload = {
        "version": "6.6",
        "input_mode": "direct_molecular_graph",
        "step": step.to_dict(),
        "analysis": result,
    }
    st.download_button(
        "Download step analysis JSON",
        json.dumps(payload, indent=2, default=str),
        file_name=f"v6.6_step_{step.step_no}_analysis.json",
        mime="application/json",
        key=f"{prefix}_download_json",
    )
    rxn_block = reaction_to_rxn_block(step)
    if rxn_block:
        st.download_button(
            "Download RXN file",
            rxn_block,
            file_name=f"v6.6_step_{step.step_no}.rxn",
            mime="chemical/x-mdl-rxnfile",
            key=f"{prefix}_download_rxn",
        )

st.title("🧪 Chemical Reaction Mechanism Automation — V6.6")
st.caption(
    "Reaction Drawing Workspace + Direct Molecular Graph Automation. "
    "Drawing/direct graph input bypasses OCSR and feeds exact molecular topology into the mechanism engine."
)

with st.sidebar:
    st.markdown("### V6.6 status")
    st.write(f"Drawing backend: **{editor_backend()}**")
    st.write(f"Knowledge-base files: **{len(D.files)}**")
    st.info(
        "Preferred workflow: draw or paste exact structures. "
        "PDF/image OCSR remains available as a legacy page when needed."
    )

tab1, tab2, tab3 = st.tabs([
    "✏️ Draw single reaction",
    "🧬 Build multi-step route",
    "⌨️ Paste SMILES / RXN",
])

# ---------------- Single reaction ----------------
with tab1:
    st.subheader("Draw a reaction")
    st.caption("Draw each molecule separately. Exact molecular graphs go directly to RDKit and reaction-center analysis.")

    n_reactants = st.number_input("Number of reactant structures", 1, 4, 2, 1, key="single_n_r")
    n_products = st.number_input("Number of product structures", 1, 3, 1, 1, key="single_n_p")

    reactants = []
    st.markdown("### Reactants")
    for i in range(int(n_reactants)):
        with st.expander(f"Reactant {i+1}", expanded=True):
            item = draw_structure(f"Reactant {i+1}", f"single_r_{i}")
            if item["valid"]:
                reactants.append(item["smiles"])

    products = []
    st.markdown("### Products")
    for i in range(int(n_products)):
        with st.expander(f"Product {i+1}", expanded=True):
            item = draw_structure(f"Product {i+1}", f"single_p_{i}")
            if item["valid"]:
                products.append(item["smiles"])

    st.markdown("### Reaction conditions")
    cond = conditions_ui("single")
    notes = st.text_area("Notes", key="single_notes")

    step = ReactionStep(
        step_no=1,
        reactants=reactants,
        products=products,
        reagents=cond["reagents"],
        catalysts=cond["catalysts"],
        solvents=cond["solvents"],
        temperature=cond["temperature"],
        time=cond["time"],
        atmosphere=cond["atmosphere"],
        notes=notes,
    )

    if st.button("Analyze drawn reaction", type="primary", use_container_width=True):
        check = validate_route([step])
        if not check["valid"]:
            st.error("Draw/enter at least one valid reactant and one valid product before analysis.")
        else:
            st.session_state["single_analysis"] = analyze_direct_step(step, D)
            st.session_state["single_step"] = step

    if "single_analysis" in st.session_state and "single_step" in st.session_state:
        show_analysis(st.session_state["single_step"], st.session_state["single_analysis"], "single")

# ---------------- Multi-step route ----------------
with tab2:
    st.subheader("Multi-step synthesis route builder")
    st.caption(
        "Add one reaction step at a time. The previous product can automatically become the next step's starting material."
    )

    if "v66_route_steps" not in st.session_state:
        st.session_state["v66_route_steps"] = []

    route_steps = st.session_state["v66_route_steps"]
    next_no = len(route_steps) + 1
    suggested = suggested_next_substrate(route_steps)

    st.markdown(f"### Add route step {next_no}")
    main_sub = draw_structure("Main substrate", f"route_{next_no}_main", suggested)
    partner = draw_structure("Reaction partner (optional)", f"route_{next_no}_partner", "")
    product = draw_structure("Product", f"route_{next_no}_product", "")
    cond = conditions_ui(f"route_{next_no}")
    yld = st.text_input("Yield", key=f"route_{next_no}_yield")
    notes = st.text_area("Step notes", key=f"route_{next_no}_notes")

    if st.button(f"Add step {next_no} to route", use_container_width=True):
        rs = []
        if main_sub["valid"]:
            rs.append(main_sub["smiles"])
        if partner["valid"]:
            rs.append(partner["smiles"])
        ps = [product["smiles"]] if product["valid"] else []

        new_step = ReactionStep(
            step_no=next_no,
            reactants=rs,
            products=ps,
            reagents=cond["reagents"],
            catalysts=cond["catalysts"],
            solvents=cond["solvents"],
            temperature=cond["temperature"],
            time=cond["time"],
            atmosphere=cond["atmosphere"],
            yield_text=yld,
            notes=notes,
        )
        if validate_route([new_step])["valid"]:
            st.session_state["v66_route_steps"].append(new_step)
            st.success(f"Step {next_no} added.")
            st.rerun()
        else:
            st.error("The step needs at least one valid reactant and one valid product.")

    if route_steps:
        st.markdown("### Current route")
        for s in route_steps:
            with st.expander(f"Step {s.step_no}: {s.reaction_smiles}", expanded=False):
                st.write("Reagents:", s.reagents or "—")
                st.write("Catalysts:", s.catalysts or "—")
                st.write("Solvents:", s.solvents or "—")
                st.code(s.reaction_smiles, language=None)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Analyze entire route", type="primary", use_container_width=True):
                results = [analyze_direct_step(s, D) for s in route_steps]
                st.session_state["v66_route_analysis"] = results
        with c2:
            if st.button("Clear route", use_container_width=True):
                st.session_state["v66_route_steps"] = []
                st.session_state.pop("v66_route_analysis", None)
                st.rerun()

        results = st.session_state.get("v66_route_analysis")
        if results:
            for s, r in zip(route_steps, results):
                st.divider()
                st.markdown(f"## Route step {s.step_no}")
                show_analysis(s, r, f"route_result_{s.step_no}")

            route_payload = {
                "version": "6.6",
                "input_mode": "multi_step_direct_molecular_graph",
                "steps": [s.to_dict() for s in route_steps],
                "analysis": results,
            }
            st.download_button(
                "Download complete route JSON",
                json.dumps(route_payload, indent=2, default=str),
                file_name="v6.6_synthesis_route.json",
                mime="application/json",
            )

# ---------------- SMILES / RXN ----------------
with tab3:
    st.subheader("Direct expert input")
    mode = st.radio("Input format", ["Reaction SMILES", "RXN file"], horizontal=True)

    parsed_step = None
    if mode == "Reaction SMILES":
        rxn_smi = st.text_area(
            "Reaction SMILES",
            placeholder="reactant1.reactant2>>product",
            height=120,
        )
        if rxn_smi.strip():
            try:
                parsed_step = parse_reaction_smiles(rxn_smi)
            except Exception as exc:
                st.error(str(exc))
    else:
        rxn_file = st.file_uploader("Upload .rxn", type=["rxn"], key="rxn_upload")
        if rxn_file is not None:
            try:
                parsed_step = parse_rxn_block(rxn_file.getvalue().decode("utf-8", errors="ignore"))
            except Exception as exc:
                st.error(str(exc))

    if parsed_step is not None:
        st.success("Reaction molecular graph parsed successfully.")
        st.code(parsed_step.reaction_smiles, language=None)
        if st.button("Analyze direct reaction input", type="primary", use_container_width=True):
            st.session_state["direct_parsed_step"] = parsed_step
            st.session_state["direct_parsed_analysis"] = analyze_direct_step(parsed_step, D)

    if "direct_parsed_analysis" in st.session_state and "direct_parsed_step" in st.session_state:
        show_analysis(
            st.session_state["direct_parsed_step"],
            st.session_state["direct_parsed_analysis"],
            "direct",
        )

st.divider()
st.caption(
    "V6.6 keeps V6.5 Advanced OCSR as an optional Streamlit page for historical PDF/image schemes. "
    "Use the drawing workspace whenever exact structures can be entered directly."
)
