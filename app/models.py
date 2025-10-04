from pydantic import BaseModel
from typing import Optional

class Asteroid(BaseModel):
    id: int
    name: str
    date: str
    diameter_avg: float
    velocity_km_s: float
    miss_distance_km: float
    energy_megatons_TNT: float
    is_potentially_hazardous: bool = False

class AsteroidSummary(BaseModel):
    total_count: int
    dangerous_count: int
    avg_diameter: float
    avg_velocity: float
    avg_energy: float
    closest_approach_km: float
    most_dangerous: Optional[dict]

class EnergyCalculation(BaseModel):
    asteroid_id: int
    name: str
    kinetic_energy_megatons: float
    impact_crater_diameter_km: float
    destruction_radius_km: float
    equivalent_hiroshima_bombs: float

class ImpactAnalysis(BaseModel):
    asteroid: dict
    mass_kg: float
    energy: dict
    impact_effects: dict
    hazard_classification: str