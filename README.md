# Chemical Reaction Mechanism Automation V6.6

## Reaction Drawing Workspace + Direct Molecular Graph Automation

V6.6 changes the preferred input from image recognition to **explicit chemical graphs**.

### Preferred V6.6 flow

```text
Draw molecule / paste SMILES / load RXN
            ↓
Exact molecular graph
            ↓
RDKit sanitization
            ↓
Reactant ↔ product atom mapping
            ↓
Bond-change / reaction-center detection
            ↓
Reaction classification
            ↓
Named-reaction / mechanism knowledge base
            ↓
Intermediate generation
            ↓
Graphical mechanism pathway
            ↓
JSON / RXN export
```

Image/PDF OCSR is still included as a legacy page for literature and patent schemes.

## Input modes

1. **Draw single reaction**
   - 1–4 reactants
   - 1–3 products
   - reagent / catalyst / solvent / temperature / time / atmosphere fields
   - direct mechanism analysis

2. **Build multi-step route**
   - add route steps sequentially
   - previous product can seed the next starting material
   - analyze the entire route
   - export route JSON

3. **Paste Reaction SMILES / load RXN**
   - expert-mode direct graph input
   - bypasses all OCSR

4. **Legacy PDF/Image OCSR**
   - V6.5 Advanced OCSR retained under `pages/4_Legacy_PDF_Image_OCSR.py`

## Drawing engine

V6.6 prefers `streamlit-chem` (Ketcher-backed `st.chem_draw`) and includes
`streamlit-ketcher` as a fallback. A direct SMILES field is always available.

The drawing tool bypasses optical structure recognition, but RDKit validation is
still retained to check graph/valence/sanitization quality.

## Deployment

- Python: **3.12**
- Main entry: `app.py`
- Streamlit Cloud: point the app to the repository root and `app.py`.

## Important design principle

**OCSR is no longer required for normal use.** It is only a compatibility path
for existing PDFs/images. Exact drawings and direct molecular formats are the
recommended inputs for mechanism automation.
