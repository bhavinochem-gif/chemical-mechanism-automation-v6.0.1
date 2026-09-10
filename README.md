# Chemical Reaction Mechanism Automation V6.2

V6.2 focuses on **graphical chemical structure → validated molecular graph** conversion.

## Main upgrades
- High-resolution PDF/image rendering
- Structure-focused page crops
- Vision-AI structure recognition with SMILES output
- RDKit validation and canonical/isomeric SMILES normalization
- Editable molecular-graph workbench
- MCS-based atom mapping
- Reaction-center bond-change detection
- Existing V6.1 route-signature resolver for the supplied Pd alpha-arylation test route
- Mechanism/electron-flow/intermediate analysis
- JSON/PDF reports
- Cloud-safe PDF iframe viewer

## Important
The application never silently converts an uncertain drawing into an invented molecular graph. When vision recognition is uncertain, the SMILES remains blank and the UI provides a manual exact-SMILES confirmation route.

## Streamlit Cloud
Main file: `app.py`

Add `GEMINI_API_KEY` to Streamlit secrets for Gemini vision structure recognition.
