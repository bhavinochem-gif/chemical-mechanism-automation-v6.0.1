import os,json,base64,io,re
class AIAnalyzer:
 def __init__(self,p="gemini",enabled=True):self.p=p;self.enabled=enabled
 def analyze_route(self,text,images):
  if not self.enabled:return self.fallback(text)
  try:
   if self.p=="gemini":return self.gemini(text,images)
   return self.compatible(text,images)
  except Exception as e:
   x=self.fallback(text);x["ai_error"]=str(e);return x
 def prompt(self,t):return """Extract this synthesis route into JSON with route_summary and steps. For each step give step, starting_material, reagent, solvent, temperature, time, product, yield, reaction. Never invent unreadable structures; use graphical structure—verification required.\n"""+(t or "(no text)")
 def gemini(self,t,ims):
  from google import genai
  from google.genai import types
  key=os.getenv("GEMINI_API_KEY","")
  if not key:raise RuntimeError("GEMINI_API_KEY not configured")
  c=genai.Client(api_key=key); parts=[types.Part(text=self.prompt(t))]
  for im in ims[:10]:
   b=io.BytesIO();im.save(b,"PNG");parts.append(types.Part(inline_data=types.Blob(mime_type="image/png",data=b.getvalue())))
  x=c.interactions.create(model=os.getenv("GEMINI_MODEL","gemini-3.6-flash"),input=parts,response_format={"type":"text","mime_type":"application/json"})
  return self.parse(getattr(x,"output_text",str(x)))
 def compatible(self,t,ims):
  from openai import OpenAI
  cfg={"openrouter":("OPENROUTER_API_KEY","https://openrouter.ai/api/v1","openrouter/free"),"groq":("GROQ_API_KEY","https://api.groq.com/openai/v1","qwen/qwen3.6-27b"),"ollama":("OLLAMA_ENABLED",os.getenv("OLLAMA_BASE_URL","http://localhost:11434/v1"),os.getenv("OLLAMA_MODEL","gemma3:12b")),"openai":("OPENAI_API_KEY","https://api.openai.com/v1",os.getenv("OPENAI_MODEL","gpt-5.6-luna"))}
  e,b,m=cfg[self.p]
  if self.p=="ollama":
   if os.getenv(e,"false").lower()!="true":raise RuntimeError("Ollama disabled")
   key="ollama"
  else:
   key=os.getenv(e,"")
   if not key:raise RuntimeError(e+" not configured")
  c=OpenAI(api_key=key,base_url=b);content=[{"type":"text","text":self.prompt(t)}]
  for im in ims[:6]:
   z=io.BytesIO();im.save(z,"PNG");content.append({"type":"image_url","image_url":{"url":"data:image/png;base64,"+base64.b64encode(z.getvalue()).decode()}})
  r=c.chat.completions.create(model=m,messages=[{"role":"user","content":content}],temperature=0)
  return self.parse(r.choices[0].message.content)
 def parse(self,x):
  s=str(x).strip();s=re.sub(r"^```json\s*","",s);s=re.sub(r"\s*```$","",s)
  try:return json.loads(s)
  except:
   m=re.search(r"\{.*\}",s,re.S)
   return json.loads(m.group()) if m else {"route_summary":s,"steps":[]}
 def fallback(self,t):
  return {"route_summary":"Fallback PDF text extraction; graphical structures require verification.","steps":[]}
