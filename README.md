# Chemical Reaction Mechanism Automation V6.5

**V6.5 = Advanced OCSR + Structure Verification Engine + Graphical Mechanism Engine**

The application accepts reaction/synthesis schemes as PDF, PNG, JPG or JPEG. It independently interprets each upload, detects individual molecular drawings, generates and verifies OCSR candidates, validates molecular graphs with RDKit, detects reaction centers, classifies the transformation, and renders a graphical mechanism pathway when the required structures are confirmed.

## Why V6.5

Previous versions could correctly describe a reaction while failing to recover the exact molecular graph from a complex scheme. V6.5 does not use RDKit as an optical recognizer. It separates the workflow into:

`scheme image → structure detection → isolated OCSR → candidate SMILES → RDKit validation → image-vs-render verification → user confirmation → atom mapping → mechanism`

## Setup

1. Upload this repository to GitHub.
2. Deploy `app.py` with Streamlit Cloud.
3. Keep Python 3.12 (`runtime.txt` and `.python-version` are included).
4. Add at least one vision-capable AI provider in Streamlit Secrets. Gemini is the primary tested OCSR path.

Example `.streamlit/secrets.toml` entries are already provided. Put your own API keys in Streamlit Cloud Secrets rather than committing live keys.

## Notes

- V6.5 generates several candidates rather than forcing one structure.
- A chemically valid SMILES is not automatically considered visually correct.
- Low-confidence structures require confirmation.
- The graphical mechanism engine only becomes exact when reactant and product molecular graphs are confirmed.
