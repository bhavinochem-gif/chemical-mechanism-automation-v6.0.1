"""V6.6 drawing workspace adapter.

Primary editor: streamlit-chem / Ketcher (`st.chem_draw`) when available.
Fallback: streamlit-ketcher. Final fallback: direct SMILES input.
"""
from __future__ import annotations
import inspect
import streamlit as st
from .direct_graph_engine import canonical_smiles, validate_structure

# Import for registration/side effects if installed.
try:
    import streamlit_chem  # noqa: F401
except Exception:
    pass


def editor_backend() -> str:
    if callable(getattr(st, "chem_draw", None)):
        return "streamlit-chem / Ketcher"
    try:
        from streamlit_ketcher import st_ketcher  # noqa: F401
        return "streamlit-ketcher / Ketcher"
    except Exception:
        return "SMILES fallback"


def _call_chem_draw(initial_smiles: str, key: str):
    fn = getattr(st, "chem_draw", None)
    if not callable(fn):
        return None
    # Support minor API changes conservatively.
    attempts = [
        lambda: fn(initial_smiles, key=key),
        lambda: fn(value=initial_smiles, key=key),
        lambda: fn(smiles=initial_smiles, key=key),
        lambda: fn(initial_smiles),
    ]
    for call in attempts:
        try:
            return call()
        except TypeError:
            continue
        except Exception:
            return None
    return None


def _call_streamlit_ketcher(initial_smiles: str, key: str):
    try:
        from streamlit_ketcher import st_ketcher
    except Exception:
        return None
    try:
        sig = inspect.signature(st_ketcher)
        if "key" in sig.parameters:
            return st_ketcher(initial_smiles, key=key)
        return st_ketcher(initial_smiles)
    except Exception:
        try:
            return st_ketcher(initial_smiles)
        except Exception:
            return None


def draw_structure(label: str, key: str, initial_smiles: str = "") -> dict:
    """Render a structure editor and return canonical graph information.

    The result always contains `smiles`, `valid`, `backend` and `validation`.
    """
    st.markdown(f"**{label}**")
    result = None
    backend = editor_backend()

    if backend.startswith("streamlit-chem"):
        result = _call_chem_draw(initial_smiles, key)
    elif backend.startswith("streamlit-ketcher"):
        result = _call_streamlit_ketcher(initial_smiles, key)

    # A direct text field is always available for interoperability and recovery.
    if result is not None:
        smi = canonical_smiles(result)
    else:
        smi = ""

    current = smi or initial_smiles or ""
    edited = st.text_input(
        f"{label} SMILES",
        value=current,
        key=f"{key}_smiles",
        help="The drawing editor feeds this molecular graph. You may also paste an exact SMILES directly.",
    ).strip()

    validation = validate_structure(edited)
    if edited and validation.get("valid"):
        st.success(
            f"Valid molecular graph • {validation.get('formula','')} • "
            f"{validation.get('atoms',0)} atoms"
        )
    elif edited:
        st.error("Invalid molecular graph. Correct the drawing/SMILES before mechanism analysis.")

    return {
        "label": label,
        "backend": backend,
        "smiles": validation.get("canonical_smiles", "") if validation.get("valid") else "",
        "valid": bool(validation.get("valid")),
        "validation": validation,
    }
