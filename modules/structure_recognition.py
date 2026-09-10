import base64, io, json, os, re
from PIL import Image
from rdkit import Chem

STRUCTURE_PROMPT = r"""
You are a chemical structure recognition assistant. Inspect ONLY the supplied structure crop.
Return JSON only with:
{
  "role":"substrate|aryl_halide|product|unknown",
  "name":"best chemical description",
  "smiles":"valid canonical or isomeric SMILES if and only if connectivity can be read",
  "confidence":0.0,
  "visual_features":["..."],
  "uncertainties":["..."]
}
Rules:
- Do not invent missing atoms, stereochemistry, ring closures, substituent positions, or protecting-group connectivity.
- If exact connectivity is not readable, return an empty SMILES and describe what is visible.
- Preserve wedge/dash as stereochemical information only when it can be assigned confidently.
- The goal is a molecular graph, not a reaction prediction.
"""

def validate_smiles(smiles):
    if not smiles: return {"valid":False,"smiles":"","reason":"empty"}
    mol=Chem.MolFromSmiles(smiles)
    if not mol: return {"valid":False,"smiles":smiles,"reason":"RDKit parse failed"}
    return {"valid":True,"smiles":Chem.MolToSmiles(mol,isomericSmiles=True),"atoms":mol.GetNumAtoms(),"bonds":mol.GetNumBonds()}

def _secret(name):
    try:
        import streamlit as st
        return st.secrets.get(name, "")
    except Exception:
        return os.getenv(name, "")

def _png_b64(image):
    b=io.BytesIO(); image.save(b,format="PNG",optimize=True); return base64.b64encode(b.getvalue()).decode()

def recognize_with_gemini(image, role_hint="unknown"):
    from google import genai
    key=os.getenv("GEMINI_API_KEY") or _secret("GEMINI_API_KEY")
    model=os.getenv("GEMINI_MODEL") or _secret("GEMINI_MODEL") or "gemini-3.6-flash"
    client=genai.Client(api_key=key)
    prompt=STRUCTURE_PROMPT+f"\nRole hint: {role_hint}"
    # Interactions API input parts; image is passed as inline data where supported.
    interaction=client.interactions.create(
        model=model,
        input=[
            {"type":"text","text":prompt},
            {"type":"image","image_url":"data:image/png;base64,"+_png_b64(image)},
        ],
        response_format={"type":"text","mime_type":"application/json"},
    )
    raw=getattr(interaction,"output_text",None) or str(interaction)
    raw=raw.strip()
    if raw.startswith("```"):
        raw=raw.split("\n",1)[1].rsplit("```",1)[0]
    obj=json.loads(raw)
    obj["role"]=obj.get("role") or role_hint
    obj["validation"]=validate_smiles(obj.get("smiles",""))
    if obj["validation"].get("valid"):
        obj["smiles"]=obj["validation"]["smiles"]
    else:
        obj["smiles"]=""
    return obj

def recognize_structure(image, role_hint="unknown", provider="gemini", use_ai=True):
    if not use_ai or provider!="gemini":
        return {"role":role_hint,"name":"Manual/AI structure recognition required","smiles":"","confidence":0.0,"visual_features":[],"uncertainties":["Vision structure recognition not run."],"validation":validate_smiles("")}
    try:
        return recognize_with_gemini(image, role_hint)
    except Exception as e:
        return {"role":role_hint,"name":"Structure recognition failed","smiles":"","confidence":0.0,"visual_features":[],"uncertainties":[str(e)],"validation":validate_smiles("")}
