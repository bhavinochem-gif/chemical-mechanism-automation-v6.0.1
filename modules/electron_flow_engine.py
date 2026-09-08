def infer_electron_flow(rc,changes):
 o=[]
 for c in changes:o.append({"type":"bond_formation" if c["type"]=="formed" else "bond_cleavage" if c["type"]=="broken" else "bond_order_change","source":"electron-rich/reaction-center site","destination":"electrophilic atom/leaving group","evidence":c})
 return o
