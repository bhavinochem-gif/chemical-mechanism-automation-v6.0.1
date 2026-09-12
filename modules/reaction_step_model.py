from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from .direct_graph_engine import combine_smiles

@dataclass
class ReactionStep:
    step_no: int
    reactants: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    reagents: str = ""
    catalysts: str = ""
    solvents: str = ""
    temperature: str = ""
    time: str = ""
    pressure: str = ""
    atmosphere: str = ""
    yield_text: str = ""
    notes: str = ""

    @property
    def reactant_smiles(self) -> str:
        return combine_smiles(self.reactants)

    @property
    def product_smiles(self) -> str:
        return combine_smiles(self.products)

    @property
    def reaction_smiles(self) -> str:
        return f"{self.reactant_smiles}>>{self.product_smiles}"

    def classifier_row(self) -> Dict[str, Any]:
        return {
            "Step": self.step_no,
            "Starting Material": self.reactant_smiles,
            "Reagents": self.reagents,
            "Catalyst": self.catalysts,
            "Solvent": self.solvents,
            "Conditions": "; ".join(
                x for x in [
                    f"T={self.temperature}" if self.temperature else "",
                    f"time={self.time}" if self.time else "",
                    f"pressure={self.pressure}" if self.pressure else "",
                    f"atmosphere={self.atmosphere}" if self.atmosphere else "",
                ] if x
            ),
            "Product": self.product_smiles,
            "Yield": self.yield_text,
            "Notes": self.notes,
        }

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["reactant_smiles"] = self.reactant_smiles
        d["product_smiles"] = self.product_smiles
        d["reaction_smiles"] = self.reaction_smiles
        return d
