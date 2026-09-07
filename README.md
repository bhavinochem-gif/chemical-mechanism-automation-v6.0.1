# Chemical Reaction Mechanism Automation V6.0.2
This build removes `st.pdf()` and uses a base64 HTML iframe, avoiding the Streamlit Cloud PDF-element exception.

Workflow: PDF → text extraction + PNG page rendering → AI/vision analysis → editable ROS → chemistry knowledge base → mechanism candidates → JSON/PDF reports.

Run:
`pip install -r requirements.txt`
`streamlit run app.py`

Set provider API keys in Streamlit Cloud App Settings → Secrets. Do not commit real keys.
