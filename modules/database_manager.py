import json
from pathlib import Path
class ChemistryDatabase:
 def __init__(self,folder="data"):
  self.data={};self.files=[]
  for p in sorted(Path(folder).glob("*.json")):
   try:self.data[p.stem]=json.loads(p.read_text(encoding="utf-8"))
   except Exception:self.data[p.stem]={"_error":"parse failure"}
   self.files.append(p.name)
 def search(self,q,limit=20):return[n for n,d in self.data.items() if q.lower() in json.dumps(d,ensure_ascii=False).lower()][:limit]
 def get(self,n,default=None):return self.data.get(n,default)
