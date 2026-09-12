import base64, json, os, io

PROMPT = r'''
You are analyzing ONE newly uploaded chemical reaction/synthesis scheme. Treat every upload independently.
The graphical structures are primary evidence; extracted PDF text is secondary evidence.

Return JSON only with this schema:
{
  "route_summary":"plain-language summary",
  "steps":[{
    "step":1,
    "starting_materials":[{"name":"","smiles":"","confidence":0.0}],
    "reagents":[], "catalysts":[], "solvents":[],
    "conditions":{"temperature":"","time":"","pressure":"","atmosphere":""},
    "product":{"name":"","smiles":"","confidence":0.0},
    "yield":"",
    "reaction":"",
    "reaction_class":"",
    "named_reaction":"",
    "confidence":0.0,
    "evidence":[],
    "uncertainties":[]
  }],
  "recognition":{"structure_recognition":"","structure_smiles_status":"","confidence":0.0}
}

Rules:
- NEVER reuse a reaction assignment from a previous upload.
- Do not assume palladium alpha-arylation unless this upload itself supports it.
- Do not invent a named reaction.
- Do not invent SMILES, stereochemistry, ring closures or substituent positions.
- If a structure is unreadable, leave its SMILES empty and describe only visible features.
- Use "Unclassified transformation" if the evidence is insufficient.
- Use "None identified" for named_reaction if no named reaction is supported.
- A reaction assignment must be based on visible reactant/product change and/or matching reagents/conditions.
- Include uncertainties whenever graphical structure recognition is incomplete.
'''

class AIAnalyzer:
    def __init__(self, provider="gemini", use_ai=True):
        self.provider = provider
        self.use_ai = use_ai

    def _secret(self, name):
        try:
            import streamlit as st
            return st.secrets.get(name, "")
        except Exception:
            return os.getenv(name, "")

    def analyze_route(self, text, pages):
        if not self.use_ai:
            return self._fallback("AI analysis disabled.")
        try:
            if self.provider == "gemini":
                return self._gemini(text, pages)
            return self._compatible(text, pages)
        except Exception as exc:
            return self._fallback(f"AI analysis failed: {exc}")

    def _img(self, page):
        b = io.BytesIO()
        page.save(b, format="PNG")
        return base64.b64encode(b.getvalue()).decode()

    def _gemini(self, text, pages):
        from google import genai
        key = os.getenv("GEMINI_API_KEY") or self._secret("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL") or self._secret("GEMINI_MODEL") or "gemini-3.6-flash"
        client = genai.Client(api_key=key)
        parts = [{"type":"text", "text":PROMPT + "\nEXTRACTED TEXT:\n" + (text or "")[:30000]}]
        for page in pages[:6]:
            parts.append({"type":"image", "image_url":"data:image/png;base64," + self._img(page)})
        response = client.interactions.create(
            model=model,
            input=parts,
            response_format={"type":"text", "mime_type":"application/json"},
        )
        return self._parse(getattr(response, "output_text", None) or str(response))

    def _compatible(self, text, pages):
        from openai import OpenAI
        cfg = {
            "openrouter": ("OPENROUTER_API_KEY", "OPENROUTER_MODEL", "https://openrouter.ai/api/v1", "openrouter/free"),
            "groq": ("GROQ_API_KEY", "GROQ_MODEL", "https://api.groq.com/openai/v1", "qwen/qwen3.6-27b"),
            "ollama": ("OLLAMA_API_KEY", "OLLAMA_MODEL", self._secret("OLLAMA_BASE_URL") or "http://localhost:11434/v1", "gemma3:12b"),
            "openai": ("OPENAI_API_KEY", "OPENAI_MODEL", None, "gpt-5.6-luna"),
        }[self.provider]
        key = os.getenv(cfg[0]) or self._secret(cfg[0]) or ("ollama" if self.provider == "ollama" else "")
        model = os.getenv(cfg[1]) or self._secret(cfg[1]) or cfg[3]
        content = [{"type":"text", "text":PROMPT + "\nEXTRACTED TEXT:\n" + (text or "")[:30000]}]
        for page in pages[:6]:
            content.append({"type":"image_url", "image_url":{"url":"data:image/png;base64," + self._img(page)}})
        response = OpenAI(api_key=key, base_url=cfg[2]).chat.completions.create(
            model=model,
            messages=[{"role":"user", "content":content}],
            temperature=0,
        )
        return self._parse(response.choices[0].message.content)

    def _parse(self, raw):
        raw = (raw or "").strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            raise ValueError("AI response is not a JSON object")
        obj.setdefault("route_summary", "Reaction interpretation requires verification.")
        obj.setdefault("steps", [])
        obj.setdefault("recognition", {})
        return obj

    def _fallback(self, reason="Structure recognition requires verification."):
        return {
            "route_summary":"Reaction could not be assigned confidently from this upload.",
            "steps":[{
                "step":1, "starting_materials":[], "reagents":[], "catalysts":[], "solvents":[],
                "conditions":{}, "product":{"name":"", "smiles":"", "confidence":0.0},
                "yield":"", "reaction":"Unclassified transformation",
                "reaction_class":"Requires structure verification", "named_reaction":"None identified",
                "confidence":0.0, "evidence":[], "uncertainties":[reason]
            }],
            "recognition":{"structure_recognition":"incomplete", "structure_smiles_status":"unverified", "confidence":0.0},
        }
