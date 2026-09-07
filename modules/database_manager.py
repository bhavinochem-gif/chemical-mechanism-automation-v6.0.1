import json
from pathlib import Path
class ChemistryDatabase:
 def __init__(self,d="data"):
  self.data={}; self.files=[]
  for p in sorted(Path(d).glob("*.json")):
   try:self.data[p.stem]=json.loads(p.read_text(encoding="utf8"));self.files.append(p.name)
   except Exception as e:self.data[p.stem]={"error":str(e)}
 def get(self,n,default=None): return self.data.get(n,default)
