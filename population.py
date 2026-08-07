from dataclasses import dataclass, field
from itertools import product



ETHNICITIES = ["White", "Black", "Hispanic", "Asian", "Other"]
EMPLOYMENT_STATUSES = ["Unemployed", "Salaried", "Business Owner"]
INCOME_TIERS = ["Poor", "Middle Class", "Wealthy"]

ETHNICITY_DIST = {
    "White": 0.58,
    "Black": 0.13,
    "Hispanic": 0.19,
    "Asian": 0.07,
    "Other": 0.03,
}

EMPLOYMENT_DIST = {
    "Unemployed": 0.08,
    "Salaried": 0.72,
    "Business Owner": 0.20,
}

INCOME_DIST = {
    "Poor": 0.25,
    "Middle Class": 0.55,
    "Wealthy": 0.20,
}

EMPLOYMENT_INCOME_CORRELATION = {
    "Unemployed": {"Poor": 2.6, "Middle Class": 0.35, "Wealthy": 0.05},
    "Salaried": {"Poor": 0.55, "Middle Class": 1.45, "Wealthy": 0.75},
    "Business Owner": {"Poor": 0.3, "Middle Class": 0.9, "Wealthy": 2.6},
}


@dataclass
class Segment:
    id: str
    ethnicity: str
    employment_status: str
    income_tier: str
    weight: float  
    count: int = field(default=0)  

    def label(self) -> str:
        return f"{self.employment_status} · {self.income_tier} · {self.ethnicity}"

    def to_dict(self):
        return {
            "id": self.id,
            "ethnicity": self.ethnicity,
            "employment_status": self.employment_status,
            "income_tier": self.income_tier,
            "weight": self.weight,
            "count": self.count,
            "label": self.label(),
        }


def generate_population(population_size: int = 10_000, max_segments: int = 15):
    """
    Build a weighted list of Segment objects covering the top `max_segments`
    highest-weight combinations of ethnicity x employment x income, with
    weights renormalized to sum to 1.0 across the returned segments.
    """
    raw = []
    for ethnicity, employment, income in product(ETHNICITIES, EMPLOYMENT_STATUSES, INCOME_TIERS):
        base = ETHNICITY_DIST[ethnicity] * EMPLOYMENT_DIST[employment] * INCOME_DIST[income]
        corr = EMPLOYMENT_INCOME_CORRELATION[employment][income]
        weight = base * corr
        raw.append((ethnicity, employment, income, weight))

    raw.sort(key=lambda r: r[3], reverse=True)
    top = raw[:max_segments]

    total_weight = sum(r[3] for r in top)
    segments = []
    for i, (ethnicity, employment, income, weight) in enumerate(top):
        normalized_weight = weight / total_weight
        seg = Segment(
            id=f"seg_{i:02d}",
            ethnicity=ethnicity,
            employment_status=employment,
            income_tier=income,
            weight=normalized_weight,
        )
        seg.count = round(normalized_weight * population_size)
        segments.append(seg)

    return segments
