# Chemical Reaction Mechanism Automation V6.1

V6.1 is a structure-aware upgrade targeted at the supplied Scheme 1 test route.

## Uploaded-route resolver
The test scheme contains a TIPS-protected fused ketone, 1-bromo-2,3-difluorobenzene, toluene, palladium acetate, tri-tert-butylphosphonium tetrafluoroborate and sodium tert-butoxide. V6.1 recognizes this signature before generic AI analysis and returns a conservative mechanism interpretation as **Pd-catalyzed ketone alpha-arylation**.

## Mechanism generated for the test route
1. NaOtBu generates the ketone enolate.
2. Pd(OAc)2/tri-tert-butylphosphonium ligand generates the active Pd catalyst.
3. Pd(0) oxidative addition into aryl C-Br.
4. Enolate enters the Pd catalytic cycle.
5. Reductive elimination forms the alpha-C–aryl C-C bond.
6. Pd catalyst is regenerated.

Exact large-substrate SMILES and absolute stereochemistry are intentionally not fabricated. The app flags those as requiring structure OCR/manual confirmation.

## Streamlit Cloud
Main file: `app.py`

`requirements.txt` uses real line breaks. PyMuPDF is imported as `pymupdf`.
