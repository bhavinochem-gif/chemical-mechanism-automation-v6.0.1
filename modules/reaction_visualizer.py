"""Streamlit-safe visual mechanism presentation helpers."""

def mechanism_text(step):
    data = {
        1: ("Enolate formation", "NaOtBu removes the hydrogen next to the ketone and generates the ketone enolate."),
        2: ("Aryl–palladium formation", "Palladium undergoes oxidative addition into the aryl C–Br bond."),
        3: ("C–C bond formation", "The ketone alpha-carbon forms a new bond with the 2,3-difluorophenyl group."),
        4: ("Product formation", "Reductive elimination gives the alpha-aryl ketone and regenerates the palladium catalyst."),
    }
    return data.get(step, ("Mechanism step", "Mechanistic transformation."))
