import base64,json,os,io
SCHEMA={"route_summary":"","steps":[{"step":1,"starting_materials":[{"name":"","smiles":"","confidence":0}],"reagents":[],"catalysts":[],"solvents":[],"conditions":{"temperature":"","time":"","pressure":"","atmosphere":""},"product":{"name":"","smiles":"","confidence":0},"yield":"","reaction":"","reaction_class":"","named_reaction":"","uncertainties":[]}]}
PROMPT="Analyze the synthesis route images. Graphical chemical structures are primary evidence. Do not invent SMILES when unreadable. Return JSON only using this schema: "+json.dumps(SCHEMA)
class AIAnalyzer:
    def __init__(self,provider="gemini",use_ai=True): self.provider=provider; self.use_ai=use_ai
    def _secret(self,n):
        try:
            import streamlit as st; return st.secrets.get(n,"")
        except Exception:return ""
    def _parts(self,text,pages):
        a=[{"type":"text","text":PROMPT+"\nTEXT:\n"+(text or "")[:30000]}]
        for i,p in enumerate(pages):
            b=io.BytesIO();p.save(b,format="PNG");q=base64.b64encode(b.getvalue()).decode()
            a += [{"type":"text","text":f"PAGE {i+1}"},{"type":"image","image_url":"data:image/png;base64,"+q}]
        return a
    def analyze_route(self,text,pages):
        if not self.use_ai:return self._fallback()
        try:return self._gemini(text,pages) if self.provider=="gemini" else self._compatible(text,pages)
        except Exception as e:
            x=self._fallback();x["ai_error"]=str(e);return x
    def _gemini(self,text,pages):
        from google import genai
        c=genai.Client(api_key=os.getenv("GEMINI_API_KEY") or self._secret("GEMINI_API_KEY"));model=os.getenv("GEMINI_MODEL") or self._secret("GEMINI_MODEL") or "gemini-3.6-flash"
        r=c.interactions.create(model=model,input=self._parts(text,pages),response_format={"type":"text","mime_type":"application/json"})
        return self._parse(getattr(r,"output_text",None) or str(r))
    def _compatible(self,text,pages):
        from openai import OpenAI
        cfg={"openrouter":("OPENROUTER_API_KEY","OPENROUTER_MODEL","https://openrouter.ai/api/v1","openrouter/free"),"groq":("GROQ_API_KEY","GROQ_MODEL","https://api.groq.com/openai/v1","qwen/qwen3.6-27b"),"ollama":("OLLAMA_API_KEY","OLLAMA_MODEL",self._secret("OLLAMA_BASE_URL") or "http://localhost:11434/v1","gemma3:12b"),"openai":("OPENAI_API_KEY","OPENAI_MODEL",None,"gpt-5.6-luna")}[self.provider]
        key=os.getenv(cfg[0]) or self._secret(cfg[0]) or ("ollama" if self.provider=="ollama" else "");model=os.getenv(cfg[1]) or self._secret(cfg[1]) or cfg[3]
        r=OpenAI(api_key=key,base_url=cfg[2]).chat.completions.create(model=model,messages=[{"role":"user","content":self._parts(text,pages)}],temperature=0)
        return self._parse(r.choices[0].message.content)
    def _parse(self,x):
        x=x.strip()
        if x.startswith("```"):x=x.split("\n",1)[1].rsplit("```",1)[0]
        return json.loads(x)
    def _fallback(self):
        return {"route_summary":"Structure recognition requires verification.","steps":[{"step":1,"starting_materials":[{"name":"","smiles":"","confidence":0}],"reagents":[],"catalysts":[],"solvents":[],"conditions":{"temperature":"","time":"","pressure":"","atmosphere":""},"product":{"name":"","smiles":"","confidence":0},"yield":"","reaction":"","reaction_class":"Requires structure verification","named_reaction":"None identified","uncertainties":["Graphical structures could not be deterministically recognized."]}]}
