import re
from .route_signature import signature_hits

def _txt(row):
    keys = ["Reagent","Catalyst","Solvent","Reaction","Reaction Class","Named Reaction","Starting Material","Product"]
    return " ".join(str(row.get(k, "")) for k in keys).lower()

def _candidate(name, score, evidence):
    return {"class":name, "score":round(float(score), 3), "evidence":evidence}

def classify_reaction(center, row, db):
    text = _txt(row)
    candidates = []
    changes = center.get("bond_changes", []) if isinstance(center, dict) else []
    center_ok = center.get("status") == "ok" if isinstance(center, dict) else False

    # Structure-derived evidence is strongest.
    formed = [x for x in changes if x.get("type") in {"formed", "formed_or_new_atom_bond"}]
    broken = [x for x in changes if x.get("type") == "broken"]
    order = [x for x in changes if x.get("type") == "order_change"]
    if formed and broken:
        candidates.append(_candidate("Substitution / cross-coupling transformation", 0.72, ["validated formed and broken bonds"]))
    elif formed:
        candidates.append(_candidate("Bond-forming reaction", 0.64, ["validated new bond"]));
    elif broken:
        candidates.append(_candidate("Bond cleavage / substitution", 0.62, ["validated bond cleavage"]))
    if order:
        candidates.append(_candidate("Bond-order transformation", 0.67, ["validated bond-order change"]))

    # Reagent/condition patterns for broad reaction families.
    rules = [
        ("Suzuki-Miyaura cross-coupling", 0.86, ["boronic/boronate + Pd"], ("boronic", "boronate"), ("palladium", "pd(")),
        ("Buchwald-Hartwig C-N coupling", 0.82, ["amine + Pd catalyst"], ("amine", "nh2", "amino"), ("palladium", "pd(")),
        ("Sonogashira coupling", 0.86, ["terminal alkyne + Pd/Cu"], ("alkyne", "ethynyl", "terminal alkyne"), ("palladium", "copper", "cui")),
        ("Heck coupling", 0.80, ["alkene + Pd"], ("alkene", "olefin"), ("palladium", "pd(")),
        ("Amide bond formation", 0.82, ["amine + coupling/activation reagent"], ("amine", "amino"), ("edc", "dcc", "hatu", "hatU".lower(), "cdi", "acid chloride")),
        ("Reductive amination", 0.84, ["carbonyl/imine + reducing reagent"], ("reductive amination", "imine"), ("nabh", "borohydride", "cyanoborohydride", "triacetoxyborohydride")),
        ("Catalytic hydrogenation", 0.84, ["H2 + metal catalyst"], ("hydrogen", "h2"), ("pd/c", "platinum", "pt/c", "raney nickel", "nickel")),
        ("Oxidation", 0.76, ["oxidizing reagent"], ("m-cpba", "mcpba", "pcc", "pdc", "dess-martin", "dmp", "tempo", "oxone"), ("",)),
        ("Reduction", 0.76, ["reducing reagent"], ("nabh4", "lialh4", "dibal", "borane", "bh3", "red-al"), ("",)),
        ("Boc deprotection", 0.86, ["acidic Boc removal conditions"], ("tfa", "hcl"), ("boc", "tert-butoxycarbonyl")),
        ("Silyl deprotection", 0.84, ["fluoride / acid silyl removal"], ("tbaf", "fluoride", "hf"), ("tbs", "tbdms", "tips", "silyl")),
    ]
    for name, score, ev, group1, group2 in rules:
        if any(x and x in text for x in group1) and (group2 == ("",) or any(x and x in text for x in group2)):
            candidates.append(_candidate(name, score, ev))

    # The former hard-coded route is only accepted with a complete current-upload signature.
    for sig in signature_hits(text):
        candidates.append(_candidate(sig["name"], 0.90, ["current upload matches all signature groups"] + sig["matched"]))

    # AI-proposed class is retained as evidence, not blindly trusted.
    ai_class = str(row.get("Reaction Class", "") or "").strip()
    if ai_class and ai_class.lower() not in {"requires structure verification", "unclassified transformation", "none"}:
        candidates.append(_candidate(ai_class, 0.68 if not center_ok else 0.78, ["AI route interpretation for current upload"]))

    # Deduplicate by class, keeping strongest score.
    best = {}
    for c in candidates:
        k = c["class"].lower()
        if k not in best or c["score"] > best[k]["score"]:
            best[k] = c
    ranked = sorted(best.values(), key=lambda x:x["score"], reverse=True)

    if not ranked:
        return {"reaction_class":"Requires structure verification", "candidates":[], "confidence":0.15,
                "evidence":["No validated bond-change or sufficiently specific reagent pattern"]}

    top = ranked[0]
    # Avoid overclaiming: without a validated center, require stronger pattern evidence.
    if not center_ok and top["score"] < 0.80:
        return {"reaction_class":"Requires structure verification", "candidates":ranked[:5], "confidence":0.35,
                "evidence":["Candidate reaction found, but molecular-graph confirmation is missing"]}
    return {"reaction_class":top["class"], "candidates":ranked[:5], "confidence":top["score"], "evidence":top.get("evidence", [])}
