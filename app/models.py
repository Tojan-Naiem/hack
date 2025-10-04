from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
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



class UserAsteroidInput(BaseModel):
    diameter_km: float = Field(..., ge=0.01, le=10.0, description="Asteroid diameter in km (0.01 - 10 km)")
    velocity_km_s: float = Field(..., ge=1.0, le=70.0, description="Velocity in km/s (1 - 70 km/s)")
    mass_kg: Optional[float] = Field(None, description="Mass in kg (auto-calculated if not provided)")
    density_kg_m3: float = Field(2000, ge=1000, le=8000, description="Density in kg/m³")
    entry_angle: float = Field(..., ge=0, le=90, description="Entry angle in degrees (0-90)")
    impact_lat: float = Field(..., ge=-90, le=90, description="Impact latitude")
    impact_lng: float = Field(..., ge=-180, le=180, description="Impact longitude")
    defense_strategy: Optional[str] = Field(None, description="Selected defense strategy")

class UserImpactAnalysis(BaseModel):
    input_data: UserAsteroidInput
    calculated_mass: float
    kinetic_energy_megatons: float
    impact_effects: Dict
    natural_hazards: Dict
    defense_recommendations: List[Dict]
    risk_assessment: Dict