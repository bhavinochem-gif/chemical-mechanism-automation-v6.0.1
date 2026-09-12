def generate_intermediates(reaction_class, flows, row):
    out = []
    for i, flow in enumerate(flows or [], 1):
        out.append({
            "intermediate": i,
            "name": str(flow.get("event", f"Mechanistic stage {i}")).replace("_", " ").title(),
            "description": flow.get("description", "Candidate mechanistic stage inferred from the reaction class."),
            "structure_status": "render when a validated molecular graph can be generated"
        })
    if not out:
        out.append({"intermediate":1, "name":"Structure-specific intermediate", "description":"No mechanistic intermediate is assigned until the reaction class and molecular graph are verified.", "structure_status":"pending verification"})
    return out
