# Chemical Reaction Mechanism Automation V6.4

V6.4 is the general-ROS build. It fixes the major V6.2.x behavior where unrelated uploaded routes could inherit the same Pd alpha-arylation interpretation.

## Pipeline

Upload PDF/image → reset prior-upload state → full-route vision interpretation → candidate structure crops → structure recognition → RDKit SMILES validation → molecular graph → reactant/product atom mapping → reaction-center detection → reaction classification → named-reaction candidates → mechanism cards → report.

## Important behavior

The app does **not** assign a named reaction when evidence is insufficient. It returns `Requires structure verification` and asks for structure confirmation instead of inventing a mechanism.

## Streamlit Cloud

Python 3.12 is pinned. Structure rendering tries RDKit `rdMolDraw2D` first and automatically falls back to the Pure-Pillow molecular-graph renderer if the drawing extension is unavailable.
