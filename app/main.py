from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, Dict, List, Tuple
from app.database import AsteroidDB
from app.physics import AsteroidPhysics
from app.nasa_client import NASAAPIClient
from app.models import AsteroidSummary, EnergyCalculation
from app.config import Config
from app.location_analyzer import location_analyzer
from app.quantum_analyzer import quantum_analyzer
from app.usgs_analyzer import USGSAnalyzer
from app.quantum_optimizer import quantum_optimizer
import logging
import pandas as pd
import random
from typing import Dict
import hashlib
from math import radians, sin, cos, sqrt, atan2

# =============================
# ASTEROID TYPE CLASSIFIER
# =============================

import random
from typing import Dict

class AsteroidTypeClassifier:
    """Classify asteroids by spectral type with corresponding images"""
    
    ASTEROID_TYPES = {
        "C": {
            "name": "C-type (Carbonaceous)",
            "description": "Dark, carbon-rich asteroids. Most common in outer belt.",
            "albedo_range": (0.03, 0.10),
            "image_url": "/static/images/asteroids/c-type.jpg",
            "characteristics": ["Very dark", "Carbon-rich", "Primitive composition"],
            "composition": "Carbon, water ice, organic compounds"
        },
        "S": {
            "name": "S-type (Silicaceous)",
            "description": "Stony, silicate-rich asteroids. Common in inner belt.",
            "albedo_range": (0.10, 0.22),
            "image_url": "/static/images/asteroids/s-type.jpg",
            "characteristics": ["Moderate brightness", "Silicate minerals", "Rocky"],
            "composition": "Iron, magnesium silicates"
        },
        "M": {
            "name": "M-type (Metallic)",
            "description": "Metal-rich asteroids, possibly exposed cores.",
            "albedo_range": (0.10, 0.18),
            "image_url": "/static/images/asteroids/m-type.jpg",
            "characteristics": ["Metal-rich", "High density", "Nickel-iron"],
            "composition": "Iron, nickel, cobalt"
        },
        "V": {
            "name": "V-type (Vesta-like)",
            "description": "Basaltic composition, similar to asteroid Vesta.",
            "albedo_range": (0.30, 0.50),
            "image_url": "/static/images/asteroids/v-type.jpg",
            "characteristics": ["Very bright", "Basaltic", "Differentiated"],
            "composition": "Basalt, pyroxene"
        },
        "B": {
            "name": "B-type",
            "description": "Similar to C-type but slightly brighter.",
            "albedo_range": (0.04, 0.08),
            "image_url": "/static/images/asteroids/b-type.jpg",
            "characteristics": ["Dark", "Primitive", "Carbon-bearing"],
            "composition": "Carbonaceous materials"
        },
        "Q": {
            "name": "Q-type",
            "description": "Similar to ordinary chondrite meteorites.",
            "albedo_range": (0.15, 0.30),
            "image_url": "/static/images/asteroids/q-type.jpg",
            "characteristics": ["Fresh surface", "Unweathered", "Stony"],
            "composition": "Olivine, pyroxene, metal"
        },
        "K": {
            "name": "K-type",
            "description": "Intermediate between C and S types.",
            "albedo_range": (0.08, 0.15),
            "image_url": "/static/images/asteroids/k-type.jpg",
            "characteristics": ["Moderate reflectance", "Mixed composition"],
            "composition": "Mixed silicates and carbonaceous materials"
        },
        "D": {
            "name": "D-type",
            "description": "Very dark, organic-rich asteroids.",
            "albedo_range": (0.02, 0.05),
            "image_url": "/static/images/asteroids/d-type.jpg",
            "characteristics": ["Extremely dark", "Organic-rich"],
            "composition": "Organic compounds, water ice"
        },
        "P": {
            "name": "P-type",
            "description": "Similar to D-type, very dark and red.",
            "albedo_range": (0.02, 0.06),
            "image_url": "/static/images/asteroids/p-type.jpg",
            "characteristics": ["Very dark", "Reddish", "Primitive"],
            "composition": "Organic materials, silicates"
        },
        "R": {
            "name": "R-type",
            "description": "Rich in olivine, relatively rare.",
            "albedo_range": (0.20, 0.40),
            "image_url": "/static/images/asteroids/r-type.jpg",
            "characteristics": ["Olivine-rich", "Bright", "Uncommon"],
            "composition": "Olivine, pyroxene"
        },
        "T": {
            "name": "T-type",
            "description": "Moderately red, similar to D and P types.",
            "albedo_range": (0.03, 0.07),
            "image_url": "/static/images/asteroids/t-type.jpg",
            "characteristics": ["Dark", "Reddish", "Trojan asteroids"],
            "composition": "Organic materials"
        },
        "A": {
            "name": "A-type",
            "description": "Olivine-dominated, very rare.",
            "albedo_range": (0.15, 0.30),
            "image_url": "/static/images/asteroids/a-type.jpg",
            "characteristics": ["Olivine-rich", "Differentiated", "Extremely rare"],
            "composition": "Pure olivine"
        },
        "L": {
            "name": "L-type",
            "description": "Similar to K-type, moderate albedo.",
            "albedo_range": (0.08, 0.18),
            "image_url": "/static/images/asteroids/l-type.jpg",
            "characteristics": ["Moderate brightness", "Mixed composition"],
            "composition": "Mixed materials"
        },
        "F": {
            "name": "F-type",
            "description": "Similar to B-type, carbon-rich.",
            "albedo_range": (0.03, 0.06),
            "image_url": "/static/images/asteroids/f-type.jpg",
            "characteristics": ["Dark", "Carbonaceous"],
            "composition": "Carbon compounds"
        },
        "G": {
            "name": "G-type",
            "description": "Similar to C-type with UV absorption.",
            "albedo_range": (0.05, 0.09),
            "image_url": "/static/images/asteroids/g-type.jpg",
            "characteristics": ["Dark", "Carbonaceous", "UV absorption"],
            "composition": "Carbonaceous materials with organics"
        },
        "U": {
            "name": "U-type (Unclassified)",
            "description": "Does not fit standard classifications.",
            "albedo_range": (0.0, 1.0),
            "image_url": "/static/images/asteroids/u-type.jpg",
            "characteristics": ["Unusual spectrum", "Rare"],
            "composition": "Variable"
        },
        "UNKNOWN": {
            "name": "Unknown/Unclassified",
            "description": "Spectral type not determined.",
            "albedo_range": (0.0, 1.0),
            "image_url": "/static/images/asteroids/unknown.jpg",
            "characteristics": ["Classification pending", "Insufficient data"],
            "composition": "Unknown"
        }
    }
    
    def classify_by_id(self, asteroid_id: int) -> str:
        """Classify asteroid using deterministic pseudo-random selection"""
        random.seed(asteroid_id)
        
        type_distribution = [
            ("S", 45), ("C", 30), ("M", 5), ("Q", 5),
            ("V", 3), ("B", 2), ("K", 2), ("D", 2),
            ("P", 2), ("R", 1), ("T", 1), ("A", 1), ("L", 1)
        ]
        
        total = sum(weight for _, weight in type_distribution)
        rand_val = random.randint(1, total)
        
        cumulative = 0
        for type_code, weight in type_distribution:
            cumulative += weight
            if rand_val <= cumulative:
                random.seed()
                return type_code
        
        random.seed()
        return "UNKNOWN"
    
    def get_type_info(self, type_code: str) -> Dict:
        """Get complete information for an asteroid type"""
        return self.ASTEROID_TYPES.get(type_code, self.ASTEROID_TYPES["UNKNOWN"])
    
    def classify_asteroid(self, asteroid_id: int) -> Dict:
        """Classify asteroid and return full information"""
        type_code = self.classify_by_id(asteroid_id)
        type_info = self.get_type_info(type_code)
        
        return {
            "type_code": type_code,
            "type_name": type_info["name"],
            "description": type_info["description"],
            "image_url": type_info["image_url"],
            "characteristics": type_info["characteristics"],
            "composition": type_info["composition"],
            "classification_method": "statistical",
            "confidence": "low"
        }
from datetime import datetime, timedelta
import math

# =============================
# IMPACT DATE CALCULATOR
# =============================

class ImpactDateCalculator:
    """Calculate potential impact dates based on orbital parameters"""
    
    def calculate_impact_date(self, asteroid_data: Dict) -> Dict:
        """
        Calculate potential impact date based on current distance and velocity
        """
        try:
            # Extract basic parameters
            miss_distance_km = asteroid_data['miss_distance_km']
            velocity_km_s = asteroid_data['velocity_km_s']
            close_approach_date = asteroid_data.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            # Convert to AU for astronomical calculations
            distance_au = miss_distance_km / 149597870.7  # 1 AU in km
            
            # Calculate time to impact based on different scenarios
            impact_analysis = self._calculate_impact_scenarios(distance_au, velocity_km_s, close_approach_date)
            
            return impact_analysis
            
        except Exception as e:
            logger.error(f"Error calculating impact date: {e}")
            return self._get_default_impact_analysis()

    def _calculate_impact_scenarios(self, distance_au: float, velocity_km_s: float, approach_date: str) -> Dict:
        """Calculate different impact scenarios"""
        
        # Convert approach date to datetime
        try:
            approach_dt = datetime.strptime(approach_date, '%Y-%m-%d')
        except:
            approach_dt = datetime.now()

        # Scenario 1: Direct impact (current trajectory)
        direct_impact = self._calculate_direct_impact(distance_au, velocity_km_s, approach_dt)
        
        # Scenario 2: Gravitational perturbation
        perturbed_impact = self._calculate_perturbed_impact(distance_au, velocity_km_s, approach_dt)
        
        # Scenario 3: Orbital resonance (future approaches)
        resonant_impact = self._calculate_resonant_impact(distance_au, velocity_km_s, approach_dt)
        
        # Determine most likely scenario
        most_likely = self._determine_most_likely_scenario(direct_impact, perturbed_impact, resonant_impact, distance_au)
        
        return {
            "current_approach_date": approach_date,
            "distance_au": round(distance_au, 6),
            "velocity_km_s": velocity_km_s,
            "scenarios": {
                "direct_impact": direct_impact,
                "gravitational_perturbation": perturbed_impact,
                "orbital_resonance": resonant_impact
            },
            "most_likely_scenario": most_likely,
            "impact_probability": self._calculate_impact_probability(distance_au),
            "monitoring_recommendation": self._get_monitoring_recommendation(distance_au)
        }

    def _calculate_direct_impact(self, distance_au: float, velocity_km_s: float, approach_dt: datetime) -> Dict:
        """Calculate direct impact scenario"""
        if distance_au <= 0.01:  # Within 0.01 AU - immediate threat
            days_to_impact = (distance_au * 149597870.7) / (velocity_km_s * 86400)  # km / (km/day)
            impact_date = approach_dt + timedelta(days=days_to_impact)
            confidence = "HIGH"
        else:
            # For more distant objects, estimate based on orbital mechanics
            orbital_period_days = self._estimate_orbital_period(distance_au)
            impact_date = approach_dt + timedelta(days=orbital_period_days)
            confidence = "LOW"
            
        return {
            "type": "DIRECT_COLLISION",
            "estimated_impact_date": impact_date.strftime('%Y-%m-%d'),
            "days_until_impact": max(0, (impact_date - datetime.now()).days),
            "confidence": confidence,
            "description": "Current trajectory leads to direct impact",
            "probability": "0.1%-1%" if distance_au <= 0.01 else "<0.1%"
        }

    def _calculate_perturbed_impact(self, distance_au: float, velocity_km_s: float, approach_dt: datetime) -> Dict:
        """Calculate impact after gravitational perturbations"""
        # Estimate effect of planetary perturbations
        perturbation_factor = self._calculate_perturbation_factor(distance_au)
        
        if perturbation_factor > 0.1:  # Significant perturbation possible
            # Perturbations typically affect orbits over multiple passes
            orbital_period_days = self._estimate_orbital_period(distance_au)
            impact_date = approach_dt + timedelta(days=orbital_period_days * 2)
            confidence = "MEDIUM"
        else:
            impact_date = approach_dt + timedelta(days=365 * 10)  # 10 years default
            confidence = "LOW"
            
        return {
            "type": "GRAVITATIONAL_PERTURBATION",
            "estimated_impact_date": impact_date.strftime('%Y-%m-%d'),
            "days_until_impact": max(0, (impact_date - datetime.now()).days),
            "confidence": confidence,
            "description": "Orbital changes due to planetary gravity may lead to future impact",
            "probability": "0.01%-0.1%",
            "perturbation_strength": self._classify_perturbation_strength(perturbation_factor)
        }

    def _calculate_resonant_impact(self, distance_au: float, velocity_km_s: float, approach_dt: datetime) -> Dict:
        """Calculate impact due to orbital resonance"""
        # Check for orbital resonance with Earth (common periods)
        resonance_periods = self._find_orbital_resonances(distance_au)
        
        if resonance_periods:
            # Use the strongest resonance
            strongest_resonance = resonance_periods[0]
            impact_date = approach_dt + timedelta(days=strongest_resonance['days_until_resonance'])
            confidence = "MEDIUM"
        else:
            impact_date = approach_dt + timedelta(days=365 * 20)  # 20 years default
            confidence = "LOW"
            
        return {
            "type": "ORBITAL_RESONANCE",
            "estimated_impact_date": impact_date.strftime('%Y-%m-%d'),
            "days_until_impact": max(0, (impact_date - datetime.now()).days),
            "confidence": confidence,
            "description": "Orbital resonance with Earth may lead to repeated close approaches",
            "probability": "0.001%-0.01%",
            "resonance_strength": "STRONG" if resonance_periods else "WEAK"
        }

    def _estimate_orbital_period(self, distance_au: float) -> float:
        """Estimate orbital period in days using Kepler's third law"""
        # Simplified estimation for near-Earth objects
        if distance_au <= 0.1:
            return 365  # ~1 year for very close objects
        elif distance_au <= 1.0:
            return 365 * 2  # ~2 years
        else:
            return 365 * 5  # ~5 years for more distant objects

    def _calculate_perturbation_factor(self, distance_au: float) -> float:
        """Calculate planetary perturbation factor"""
        # Planets have stronger effects at certain distances
        if distance_au <= 0.1:
            return 0.8  # Strong perturbations from Earth/Moon
        elif distance_au <= 1.0:
            return 0.5  # Moderate perturbations from Venus/Mars
        elif distance_au <= 5.0:
            return 0.3  # Weaker perturbations from Jupiter
        else:
            return 0.1  # Minimal perturbations

    def _find_orbital_resonances(self, distance_au: float) -> List[Dict]:
        """Find orbital resonances with Earth"""
        resonances = []
        
        # Common orbital resonances with Earth (in Earth years)
        common_resonances = [
            (1, 1),    # 1:1 resonance
            (2, 1),    # 2:1 resonance  
            (3, 2),    # 3:2 resonance
            (4, 3),    # 4:3 resonance
        ]
        
        for earth_years, asteroid_years in common_resonances:
            resonance_strength = self._calculate_resonance_strength(distance_au, earth_years, asteroid_years)
            if resonance_strength > 0.7:  # Strong resonance
                resonances.append({
                    'ratio': f"{asteroid_years}:{earth_years}",
                    'strength': resonance_strength,
                    'days_until_resonance': earth_years * 365,
                    'description': f"{asteroid_years}:{earth_years} orbital resonance with Earth"
                })
        
        return sorted(resonances, key=lambda x: x['strength'], reverse=True)

    def _calculate_resonance_strength(self, distance_au: float, earth_years: int, asteroid_years: int) -> float:
        """Calculate strength of orbital resonance"""
        expected_distance = (earth_years / asteroid_years) ** (2/3)  # Kepler's third law
        distance_diff = abs(distance_au - expected_distance)
        
        if distance_diff <= 0.05:
            return 0.9
        elif distance_diff <= 0.1:
            return 0.7
        elif distance_diff <= 0.2:
            return 0.5
        else:
            return 0.0

    def _determine_most_likely_scenario(self, direct: Dict, perturbed: Dict, resonant: Dict, distance_au: float) -> Dict:
        """Determine the most likely impact scenario"""
        scenarios = [direct, perturbed, resonant]
        
        # Weight scenarios based on distance
        if distance_au <= 0.01:
            return direct  # Immediate threat
        elif distance_au <= 0.05:
            return perturbed  # Gravitational effects dominate
        else:
            return resonant  # Long-term orbital dynamics

    def _calculate_impact_probability(self, distance_au: float) -> str:
        """Calculate impact probability based on distance"""
        if distance_au <= 0.001:
            return "1-10%"
        elif distance_au <= 0.01:
            return "0.1-1%"
        elif distance_au <= 0.05:
            return "0.01-0.1%"
        else:
            return "<0.01%"

    def _classify_perturbation_strength(self, factor: float) -> str:
        """Classify perturbation strength"""
        if factor > 0.7:
            return "VERY_STRONG"
        elif factor > 0.5:
            return "STRONG"
        elif factor > 0.3:
            return "MODERATE"
        else:
            return "WEAK"

    def _get_monitoring_recommendation(self, distance_au: float) -> str:
        """Get monitoring recommendation based on distance"""
        if distance_au <= 0.01:
            return "CONTINUOUS_MONITORING"
        elif distance_au <= 0.05:
            return "ENHANCED_MONITORING"
        else:
            return "STANDARD_MONITORING"

    def _get_default_impact_analysis(self) -> Dict:
        """Get default impact analysis when calculation fails"""
        return {
            "current_approach_date": datetime.now().strftime('%Y-%m-%d'),
            "distance_au": 0.0,
            "velocity_km_s": 0.0,
            "scenarios": {
                "direct_impact": {
                    "type": "UNKNOWN",
                    "estimated_impact_date": "Unknown",
                    "days_until_impact": 0,
                    "confidence": "LOW",
                    "description": "Insufficient data for calculation",
                    "probability": "Unknown"
                }
            },
            "most_likely_scenario": "UNKNOWN",
            "impact_probability": "Unknown",
            "monitoring_recommendation": "DATA_REQUIRED"
        }

# Initialize impact date calculator
impact_calculator = ImpactDateCalculator()

# =============================
# UPDATED API ENDPOINTS WITH IMPACT DATES
# =============================

@app.get("/asteroids/{asteroid_id}/impact-date")
async def get_asteroid_impact_date(asteroid_id: int):
    """Get calculated impact dates for specific asteroid"""
    asteroid = db.get_asteroid_by_id(asteroid_id)
    
    if not asteroid:
        raise HTTPException(status_code=404, detail="Asteroid not found")
    
    # Calculate impact date scenarios
    impact_analysis = impact_calculator.calculate_impact_date(asteroid)
    
    return {
        "asteroid_id": asteroid_id,
        "name": asteroid['name'],
        "impact_date_analysis": impact_analysis,
        "next_observation_window": calculate_next_observation_window(asteroid),
        "defense_timeline": calculate_defense_timeline(impact_analysis)
    }

@app.get("/asteroids/threats/with-dates")
async def get_threats_with_dates():
    """Get all threats with calculated impact dates"""
    threats = validate_and_identify_threats()
    
    threats_with_dates = []
    for threat in threats:
        asteroid = db.get_asteroid_by_id(threat['id'])
        if asteroid:
            impact_analysis = impact_calculator.calculate_impact_date(asteroid)
            threat['impact_analysis'] = impact_analysis
            threats_with_dates.append(threat)
    
    return {
        "count": len(threats_with_dates),
        "threats": threats_with_dates,
        "timeframe_analysis": analyze_impact_timeframes(threats_with_dates)
    }

def calculate_next_observation_window(asteroid: Dict) -> Dict:
    """Calculate next optimal observation window"""
    distance_au = asteroid['miss_distance_km'] / 149597870.7
    
    if distance_au <= 0.01:
        return {
            "next_window": "IMMEDIATE",
            "recommended_observatories": ["Space-based", "All ground stations"],
            "observation_priority": "HIGHEST",
            "frequency": "Continuous"
        }
    elif distance_au <= 0.05:
        return {
            "next_window": "Within 7 days",
            "recommended_observatories": ["Major observatories", "Radar systems"],
            "observation_priority": "HIGH",
            "frequency": "Daily"
        }
    else:
        return {
            "next_window": "Within 30 days",
            "recommended_observatories": ["Standard monitoring networks"],
            "observation_priority": "MEDIUM",
            "frequency": "Weekly"
        }

def calculate_defense_timeline(impact_analysis: Dict) -> Dict:
    """Calculate defense mission timeline based on impact date"""
    most_likely = impact_analysis['most_likely_scenario']
    days_until_impact = most_likely.get('days_until_impact', 0)
    
    if days_until_impact <= 30:
        return {
            "feasibility": "LIMITED",
            "recommended_strategy": "NUCLEAR_DEFLECTION",
            "mission_timeline": "EMERGENCY_RESPONSE",
            "preparation_time": "Days to weeks",
            "success_probability": "30-50%"
        }
    elif days_until_impact <= 365:
        return {
            "feasibility": "MODERATE",
            "recommended_strategy": "KINETIC_IMPACTOR",
            "mission_timeline": "ACCELERATED",
            "preparation_time": "3-12 months",
            "success_probability": "60-80%"
        }
    elif days_until_impact <= 3650:  # 10 years
        return {
            "feasibility": "HIGH",
            "recommended_strategy": "GRAVITY_TRACTOR",
            "mission_timeline": "STANDARD",
            "preparation_time": "2-8 years",
            "success_probability": "80-95%"
        }
    else:
        return {
            "feasibility": "VERY_HIGH",
            "recommended_strategy": "Multiple approaches",
            "mission_timeline": "LONG_TERM",
            "preparation_time": "5-15 years",
            "success_probability": "90-99%"
        }

def analyze_impact_timeframes(threats: List[Dict]) -> Dict:
    """Analyze impact timeframes across all threats"""
    timeframes = {
        "immediate": [],      # 0-30 days
        "short_term": [],     # 1-12 months  
        "medium_term": [],    # 1-10 years
        "long_term": []       # 10+ years
    }
    
    for threat in threats:
        impact_analysis = threat.get('impact_analysis', {})
        most_likely = impact_analysis.get('most_likely_scenario', {})
        days_until = most_likely.get('days_until_impact', 9999)
        
        if days_until <= 30:
            timeframes["immediate"].append(threat)
        elif days_until <= 365:
            timeframes["short_term"].append(threat)
        elif days_until <= 3650:
            timeframes["medium_term"].append(threat)
        else:
            timeframes["long_term"].append(threat)
    
    return {
        "immediate_threats": len(timeframes["immediate"]),
        "short_term_threats": len(timeframes["short_term"]),
        "medium_term_threats": len(timeframes["medium_term"]),
        "long_term_threats": len(timeframes["long_term"]),
        "most_urgent": timeframes["immediate"][:3] if timeframes["immediate"] else [],
        "global_risk_timeline": {
            "current_risk": "HIGH" if timeframes["immediate"] else "MEDIUM" if timeframes["short_term"] else "LOW",
            "peak_risk_period": "Immediate" if timeframes["immediate"] else "Short-term" if timeframes["short_term"] else "Long-term"
        }
    }

# =============================
# UPDATE EXISTING ENDPOINTS WITH IMPACT DATES
# =============================

@app.get("/asteroids/impact/{asteroid_id}")
async def get_impact_analysis_with_dates(asteroid_id: int):
    """Enhanced impact analysis with date calculations"""
    asteroid = db.get_asteroid_by_id(asteroid_id)
    
    if not asteroid:
        raise HTTPException(status_code=404, detail="Asteroid not found")
    
    distance_au = asteroid['miss_distance_km'] / 149597870.7
    
    # Calculate impact dates
    impact_date_analysis = impact_calculator.calculate_impact_date(asteroid)
    
    if distance_au > 0.05:
        return {
            "asteroid": asteroid['name'],
            "distance_au": round(distance_au, 4),
            "threat_level": "LOW",
            "impact_date_analysis": impact_date_analysis,
            "message": "This asteroid poses no immediate threat",
            "analysis_skipped": True
        }
    
    # Continue with existing impact analysis...
    impact_lat, impact_lng = generate_impact_site(asteroid_id)
    seismic_analysis = usgs_analyzer.calculate_seismic_risk(impact_lat, impact_lng)
    
    mass = physics.calculate_mass(asteroid['diameter_avg'])
    energy = physics.calculate_kinetic_energy(mass, asteroid['velocity_km_s'])
    impact_effects = physics.calculate_impact_effects(energy['energy_megatons_TNT'])
    
    impact_analysis = location_analyzer.analyze_impact({
        **asteroid,
        "impact_lat": impact_lat,
        "impact_lng": impact_lng
    })
    
    return {
        "asteroid": asteroid['name'],
        "threat_assessment": {
            "distance_au": round(distance_au, 6),
            "threat_level": "CRITICAL" if distance_au <= 0.01 else "HIGH",
            "is_potentially_hazardous": True
        },
        "impact_timing": impact_date_analysis,
        "impact_prediction": {
            "estimated_impact_date": impact_date_analysis['most_likely_scenario']['estimated_impact_date'],
            "days_until_impact": impact_date_analysis['most_likely_scenario']['days_until_impact'],
            "location": {
                "coordinates": [impact_lat, impact_lng],
                "type": impact_analysis['impact_location']['type'],
                "city_region": impact_analysis['impact_location'].get('description', 'Unknown')
            }
        },
        "impact_effects": {
            "energy_megatons": round(energy['energy_megatons_TNT'], 2),
            "crater_diameter_km": round(impact_effects['crater_diameter_km'], 2),
            "destruction_radius_km": round(impact_effects['destruction_radius_km'], 2),
            "estimated_casualties": impact_analysis['impact_analysis']['estimated_deaths']
        },
        "seismic_enhancement": seismic_analysis,
        "defense_timeline": calculate_defense_timeline(impact_date_analysis),
        "emergency_recommendations": generate_emergency_recommendations(asteroid, distance_au)
    }

# Update the main endpoint to include impact dates
@app.get("/")
async def root_with_dates():
    """Enhanced API Information with Impact Dates"""
    threats = validate_and_identify_threats()
    critical_threats = [t for t in threats if t['threat_level'] == "CRITICAL"]
    
    # Add impact date analysis to critical threats
    enhanced_threats = []
    for threat in critical_threats[:3]:  # Limit to first 3 for performance
        asteroid = db.get_asteroid_by_id(threat['id'])
        if asteroid:
            impact_analysis = impact_calculator.calculate_impact_date(asteroid)
            threat['impact_date'] = impact_analysis['most_likely_scenario']['estimated_impact_date']
            threat['days_until_impact'] = impact_analysis['most_likely_scenario']['days_until_impact']
            enhanced_threats.append(threat)
    
    return {
        "name": "NASA NEO Threat Assessment System",
        "version": "4.1.0",  # Updated version
        "feature": "Impact Date Calculations Added",
        "threat_status": {
            "total_asteroids": len(db.get_all_asteroids()),
            "potential_threats": len(threats),
            "critical_threats": len(critical_threats),
            "global_risk_level": "HIGH" if critical_threats else "MEDIUM" if threats else "LOW"
        },
        "recent_threats": enhanced_threats,
        "endpoints": {
            "immediate_threats": "/asteroids/threats/immediate",
            "threats_with_dates": "/asteroids/threats/with-dates",
            "impact_analysis": "/asteroids/impact/{id}",
            "impact_dates": "/asteroids/{id}/impact-date",
            "natural_hazards": "/asteroids/{id}/natural-hazards",
            "seismic_analysis": "/usgs/earthquakes/nearby"
        }
    }
class AsteroidDefenseStrategies:
    """Defense strategies for different asteroid types and threat levels"""
    
    DEFENSE_METHODS = {
        "KINETIC_IMPACTOR": {
            "name": "Kinetic Impactor",
            "description": "Spacecraft impacts asteroid to change its velocity",
            "effectiveness": "High for small to medium asteroids",
            "development_level": "Tested (DART Mission)",
            "time_required": "2-10 years",
            "cost": "Medium",
            "best_for": ["S-type", "M-type", "Q-type"]
        },
        "GRAVITY_TRACTOR": {
            "name": "Gravity Tractor", 
            "description": "Spacecraft flies near asteroid, using gravity to slowly alter course",
            "effectiveness": "Medium for all sizes",
            "development_level": "Concept",
            "time_required": "10-20 years",
            "cost": "High",
            "best_for": ["All types"]
        },
        "NUCLEAR_DEFLECTION": {
            "name": "Nuclear Deflection",
            "description": "Nuclear explosion near asteroid surface alters trajectory",
            "effectiveness": "Very high for large asteroids",
            "development_level": "Theoretical",
            "time_required": "5-15 years", 
            "cost": "Very high",
            "best_for": ["C-type", "D-type", "P-type"]
        },
        "LASER_ABLATION": {
            "name": "Laser Ablation",
            "description": "High-power lasers vaporize surface material, creating thrust",
            "effectiveness": "Medium for small asteroids",
            "development_level": "Experimental",
            "time_required": "15-25 years",
            "cost": "Very high",
            "best_for": ["S-type", "M-type"]
        },
        "ION_BEAM_SHEPHERD": {
            "name": "Ion Beam Shepherd",
            "description": "Ion thrusters directed at asteroid surface for gentle push",
            "effectiveness": "Low to medium",
            "development_level": "Concept", 
            "time_required": "20-30 years",
            "cost": "Extreme",
            "best_for": ["Small asteroids"]
        },
        "PAINT_OR_COVER": {
            "name": "Surface Albedo Modification",
            "description": "Change asteroid's reflectivity to alter solar radiation pressure",
            "effectiveness": "Very low",
            "development_level": "Theoretical",
            "time_required": "10-20 years",
            "cost": "Low",
            "best_for": ["Small, rotating asteroids"]
        }
    }
    
    def get_defense_strategies(self, asteroid_data: Dict, impact_analysis: Dict) -> List[Dict]:
        """Get appropriate defense strategies based on asteroid properties and threat level"""
        
        diameter = asteroid_data['diameter_avg']
        spectral_type = asteroid_data.get('spectral_type', 'UNKNOWN')
        threat_level = impact_analysis.get('threat_level', 'LOW')
        time_until_impact = self.estimate_time_until_impact(asteroid_data)
        
        strategies = []
        
        # KINETIC_IMPACTOR - Good for most scenarios
        if diameter < 500 and time_until_impact > 2:
            strategies.append(self._enhance_strategy(
                self.DEFENSE_METHODS["KINETIC_IMPACTOR"],
                asteroid_data,
                impact_analysis
            ))
        
        # GRAVITY_TRACTOR - For longer timelines
        if diameter < 1000 and time_until_impact > 10:
            strategies.append(self._enhance_strategy(
                self.DEFENSE_METHODS["GRAVITY_TRACTOR"],
                asteroid_data, 
                impact_analysis
            ))
        
        # NUCLEAR_DEFLECTION - For high-threat, short timeline scenarios
        if (threat_level in ["HIGH", "VERY_HIGH", "EXTREME"] and 
            time_until_impact < 5 and diameter > 200):
            strategies.append(self._enhance_strategy(
                self.DEFENSE_METHODS["NUCLEAR_DEFLECTION"],
                asteroid_data,
                impact_analysis
            ))
        
        # LASER_ABLATION - For specific asteroid types
        if spectral_type in ["S-type", "M-type"] and diameter < 200:
            strategies.append(self._enhance_strategy(
                self.DEFENSE_METHODS["LASER_ABLATION"],
                asteroid_data,
                impact_analysis
            ))
        
        # Sort by effectiveness and feasibility
        strategies.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return strategies[:3]  # Return top 3 strategies
    
    def _enhance_strategy(self, strategy: Dict, asteroid: Dict, impact_analysis: Dict) -> Dict:
        """Add asteroid-specific details to defense strategy"""
        
        diameter = asteroid['diameter_avg']
        threat_level = impact_analysis.get('threat_level', 'LOW')
        
        # Calculate success probability
        if diameter < 100:
            success_prob = "80-95%"
        elif diameter < 500:
            success_prob = "60-80%" 
        else:
            success_prob = "30-60%"
        
        # Calculate priority score
        priority_factors = {
            "LOW": 1, "MEDIUM": 2, "HIGH": 3, "VERY_HIGH": 4, "EXTREME": 5
        }
        priority_score = priority_factors.get(threat_level, 1)
        
        return {
            **strategy,
            "success_probability": success_prob,
            "priority_score": priority_score,
            "recommended_mission_name": self._generate_mission_name(asteroid['name']),
            "required_technology_level": self._assess_technology_level(strategy['development_level']),
            "international_cooperation_required": diameter > 200
        }
    
    def estimate_time_until_impact(self, asteroid: Dict) -> float:
        """Estimate time until potential impact in years"""
        distance_au = asteroid['miss_distance_km'] / 149597870.7
        
        if distance_au <= 0.01:
            return 0.1  # Months
        elif distance_au <= 0.05:
            return 1    # 1 year
        elif distance_au <= 0.1:
            return 5    # 5 years
        else:
            return 10   # 10+ years
    
    def _generate_mission_name(self, asteroid_name: str) -> str:
        """Generate a mission name based on asteroid name"""
        base_name = asteroid_name.replace('(', '').replace(')', '').replace(' ', '')
        return f"SHIELD_{base_name}"
    
    def _assess_technology_level(self, development_level: str) -> str:
        """Assess technology readiness level"""
        levels = {
            "Tested": "READY",
            "Experimental": "NEAR_TERM", 
            "Concept": "MID_TERM",
            "Theoretical": "FUTURE"
        }
        return levels.get(development_level, "FUTURE")

# Initialize defense strategies
defense_strategies = AsteroidDefenseStrategies()
# Initialize classifier
asteroid_classifier = AsteroidTypeClassifier()
# Initialize components
db = AsteroidDB()
physics = AsteroidPhysics()
nasa_client = NASAAPIClient()
usgs_analyzer = USGSAnalyzer()
asteroid_classifier = AsteroidTypeClassifier()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: Load and validate data"""
    print("🚀 Starting NASA NEO + USGS Backend...")
    
    try:
        # Load existing files
        if Config.ASTEROIDS_SUMMARY_CSV.exists():
            print(f"📂 Loading {Config.ASTEROIDS_SUMMARY_CSV}")
            db.load_from_csv(Config.ASTEROIDS_SUMMARY_CSV)
            
            # Validate and identify real threats
            threats = validate_and_identify_threats()
            if threats:
                print(f"🚨 IDENTIFIED {len(threats)} POTENTIAL THREATS!")
                for threat in threats[:5]:
                    print(f"   - {threat['name']}: {threat['distance_au']} AU")
        
        print("🌋 USGS Seismic Data: Ready (Live API)")
        print("✅ Threat assessment completed")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
    
    yield
    
    print("🛑 Shutting down...")

app = FastAPI(
    title="NASA NEO Threat Assessment API",
    description="Real asteroid threat detection and analysis",
    version="4.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_and_identify_threats():
    """Identify real asteroid threats from data"""
    df = db.get_all_asteroids()
    
    if df.empty:
        return []
    
    threats = []
    
    for idx, asteroid in df.iterrows():
        distance_au = asteroid['miss_distance_km'] / 149597870.7
        
        # CRITICAL: Objects within 0.05 AU are potentially hazardous
        if distance_au <= 0.05:
            threat_level = "CRITICAL" if distance_au <= 0.01 else "HIGH"
            
            threats.append({
                'id': asteroid['id'],
                'name': asteroid['name'],
                'date': asteroid['date'],
                'diameter_km': asteroid['diameter_avg'],
                'velocity_km_s': asteroid['velocity_km_s'],
                'distance_km': asteroid['miss_distance_km'],
                'distance_au': round(distance_au, 6),
                'energy_mt': asteroid['energy_megatons_TNT'],
                'threat_level': threat_level,
                'is_immediate_threat': distance_au <= 0.01
            })
    
    # Sort by threat level (closest first)
    threats.sort(key=lambda x: x['distance_au'])
    return threats

# =============================
# HELPER FUNCTIONS
# =============================

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in km"""
    R = 6371
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def generate_impact_site(asteroid_id: int) -> Tuple[float, float]:
    """Generate realistic impact site based on asteroid ID"""
    impact_sites = [
        (40.7128, -74.0060),   # New York
        (35.6762, 139.6503),   # Tokyo
        (25.0, 55.0),          # Dubai
        (-33.8688, 151.2093),  # Sydney
        (0, 0),                # Atlantic Ocean
        (-45.0, -170.0),       # Pacific Ocean
        (48.8566, 2.3522),     # Paris
    ]
    return impact_sites[asteroid_id % len(impact_sites)]

def calculate_impact_radius(energy_mt: float) -> float:
    """Calculate impact radius based on energy"""
    if energy_mt < 1:
        return 5
    elif energy_mt < 10:
        return 15
    elif energy_mt < 100:
        return 30
    else:
        return 50

def classify_impact_energy(energy_mt: float) -> str:
    """Classify impact energy"""
    if energy_mt < 0.01:
        return "Very Small"
    elif energy_mt < 1:
        return "Small"
    elif energy_mt < 10:
        return "Medium"
    elif energy_mt < 100:
        return "Large"
    elif energy_mt < 1000:
        return "Very Large"
    else:
        return "Extinction Level"

def calculate_risk_score(asteroid, distance_au: float) -> float:
    """Calculate comprehensive risk score (0-1)"""
    distance_factor = max(0, 1 - (distance_au / 0.05))
    size_factor = min(1, asteroid['diameter_avg'] / 1000)
    energy_factor = min(1, asteroid['energy_megatons_TNT'] / 10000)
    
    risk_score = (distance_factor * 0.5) + (size_factor * 0.3) + (energy_factor * 0.2)
    return round(risk_score, 3)

def generate_emergency_recommendations(asteroid, distance_au):
    """Generate emergency response recommendations"""
    recommendations = []
    
    if distance_au <= 0.01:
        recommendations.extend([
            "🚨 IMMEDIATE EVACUATION of predicted impact zone",
            "🏥 Activate emergency medical response",
            "📡 Continuous tracking and trajectory monitoring",
            "🌍 International cooperation required"
        ])
    elif distance_au <= 0.05:
        recommendations.extend([
            "⚠️ Close monitoring of trajectory changes",
            "🏗️ Review building codes in risk areas",
            "📊 Update risk assessment every 6 hours",
            "🔍 Enhanced telescope observation"
        ])
    
    if asteroid['energy_megatons_TNT'] > 100:
        recommendations.append("💥 High-energy impact - prepare for widespread effects")
    
    if asteroid['diameter_avg'] > 100:
        recommendations.append("🌋 Large object - potential global effects")
    
    return recommendations if recommendations else ["✅ Continue standard monitoring"]

# =============================
# NATURAL HAZARDS FUNCTIONS
# =============================

def get_nearby_volcanoes(lat: float, lng: float, radius_km: float = 500):
    """Get nearby volcanoes"""
    try:
        mock_volcanoes = [
            {
                "name": "Mount St. Helens",
                "distance_km": round(calculate_distance(lat, lng, 46.2, -122.2), 1),
                "elevation_m": 2549,
                "last_eruption": "2008",
                "status": "Active",
                "volcano_type": "Stratovolcano",
                "risk_level": "High"
            }
        ]
        
        volcanoes_in_range = [v for v in mock_volcanoes if v['distance_km'] <= radius_km]
        
        return {
            "count": len(volcanoes_in_range),
            "search_radius_km": radius_km,
            "active_volcanoes_count": len([v for v in volcanoes_in_range if v['status'] == 'Active']),
            "volcanoes": volcanoes_in_range,
            "closest_volcano": min(volcanoes_in_range, key=lambda x: x['distance_km']) if volcanoes_in_range else None
        }
        
    except Exception as e:
        return {
            "count": 0,
            "error": f"Volcano data unavailable: {str(e)}",
            "volcanoes": []
        }

def assess_volcanic_trigger_risk(lat: float, lng: float, asteroid: Dict):
    """Assess volcanic eruption trigger risk"""
    energy = asteroid['energy_megatons_TNT']
    volcanoes_data = get_nearby_volcanoes(lat, lng, radius_km=300)
    active_volcanoes_count = volcanoes_data.get('active_volcanoes_count', 0)
    
    if energy > 1000 and active_volcanoes_count > 0:
        risk_level = "VERY_HIGH"
        probability = "40-60%"
    elif energy > 500 and active_volcanoes_count > 0:
        risk_level = "HIGH"
        probability = "25-40%"
    elif energy > 100 and active_volcanoes_count > 0:
        risk_level = "MEDIUM"
        probability = "15-25%"
    elif energy > 50 and active_volcanoes_count > 0:
        risk_level = "LOW_MEDIUM"
        probability = "5-15%"
    else:
        risk_level = "LOW"
        probability = "<5%"
    
    return {
        "risk_level": risk_level,
        "probability": probability,
        "active_volcanoes_nearby": active_volcanoes_count,
        "recommendation": "Monitor volcanic activity" if active_volcanoes_count > 0 else "No immediate concern"
    }

def estimate_ash_fall(lat: float, lng: float, asteroid: Dict):
    """Estimate ash fall"""
    energy = asteroid['energy_megatons_TNT']
    volcanoes_data = get_nearby_volcanoes(lat, lng, radius_km=500)
    
    if volcanoes_data['active_volcanoes_count'] == 0:
        return {
            "ash_fall_expected": False,
            "reason": "No active volcanoes in the area"
        }
    
    return {
        "ash_fall_expected": True,
        "risk_level": "HIGH" if energy > 500 else "MEDIUM" if energy > 100 else "LOW",
        "affected_radius_km": 200,
        "health_warning": "Wear masks outdoors"
    }

def calculate_tsunami_risk(lat: float, lng: float, asteroid: Dict):
    """Calculate ACCURATE tsunami risk"""
    is_ocean = location_analyzer.is_ocean_location(lat, lng)
    energy = asteroid['energy_megatons_TNT']
    
    if not is_ocean:
        return {
            "tsunami_expected": False,
            "risk_level": "NONE",
            "reason": "Land impact - no tsunami generation",
            "coastal_warnings_needed": False,
            "evacuation_recommended": False
        }
    
    # Ocean impact - calculate tsunami potential
    distance_to_coast = calculate_distance_to_coast(lat, lng)
    
    if energy > 100:
        risk_level = "EXTREME"
        tsunami_expected = True
        evacuation = True
        warning = f"Catastrophic tsunami - {distance_to_coast}km to nearest coast"
    elif energy > 10:
        risk_level = "HIGH"
        tsunami_expected = True
        evacuation = True
        warning = f"Major tsunami possible - coastal areas at risk"
    elif energy > 1:
        risk_level = "MEDIUM"
        tsunami_expected = True
        evacuation = distance_to_coast < 500
        warning = f"Moderate tsunami - monitor coastal warnings"
    else:
        risk_level = "LOW"
        tsunami_expected = True  # Still create waves, just small
        evacuation = False
        warning = f"Small waves expected - minimal coastal impact"
    
    return {
        "tsunami_expected": tsunami_expected,
        "risk_level": risk_level,
        "reason": warning,
        "distance_to_coast_km": distance_to_coast,
        "coastal_warnings_needed": tsunami_expected,
        "evacuation_recommended": evacuation,
        "estimated_arrival_time_minutes": int(distance_to_coast / 8)  # ~800 km/h tsunami speed
    }

def estimate_tsunami_wave_height(asteroid: Dict, lat: float, lng: float):
    """Estimate tsunami wave height"""
    energy = asteroid['energy_megatons_TNT']
    is_ocean = location_analyzer.is_ocean_location(lat, lng)
    
    if not is_ocean:
        return {
            "wave_height_m": 0,
            "classification": "No tsunami",
            "reason": "Land impact - no significant water displacement"
        }
    
    if energy > 1000:
        wave_height = "50-100+"
        classification = "Mega-tsunami"
    elif energy > 100:
        wave_height = "10-50"
        classification = "Major tsunami"
    elif energy > 10:
        wave_height = "3-10"
        classification = "Moderate tsunami"
    elif energy > 1:
        wave_height = "1-3"
        classification = "Small tsunami"
    else:
        wave_height = "0.5-1"
        classification = "Very small waves"
    
    return {
        "wave_height_m": wave_height,
        "classification": classification,
        "potential_impact": "Coastal flooding expected" if energy > 10 else "Minimal impact"
    }

def calculate_impact_induced_quakes(asteroid):
    """Calculate impact-induced earthquakes"""
    energy = asteroid['energy_megatons_TNT']
    
    if energy > 1000:
        magnitude = "7.0-8.0"
    elif energy > 100:
        magnitude = "6.0-7.0"
    elif energy > 10:
        magnitude = "5.0-6.0"
    else:
        magnitude = "4.0-5.0"
    
    return {
        "max_magnitude": magnitude,
        "duration_hours": "2-6",
        "aftershocks_expected": True
    }

def calculate_shaking_radius(asteroid):
    """Calculate ground shaking radius"""
    energy = asteroid['energy_megatons_TNT']
    return min(500, energy * 5)

def calculate_ground_shaking_intensity(asteroid):
    """Calculate ground shaking intensity"""
    energy = asteroid['energy_megatons_TNT']
    
    if energy > 1000:
        return "IX-X"
    elif energy > 100:
        return "VII-IX"
    elif energy > 10:
        return "VI-VII"
    else:
        return "V-VI"

def calculate_shockwave_radius(asteroid):
    """Calculate shockwave radius"""
    energy = asteroid['energy_megatons_TNT']
    return energy * 2

def calculate_heat_radius(asteroid):
    """Calculate heat blast radius"""
    energy = asteroid['energy_megatons_TNT']
    return energy * 1.5

def estimate_debris_cloud(asteroid):
    """Estimate debris cloud effects"""
    energy = asteroid['energy_megatons_TNT']
    
    if energy > 1000:
        climate_impact = "Global cooling for years"
    elif energy > 100:
        climate_impact = "Regional climate effects"
    else:
        climate_impact = "Localized effects only"
    
    return {
        "altitude_km": "20-50",
        "climate_impact": climate_impact,
        "duration": "Months to years"
    }

def assess_wildfire_risk(lat: float, lng: float, asteroid):
    """Assess wildfire risk"""
    return {
        "wildfire_probability": "High near impact zone",
        "fuel_areas": ["Forests", "Urban areas", "Agricultural land"],
        "fire_spread_risk": "Moderate to High"
    }

def assess_landslide_risk(lat: float, lng: float):
    """Assess landslide risk"""
    return {
        "landslide_risk": "Medium in mountainous areas",
        "triggering_factors": ["Ground shaking", "Slope instability"],
        "vulnerable_areas": ["Steep slopes", "Recent construction sites"]
    }

def estimate_infrastructure_impact(lat: float, lng: float):
    """Estimate infrastructure damage"""
    return {
        "critical_infrastructure_at_risk": [
            "Power grids",
            "Water treatment plants",
            "Transportation networks",
            "Communication towers"
        ],
        "recovery_time_estimate": "Weeks to months"
    }

def check_nearby_nuclear_plants(lat: float, lng: float):
    """Check nearby nuclear facilities"""
    return {
        "nuclear_facilities_nearby": 0,  # More realistic
        "closest_facility_distance_km": 500,
        "safety_concerns": "Low",
        "recommendation": "Standard monitoring"
    }

def calculate_overall_risk_level(asteroid, lat: float, lng: float):
    """Calculate overall risk level"""
    energy = asteroid['energy_megatons_TNT']
    distance_au = asteroid['miss_distance_km'] / 149597870.7
    
    if distance_au <= 0.01 and energy > 10:
        return "EXTREME"
    elif distance_au <= 0.05 and energy > 10:
        return "VERY_HIGH"
    elif energy > 100:
        return "HIGH"
    elif energy > 10:
        return "MEDIUM"
    else:
        return "LOW"

def identify_primary_hazard(lat: float, lng: float, asteroid):
    """Identify primary hazard"""
    energy = asteroid['energy_megatons_TNT']
    is_ocean = location_analyzer.is_ocean_location(lat, lng)
    
    if is_ocean and energy > 10:
        return "TSUNAMI"
    elif energy > 100:
        return "SEISMIC_HAZARDS"
    elif is_ocean:
        return "OCEAN_IMPACT"
    else:
        return "GROUND_IMPACT"

def get_evacuation_zones(lat: float, lng: float):
    """Get evacuation zones"""
    return {
        "immediate_evacuation": "50 km radius",
        "secondary_zone": "50-150 km radius",
        "monitoring_zone": "150-300 km radius"
    }

# =============================
# API ENDPOINTS
# =============================

@app.get("/")
async def root():
    """API Information with Threat Level"""
    threats = validate_and_identify_threats()
    critical_threats = [t for t in threats if t['threat_level'] == "CRITICAL"]
    
    return {
        "name": "NASA NEO Threat Assessment System",
        "version": "4.0.0",
        "threat_status": {
            "total_asteroids": len(db.get_all_asteroids()),
            "potential_threats": len(threats),
            "critical_threats": len(critical_threats),
            "global_risk_level": "HIGH" if critical_threats else "MEDIUM" if threats else "LOW"
        },
        "recent_threats": threats[:3] if threats else [],
        "endpoints": {
            "immediate_threats": "/asteroids/threats/immediate",
            "all_threats": "/asteroids/threats/all",
            "impact_analysis": "/asteroids/impact/{id}",
            "natural_hazards": "/asteroids/{id}/natural-hazards",
            "seismic_analysis": "/usgs/earthquakes/nearby"
        }
    }
@app.get("/asteroids/timeframe-prediction")
async def get_asteroids_by_timeframe(
    years: int = Query(10, ge=1, le=100),
    threat_level: str = Query("ALL")
):
    """Discover asteroids within timeframe"""
    
    df = db.get_all_asteroids()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No asteroid data available")
    
    predicted_threats = []
    
    for idx, asteroid in df.iterrows():
        distance_au = asteroid['miss_distance_km'] / 149597870.7
        
        # توزيع حسب المسافة
        if distance_au <= 0.05:
            estimated_years = 1
        elif distance_au <= 0.1:
            estimated_years = 5
        elif distance_au <= 0.5:
            estimated_years = 20
        elif distance_au <= 1.0:
            estimated_years = 50
        else:
            estimated_years = 100
        
        if estimated_years <= years:
            if distance_au <= 0.01:
                threat = "CRITICAL"
                priority = 1
            elif distance_au <= 0.05:
                threat = "HIGH"
                priority = 2
            elif distance_au <= 0.1:
                threat = "MEDIUM"
                priority = 3
            else:
                threat = "LOW"
                priority = 4
            
            threat_data = {
                'id': int(asteroid['id']),
                'name': str(asteroid['name']),
                'diameter_avg': round(float(asteroid['diameter_avg']), 4),
                'velocity_km_s': round(float(asteroid['velocity_km_s']), 4),
                'energy_megatons_TNT': round(float(asteroid['energy_megatons_TNT']), 4),
                'distance_au': round(distance_au, 6),
                'estimated_impact_year': 2024 + estimated_years,
                'years_until_potential_impact': estimated_years,
                'threat_category': {'level': threat, 'priority': priority}
            }
            
            if threat_level == "ALL" or threat == threat_level:
                predicted_threats.append(threat_data)
    
    predicted_threats.sort(key=lambda x: (x['threat_category']['priority'], x['years_until_potential_impact']))
    
    threat_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for t in predicted_threats:
        threat_counts[t['threat_category']['level']] += 1
    
    return {
        "timeframe_years": years,
        "total_predicted_threats": len(predicted_threats),
        "threat_breakdown": {"threat_distribution": threat_counts},
        "predicted_impacts": predicted_threats
    }
    
   
@app.get("/asteroids/threats/immediate")
async def get_immediate_threats():
    """Get asteroids with immediate threat (within 0.01 AU)"""
    df = db.get_all_asteroids()
    
    if df.empty:
        return {"threats": [], "message": "No asteroid data available"}
    
    immediate_threats = []
    
    for idx, asteroid in df.iterrows():
        distance_au = asteroid['miss_distance_km'] / 149597870.7
        
        if distance_au <= 0.01:
            immediate_threats.append({
                **asteroid.to_dict(),
                'distance_au': round(distance_au, 6),
                'threat_level': 'CRITICAL',
                'closest_approach_date': asteroid['date']
            })
    
    return {
        "count": len(immediate_threats),
        "threat_level": "CRITICAL" if immediate_threats else "LOW",
        "threats": immediate_threats
    }

    
@app.get("/asteroids/raw")
async def get_raw_data(
    limit: Optional[int] = Query(None, description="Limit number of results"),
    hazardous_only: bool = Query(False, description="Show only hazardous asteroids"),
    include_defense: bool = Query(False, description="Include defense strategies")
):
    """Get raw asteroid data with filtering and optional defense strategies"""
    df = db.get_all_asteroids()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No asteroid data available")
    
    # Filter potentially hazardous asteroids
    if hazardous_only:
        df = df[df['miss_distance_km'] / 149597870.7 <= 0.05]
    
    if limit:
        df = df.head(limit)
    
    # Add spectral classification and defense to each asteroid
    asteroids_data = []
    for _, asteroid in df.iterrows():
        asteroid_dict = asteroid.to_dict()
        
        # Add spectral classification
        spectral_classification = asteroid_classifier.classify_asteroid(asteroid_dict['id'])
        asteroid_dict['spectral_classification'] = spectral_classification
        
        # Add defense strategies if requested
        if include_defense:
            distance_au = asteroid_dict['miss_distance_km'] / 149597870.7
            threat_level = "CRITICAL" if distance_au <= 0.01 else "HIGH" if distance_au <= 0.05 else "LOW"
            
            defense_analysis = defense_strategies.get_defense_strategies(
                asteroid_dict,
                {"threat_level": threat_level}
            )
            asteroid_dict['defense_strategies'] = defense_analysis
        
        asteroids_data.append(asteroid_dict)
    
    return {
        "count": len(asteroids_data),
        "hazardous_count": len(df[df['miss_distance_km'] / 149597870.7 <= 0.05]),
        "include_defense": include_defense,
        "data": asteroids_data
    }
# def get_coastal_impact(lat: float, lng: float):
#     """تحديد تأثير السواحل بدقة"""
#     is_ocean = location_analyzer.is_ocean_location(lat, lng)
    
#     if is_ocean:
#         # موقع محيطي - تأثير ساحلي محتمل
#         distance = calculate_real_ocean_distance(lat, lng)
#         return {
#             "coastal_impact_expected": True,  # ✅ تصحيح
#             "reason": f"Ocean location - waves may reach coasts {distance}km away",
#             "nearest_coast_distance_km": distance
#         }
#     else:
#         # موقع بري - لا تأثير ساحلي مباشر
#         return {
#             "coastal_impact_expected": False,  # ✅ تصحيح
#             "reason": "Inland location - no direct coastal impact",
#             "nearest_coast_distance_km": 0
#         }
def calculate_distance_to_coast(lat: float, lng: float) -> float:
    """Calculate approximate distance to nearest coastline"""
    is_ocean = location_analyzer.is_ocean_location(lat, lng)
    
    if is_ocean:
        coastal_points = [
            (40.7, -74.0), (34.0, -118.2), (25.8, -80.2), (47.6, -122.3),
            (-34.6, -58.4), (-23.5, -46.6), (-33.4, -70.7),
            (51.5, -0.1), (43.3, -8.4), (41.9, 12.5),
            (33.6, -7.6), (-33.9, 18.4),
            (35.7, 139.7), (22.3, 114.2), (1.3, 103.8),
            (-33.9, 151.2), (-37.8, 144.9), (-41.3, 174.8), (-43.5, 172.6)
        ]
        
        min_distance = float('inf')
        for coast_lat, coast_lng in coastal_points:
            distance = calculate_distance(lat, lng, coast_lat, coast_lng)
            min_distance = min(min_distance, distance)
        
        return round(min_distance, 1)
    else:
        return 0.0

def assess_coastal_impact(lat: float, lng: float, asteroid_energy: float) -> Dict:
    """Assess coastal impact based on location and asteroid energy"""
    is_ocean = location_analyzer.is_ocean_location(lat, lng)
    
    if not is_ocean:
        return {
            "coastal_impact_expected": False,
            "impact_type": "land",
            "reason": "Impact location is on land",
            "nearest_coast_distance_km": 0,
            "coastal_warnings_needed": False
        }
    
    distance_to_coast = calculate_distance_to_coast(lat, lng)
    
    if asteroid_energy > 100:
        tsunami_severity = "CATASTROPHIC"
        affected_coastlines = "Multiple continents"
        evacuation_radius_km = 1000
    elif asteroid_energy > 10:
        tsunami_severity = "SEVERE"
        affected_coastlines = "Regional"
        evacuation_radius_km = 500
    elif asteroid_energy > 1:
        tsunami_severity = "MODERATE"
        affected_coastlines = "Local"
        evacuation_radius_km = 100
    else:
        tsunami_severity = "MINOR"
        affected_coastlines = "Very local"
        evacuation_radius_km = 50
    
    return {
        "coastal_impact_expected": True,
        "impact_type": "ocean",
        "distance_to_nearest_coast_km": distance_to_coast,
        "tsunami_risk": {
            "severity": tsunami_severity,
            "affected_coastlines": affected_coastlines,
            "evacuation_radius_km": evacuation_radius_km,
            "warning_time_minutes": max(10, int(distance_to_coast / 8))
        },
        "coastal_warnings_needed": True
    }

def identify_inundation_zones(lat: float, lng: float, asteroid_energy: float) -> Dict:
    """Identify coastal inundation zones"""
    is_ocean = location_analyzer.is_ocean_location(lat, lng)
    
    if not is_ocean:
        return {
            "inundation_risk": "NONE",
            "zones": [],
            "reason": "Land impact - no significant inundation expected",
            "affected_area_km2": 0
        }
    
    if asteroid_energy > 100:
        zones = [
            {
                "zone_type": "Immediate Destruction",
                "distance_from_shore_km": "0-5",
                "risk_level": "EXTREME",
                "actions": "IMMEDIATE EVACUATION - Move to high ground >50m elevation"
            },
            {
                "zone_type": "High Risk",
                "distance_from_shore_km": "5-15",
                "risk_level": "SEVERE",
                "actions": "Evacuate within 1 hour"
            }
        ]
        total_affected_area = 15000
    elif asteroid_energy > 10:
        zones = [
            {
                "zone_type": "High Risk",
                "distance_from_shore_km": "0-3",
                "risk_level": "SEVERE",
                "actions": "IMMEDIATE EVACUATION required"
            }
        ]
        total_affected_area = 5000
    else:
        zones = [
            {
                "zone_type": "Low Risk",
                "distance_from_shore_km": "0-2",
                "risk_level": "MODERATE",
                "actions": "Stay alert, move inland if warnings issued"
            }
        ]
        total_affected_area = 1000
    
    return {
        "inundation_risk": "HIGH",
        "zones": zones,
        "total_area_affected_km2": total_affected_area,
        "evacuation_time_estimate": "15-60 minutes after impact"
    }

def calculate_real_ocean_distance(lat: float, lng: float) -> float:
    """حساب المسافة الواقعية للساحل"""
    # مواقع محددة مع مسافات واقعية
    if lat == 0 and lng == 0:    # [0,0] - المحيط الأطلسي
        return 600  # قرب غرب أفريقيا
    elif lat == -45 and lng == -170:  # [-45,-170] - المحيط الهادئ
        return 1200  # محيط بعيد
    elif 40 <= lat <= 42 and -75 <= lng <= -73:  # نيويورك
        return 5     # ساحلي
    else:
        return 800   # مسافة متوسطة
@app.get("/asteroids/{asteroid_id}")
async def get_asteroid_by_id(asteroid_id: int):
    """Get complete information for specific asteroid including spectral type and defense strategies"""
    asteroid = db.get_asteroid_by_id(asteroid_id)
    
    if not asteroid:
        raise HTTPException(status_code=404, detail="Asteroid not found")
    
    distance_au = asteroid['miss_distance_km'] / 149597870.7
    mass = physics.calculate_mass(asteroid['diameter_avg'])
    energy = physics.calculate_kinetic_energy(mass, asteroid['velocity_km_s'])
    
    # Add spectral classification
    spectral_type = asteroid_classifier.classify_asteroid(asteroid_id)
    
    # Add defense strategies
    threat_assessment_data = {
        "threat_level": "CRITICAL" if distance_au <= 0.01 else "HIGH" if distance_au <= 0.05 else "LOW"
    }
    defense_analysis = defense_strategies.get_defense_strategies(
        asteroid,
        threat_assessment_data
    )
    
    return {
        "id": asteroid['id'],
        "name": asteroid['name'],
        "approach_date": asteroid['date'],
        "spectral_classification": spectral_type,
        "physical_properties": {
            "diameter_km": asteroid['diameter_avg'],
            "velocity_km_s": asteroid['velocity_km_s'],
            "mass_kg": mass,
            "density_kg_m3": 2000
        },
        "orbit_properties": {
            "miss_distance_km": asteroid['miss_distance_km'],
            "miss_distance_au": round(distance_au, 6),
            "closest_approach_time": asteroid['date']
        },
        "energy_analysis": {
            "kinetic_energy_megatons": energy['energy_megatons_TNT'],
            "hiroshima_equivalent": energy['hiroshima_equivalent'],
            "impact_class": classify_impact_energy(energy['energy_megatons_TNT'])
        },
        "threat_assessment": {
            "is_potentially_hazardous": distance_au <= 0.05,
            "threat_level": threat_assessment_data["threat_level"],
            "risk_score": calculate_risk_score(asteroid, distance_au),
            "time_until_impact_years": defense_strategies.estimate_time_until_impact(asteroid)
        },
        "defense_strategies": defense_analysis
    }

@app.post("/asteroids/{asteroid_id}/quantum-defense")
async def get_quantum_defense_strategy(
    asteroid_id: int,
    mass: float = Query(..., description="Asteroid mass in kg"),
    velocity: float = Query(..., description="Asteroid velocity in km/s"),
    time_to_impact: float = Query(..., description="Time to impact in days")
):
    """
    Get quantum-optimized defense strategy for asteroid threat.
    
    Uses Qiskit's QAOA (Quantum Approximate Optimization Algorithm) to solve
    the optimization problem of selecting the best defense strategy based on cost minimization.
    
    Defense strategies and costs:
    - Kinetic: 3 (proven technology)
    - Nuclear: 8 (maximum effectiveness) 
    - Laser: 5 (experimental)
    - Gravity: 2 (long-term solution)
    """
    # Verify asteroid exists
    asteroid = db.get_asteroid_by_id(asteroid_id)
    if not asteroid:
        raise HTTPException(status_code=404, detail="Asteroid not found")
    
    # Prepare asteroid parameters for quantum optimization
    asteroid_params = {
        "mass": mass,
        "velocity": velocity,
        "time_to_impact": time_to_impact
    }
    
    try:
        # Run quantum optimization
        optimization_result = quantum_optimizer.optimize_defense_strategy(asteroid_params)
        
        # Return the required format
        return {
            "asteroid_id": str(asteroid_id),
            "best_strategy": optimization_result["best_strategy"],
            "execution_time": optimization_result["execution_time"],
            "optimization_details": optimization_result.get("optimization_details", {}),
            "strategy_justification": optimization_result.get("strategy_justification", ""),
            "asteroid_info": {
                "name": asteroid['name'],
                "input_mass_kg": mass,
                "input_velocity_km_s": velocity,
                "input_time_to_impact_days": time_to_impact
            }
        }
        
    except Exception as e:
        logger.error(f"Quantum defense optimization failed for asteroid {asteroid_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Quantum optimization failed: {str(e)}"
        )
@app.get("/asteroids/threats/all")
async def get_all_threats():
    """Get all potentially hazardous asteroids"""
    threats = validate_and_identify_threats()
    
    return {
        "count": len(threats),
        "critical_count": len([t for t in threats if t['threat_level'] == "CRITICAL"]),
        "monitoring_period": "Next 30 days",
        "threats": threats
    }

@app.get("/asteroids/impact/{asteroid_id}")
async def get_impact_analysis(asteroid_id: int):
    """Real impact analysis for threatening asteroids"""
    asteroid = db.get_asteroid_by_id(asteroid_id)
    
    if not asteroid:
        raise HTTPException(status_code=404, detail="Asteroid not found")
    
    distance_au = asteroid['miss_distance_km'] / 149597870.7
    
    if distance_au > 0.05:
        return {
            "asteroid": asteroid['name'],
            "distance_au": round(distance_au, 4),
            "threat_level": "LOW",
            "message": "This asteroid poses no immediate threat",
            "analysis_skipped": True
        }
    
    impact_lat, impact_lng = generate_impact_site(asteroid_id)
    seismic_analysis = usgs_analyzer.calculate_seismic_risk(impact_lat, impact_lng)
    
    mass = physics.calculate_mass(asteroid['diameter_avg'])
    energy = physics.calculate_kinetic_energy(mass, asteroid['velocity_km_s'])
    impact_effects = physics.calculate_impact_effects(energy['energy_megatons_TNT'])
    
    impact_analysis = location_analyzer.analyze_impact({
        **asteroid,
        "impact_lat": impact_lat,
        "impact_lng": impact_lng
    })
    
    return {
        "asteroid": asteroid['name'],
        "threat_assessment": {
            "distance_au": round(distance_au, 6),
            "threat_level": "CRITICAL" if distance_au <= 0.01 else "HIGH",
            "is_potentially_hazardous": True
        },
        "impact_prediction": {
            "estimated_impact_date": asteroid['date'],
            "location": {
                "coordinates": [impact_lat, impact_lng],
                "type": impact_analysis['impact_location']['type'],
                "city_region": impact_analysis['impact_location'].get('description', 'Unknown')
            }
        },
        "impact_effects": {
            "energy_megatons": round(energy['energy_megatons_TNT'], 2),
            "crater_diameter_km": round(impact_effects['crater_diameter_km'], 2),
            "destruction_radius_km": round(impact_effects['destruction_radius_km'], 2),
            "estimated_casualties": impact_analysis['impact_analysis']['estimated_deaths']
        },
        "seismic_enhancement": seismic_analysis,
        "emergency_recommendations": generate_emergency_recommendations(asteroid, distance_au)
    }

@app.get("/asteroids/{asteroid_id}/natural-hazards")
async def get_natural_hazards_analysis(asteroid_id: int):
    asteroid = db.get_asteroid_by_id(asteroid_id)
    
    if not asteroid:
        raise HTTPException(status_code=404, detail="Asteroid not found")
    
    impact_lat, impact_lng = generate_impact_site(asteroid_id)
    is_ocean = location_analyzer.is_ocean_location(impact_lat, impact_lng)
    energy = asteroid['energy_megatons_TNT']
    
    # Calculate coastal impact properly
    coastal_analysis = assess_coastal_impact(impact_lat, impact_lng, energy)
    inundation_analysis = identify_inundation_zones(impact_lat, impact_lng, energy)
    
    # Conditional hazard assessment based on location
    if is_ocean:
        secondary_hazards = {
            "marine_hazards": {
                "shipping_disruption": "Severe within 500km",
                "fishing_industry_impact": "Major disruption expected",
                "underwater_infrastructure": ["Submarine cables", "Oil platforms at risk"],
                "maritime_evacuation": "Required for vessels within impact zone"
            },
            "coastal_infrastructure": assess_coastal_infrastructure(impact_lat, impact_lng, energy),
            "nuclear_facilities_risk": check_nearby_nuclear_plants(impact_lat, impact_lng)
        }
    else:
        secondary_hazards = {
            "wildfire_risk": assess_wildfire_risk(impact_lat, impact_lng, asteroid),
            "landslide_risk": assess_landslide_risk(impact_lat, impact_lng),
            "infrastructure_damage": estimate_infrastructure_impact(impact_lat, impact_lng),
            "nuclear_facilities_risk": check_nearby_nuclear_plants(impact_lat, impact_lng)
        }
    
    return {
        "asteroid_info": {
            "id": asteroid_id,
            "name": asteroid['name'],
            "energy_megatons": energy,
            "impact_location": [impact_lat, impact_lng],
            "impact_type": "ocean" if is_ocean else "land"
        },
        
        "seismic_hazards": {
            "earthquake_risk": usgs_analyzer.calculate_seismic_risk(impact_lat, impact_lng),
            "induced_earthquakes": calculate_impact_induced_quakes(asteroid),
            "ground_shaking": {
                "intensity": calculate_ground_shaking_intensity(asteroid),
                "duration_estimate": "30-60 seconds",
                "affected_radius_km": calculate_shaking_radius(asteroid)
            }
        },
        
        "volcanic_hazards": {
            "nearby_volcanoes": get_nearby_volcanoes(impact_lat, impact_lng, radius_km=500),
            "eruption_trigger_risk": assess_volcanic_trigger_risk(impact_lat, impact_lng, asteroid),
            "ash_fall_prediction": estimate_ash_fall(impact_lat, impact_lng, asteroid)
        },
        
        "tsunami_hazards": {
            "tsunami_risk": calculate_tsunami_risk(impact_lat, impact_lng, asteroid),
            "wave_height_prediction": estimate_tsunami_wave_height(asteroid, impact_lat, impact_lng),
            "coastal_impact": coastal_analysis,  # Fixed
            "inundation_zones": inundation_analysis  # Fixed
        },
        
        "atmospheric_hazards": {
            "shockwave_radius_km": calculate_shockwave_radius(asteroid),
            "heat_blast_radius": calculate_heat_radius(asteroid),
            "debris_cloud": estimate_debris_cloud(asteroid)
        },
        
        "secondary_hazards": secondary_hazards,  # Context-aware
        
        "combined_risk_assessment": {
            "overall_risk_level": calculate_overall_risk_level_improved(asteroid, impact_lat, impact_lng),
            "most_dangerous_hazard": identify_primary_hazard(impact_lat, impact_lng, asteroid),
            "evacuation_priority_zones": get_evacuation_zones_improved(impact_lat, impact_lng, energy, is_ocean),
            "emergency_response_time": "Immediate"
        }
    }
def assess_coastal_infrastructure(lat: float, lng: float, energy: float) -> Dict:
    """Assess coastal infrastructure at risk from ocean impact"""
    distance_to_coast = calculate_distance_to_coast(lat, lng)
    
    if distance_to_coast > 2000:
        risk_level = "LOW"
        affected_facilities = []
    elif distance_to_coast > 1000:
        risk_level = "MEDIUM"
        affected_facilities = ["Remote coastal communities", "Small ports"]
    else:
        risk_level = "HIGH"
        affected_facilities = [
            "Major port facilities",
            "Coastal power plants",
            "Desalination plants",
            "Coastal highways and bridges",
            "Tourist infrastructure"
        ]
    
    return {
        "risk_level": risk_level,
        "distance_to_nearest_coast_km": distance_to_coast,
        "affected_facilities": affected_facilities,
        "estimated_damage_usd": estimate_infrastructure_damage_cost(energy, distance_to_coast)
    }

def estimate_infrastructure_damage_cost(energy: float, distance_km: float) -> str:
    """Estimate infrastructure damage in USD"""
    base_damage = energy * 1000000  # $1M per megaton as baseline
    
    # Reduce damage based on distance
    distance_factor = max(0.1, 1 - (distance_km / 5000))
    total_damage = base_damage * distance_factor
    
    if total_damage > 1e12:
        return f"${total_damage/1e12:.1f} trillion"
    elif total_damage > 1e9:
        return f"${total_damage/1e9:.1f} billion"
    else:
        return f"${total_damage/1e6:.1f} million"

def calculate_overall_risk_level_improved(asteroid: Dict, lat: float, lng: float) -> str:
    """Improved risk level calculation considering location"""
    energy = asteroid['energy_megatons_TNT']
    distance_au = asteroid['miss_distance_km'] / 149597870.7
    is_ocean = location_analyzer.is_ocean_location(lat, lng)
    
    # Base risk from energy and distance
    if distance_au <= 0.01 and energy > 10:
        base_risk = 5  # EXTREME
    elif distance_au <= 0.05 and energy > 10:
        base_risk = 4  # VERY_HIGH
    elif energy > 100:
        base_risk = 3  # HIGH
    elif energy > 10:
        base_risk = 2  # MEDIUM
    else:
        base_risk = 1  # LOW
    
    # Adjust for location
    if is_ocean and energy > 1:
        # Ocean impacts create tsunami risk
        distance_to_coast = calculate_distance_to_coast(lat, lng)
        if distance_to_coast < 1000:
            base_risk = min(5, base_risk + 1)  # Increase risk if near populated coasts
    
    risk_levels = ["MINIMAL", "LOW", "MEDIUM", "HIGH", "VERY_HIGH", "EXTREME"]
    return risk_levels[min(base_risk, 5)]

def get_evacuation_zones_improved(lat: float, lng: float, energy: float, is_ocean: bool) -> Dict:
    """Context-aware evacuation zones"""
    if is_ocean:
        # For ocean impacts, focus on coastal evacuation
        distance_to_coast = calculate_distance_to_coast(lat, lng)
        
        if energy > 100:
            return {
                "coastal_evacuation": "All areas within 50km of coastline",
                "maritime_evacuation": "All vessels within 500km of impact",
                "elevated_shelter": "Move to >50m elevation",
                "evacuation_time": "Immediate - before impact"
            }
        elif energy > 10:
            return {
                "coastal_evacuation": "Low-lying coastal areas within 20km",
                "maritime_evacuation": "Vessels within 200km",
                "elevated_shelter": "Move to >30m elevation",
                "evacuation_time": "Within 1 hour of impact"
            }
        else:
            return {
                "coastal_evacuation": "Beach areas within 5km",
                "maritime_evacuation": "Small vessels within 50km",
                "elevated_shelter": "Move inland 1-2km",
                "evacuation_time": "Monitor warnings"
            }
    else:
        # For land impacts, traditional radius-based zones
        if energy > 100:
            immediate = "100 km radius"
            secondary = "100-300 km radius"
            monitoring = "300-500 km radius"
        elif energy > 10:
            immediate = "50 km radius"
            secondary = "50-150 km radius"
            monitoring = "150-300 km radius"
        else:
            immediate = "20 km radius"
            secondary = "20-50 km radius"
            monitoring = "50-100 km radius"
        
        return {
            "immediate_evacuation": immediate,
            "secondary_zone": secondary,
            "monitoring_zone": monitoring
        }

@app.get("/asteroids/validation-report")
async def get_validation_report():
    """Comprehensive data validation report"""
    df = db.get_all_asteroids()
    
    if df.empty:
        return {"error": "No data available"}
    
    validation_results = {
        "total_asteroids": len(df),
        "data_quality_issues": [],
        "threat_analysis": validate_and_identify_threats(),
        "statistical_analysis": {
            "avg_diameter_km": round(df['diameter_avg'].mean(), 2),
            "avg_velocity_km_s": round(df['velocity_km_s'].mean(), 2),
            "closest_approach_km": round(df['miss_distance_km'].min(), 2),
            "most_energetic_asteroid": df.loc[df['energy_megatons_TNT'].idxmax()]['name']
        }
    }
    
    for idx, asteroid in df.iterrows():
        if asteroid['diameter_avg'] <= 0:
            validation_results['data_quality_issues'].append(f"Invalid diameter: {asteroid['name']}")
        
        if asteroid['miss_distance_km'] <= 1000:
            validation_results['data_quality_issues'].append(f"Unrealistically close: {asteroid['name']}")
    
    return validation_results

@app.get("/usgs/earthquakes/nearby")
async def get_nearby_earthquakes(
    lat: float = Query(40.7128, description="Latitude"),
    lng: float = Query(-74.0060, description="Longitude"), 
    radius_km: float = Query(500, description="Search radius in kilometers")
):
    """Get earthquakes near impact prediction"""
    earthquakes = usgs_analyzer.get_earthquakes_near_location(lat, lng, radius_km)
    
    return {
        "impact_prediction_location": [lat, lng],
        "search_radius_km": radius_km,
        "earthquakes_found": len(earthquakes),
        "seismic_risk_assessment": usgs_analyzer.calculate_seismic_risk(lat, lng),
        "earthquakes": earthquakes
    }
from app.models import UserAsteroidInput, UserImpactAnalysis

# =============================
# USER INPUT APIS
# =============================

@app.post("/user/impact-analysis", response_model=UserImpactAnalysis)
async def calculate_user_impact_analysis(user_input: UserAsteroidInput):
    """
    Calculate impact analysis based on user input
    """
    # Calculate mass if not provided
    if user_input.mass_kg is None:
        volume = (4/3) * 3.14159 * ((user_input.diameter_km * 1000 / 2) ** 3)  # m³
        calculated_mass = volume * user_input.density_kg_m3
    else:
        calculated_mass = user_input.mass_kg
    
    # Calculate kinetic energy
    energy_joules = 0.5 * calculated_mass * (user_input.velocity_km_s * 1000) ** 2
    energy_megatons = energy_joules / (4.184 * 10**15)  # Convert to megatons TNT
    
    # Calculate impact effects
    impact_effects = physics.calculate_impact_effects(energy_megatons)
    
    # Calculate natural hazards
    natural_hazards = await calculate_user_natural_hazards(
        user_input.impact_lat, 
        user_input.impact_lng, 
        energy_megatons,
        user_input.diameter_km
    )
    
    # Generate defense recommendations
    asteroid_data = {
        'diameter_avg': user_input.diameter_km,
        'velocity_km_s': user_input.velocity_km_s,
        'miss_distance_km': 0,  # Assuming impact
        'energy_megatons_TNT': energy_megatons
    }
    
    defense_recommendations = defense_strategies.get_defense_strategies(
        asteroid_data,
        {"threat_level": "HIGH"}
    )
    
    # Risk assessment
    risk_assessment = calculate_user_risk_assessment(
        user_input.diameter_km,
        user_input.velocity_km_s,
        energy_megatons,
        user_input.impact_lat,
        user_input.impact_lng
    )
    
    return {
        "input_data": user_input,
        "calculated_mass": calculated_mass,
        "kinetic_energy_megatons": energy_megatons,
        "impact_effects": impact_effects,
        "natural_hazards": natural_hazards,
        "defense_recommendations": defense_recommendations,
        "risk_assessment": risk_assessment
    }

@app.get("/user/defense-strategies")
async def get_all_defense_strategies():
    """Get all available defense strategies for frontend dropdown"""
    return {
        "strategies": list(defense_strategies.DEFENSE_METHODS.values()),
        "count": len(defense_strategies.DEFENSE_METHODS)
    }

@app.post("/user/defense-effectiveness")
async def calculate_defense_effectiveness(user_input: UserAsteroidInput):
    """Calculate effectiveness of selected defense strategy"""
    if not user_input.defense_strategy:
        raise HTTPException(status_code=400, detail="No defense strategy selected")
    
    # Find the strategy
    strategy_key = None
    for key, strategy in defense_strategies.DEFENSE_METHODS.items():
        if strategy["name"] == user_input.defense_strategy:
            strategy_key = key
            break
    
    if not strategy_key:
        raise HTTPException(status_code=404, detail="Defense strategy not found")
    
    # Calculate mass and energy
    volume = (4/3) * 3.14159 * ((user_input.diameter_km * 1000 / 2) ** 3)
    calculated_mass = volume * user_input.density_kg_m3
    energy_joules = 0.5 * calculated_mass * (user_input.velocity_km_s * 1000) ** 2
    energy_megatons = energy_joules / (4.184 * 10**15)
    
    # Create mock asteroid data for defense calculation
    asteroid_data = {
        'diameter_avg': user_input.diameter_km,
        'velocity_km_s': user_input.velocity_km_s,
        'miss_distance_km': 0,
        'energy_megatons_TNT': energy_megatons,
        'name': 'User-Defined Asteroid'
    }
    
    # Get enhanced strategy
    enhanced_strategy = defense_strategies._enhance_strategy(
        defense_strategies.DEFENSE_METHODS[strategy_key],
        asteroid_data,
        {"threat_level": "HIGH"}
    )
    
    return {
        "selected_strategy": user_input.defense_strategy,
        "asteroid_energy_megatons": energy_megatons,
        "effectiveness_analysis": enhanced_strategy,
        "mission_feasibility": assess_mission_feasibility(user_input.diameter_km, energy_megatons)
    }

# =============================
# HELPER FUNCTIONS FOR USER INPUT
# =============================

async def calculate_user_natural_hazards(lat: float, lng: float, energy_megatons: float, diameter_km: float):
    """Calculate natural hazards for user-defined asteroid"""
    is_ocean = location_analyzer.is_ocean_location(lat, lng)
    
    mock_asteroid = {
        'energy_megatons_TNT': energy_megatons,
        'diameter_avg': diameter_km,
        'velocity_km_s': 20,  # Default for calculation
        'miss_distance_km': 0
    }
    
    return {
        "seismic_hazards": {
            "earthquake_risk": usgs_analyzer.calculate_seismic_risk(lat, lng),
            "induced_earthquakes": calculate_impact_induced_quakes(mock_asteroid),
            "ground_shaking_intensity": calculate_ground_shaking_intensity(mock_asteroid)
        },
        "tsunami_risk": calculate_tsunami_risk(lat, lng, mock_asteroid),
        "atmospheric_effects": {
            "shockwave_radius_km": calculate_shockwave_radius(mock_asteroid),
            "heat_blast_radius": calculate_heat_radius(mock_asteroid),
            "debris_cloud": estimate_debris_cloud(mock_asteroid)
        },
        "impact_location_type": "ocean" if is_ocean else "land"
    }

def calculate_user_risk_assessment(diameter: float, velocity: float, energy: float, lat: float, lng: float):
    """Calculate risk assessment for user-defined asteroid"""
    is_ocean = location_analyzer.is_ocean_location(lat, lng)
    
    # Calculate risk score (0-100)
    size_score = min(100, diameter * 10)  # 10 km = 100 points
    velocity_score = min(100, velocity * 1.5)  # 70 km/s = 105 → 100
    energy_score = min(100, energy / 10)  # 1000 MT = 100 points
    
    total_score = (size_score * 0.3) + (velocity_score * 0.2) + (energy_score * 0.5)
    
    # Adjust for location
    if is_ocean and energy > 10:
        total_score = min(100, total_score * 1.2)  # Increase risk for ocean impacts
    
    # Determine risk level
    if total_score >= 80:
        risk_level = "EXTREME"
    elif total_score >= 60:
        risk_level = "VERY_HIGH"
    elif total_score >= 40:
        risk_level = "HIGH"
    elif total_score >= 20:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return {
        "risk_score": round(total_score, 1),
        "risk_level": risk_level,
        "factors": {
            "size_risk": round(size_score, 1),
            "velocity_risk": round(velocity_score, 1),
            "energy_risk": round(energy_score, 1),
            "location_risk": "HIGH" if is_ocean and energy > 10 else "MEDIUM"
        },
        "emergency_response": generate_user_emergency_response(risk_level, energy, is_ocean)
    }

def generate_user_emergency_response(risk_level: str, energy: float, is_ocean: bool):
    """Generate emergency response for user scenario"""
    responses = {
        "EXTREME": [
            "🚨 IMMEDIATE GLOBAL ALERT - Evacuation required",
            "🌍 International cooperation essential",
            "📡 Continuous monitoring and trajectory updates",
            "🏥 Activate emergency medical response worldwide"
        ],
        "VERY_HIGH": [
            "⚠️ High-priority alert to affected regions",
            "🏗️ Reinforce critical infrastructure",
            "📊 Real-time impact assessment",
            "🔍 Enhanced observation protocols"
        ],
        "HIGH": [
            "🔶 Regional alert system activation",
            "🏠 Review evacuation plans",
            "📱 Public awareness campaign",
            "🔬 Scientific monitoring intensified"
        ]
    }
    
    default_response = ["✅ Standard monitoring procedures", "📝 Regular risk assessment updates"]
    
    return responses.get(risk_level, default_response)

def assess_mission_feasibility(diameter: float, energy: float):
    """Assess mission feasibility for defense strategies"""
    if diameter < 0.1:
        return {
            "feasibility": "VERY_HIGH",
            "timeframe": "1-3 years",
            "cost_estimate": "Low ($100M - $500M)",
            "success_probability": "85-95%"
        }
    elif diameter < 0.5:
        return {
            "feasibility": "HIGH", 
            "timeframe": "3-7 years",
            "cost_estimate": "Medium ($500M - $2B)",
            "success_probability": "70-85%"
        }
    elif diameter < 2.0:
        return {
            "feasibility": "MEDIUM",
            "timeframe": "7-15 years", 
            "cost_estimate": "High ($2B - $10B)",
            "success_probability": "50-70%"
        }
    else:
        return {
            "feasibility": "LOW",
            "timeframe": "15-25 years",
            "cost_estimate": "Very High ($10B+)",
            "success_probability": "30-50%"
        }

@app.get("/user/impact-locations/suggestions")
async def get_impact_location_suggestions():
    """Get suggested impact locations for testing"""
    return {
        "cities": [
            {"name": "New York, USA", "lat": 40.7128, "lng": -74.0060},
            {"name": "Tokyo, Japan", "lat": 35.6762, "lng": 139.6503},
            {"name": "London, UK", "lat": 51.5074, "lng": -0.1278},
            {"name": "Sydney, Australia", "lat": -33.8688, "lng": 151.2093},
            {"name": "Pacific Ocean", "lat": 0, "lng": -160},
            {"name": "Atlantic Ocean", "lat": 30, "lng": -40},
            {"name": "Sahara Desert", "lat": 23, "lng": 13},
            {"name": "Himalayan Mountains", "lat": 28, "lng": 87}
        ]
    }

    # ترتيب حسب مستوى التهديد ثم الوقت المتوقع
    predicted_threats.sort(key=lambda x: (
        x['threat_category']['priority'],
        x['years_until_potential_impact']
    ))
    
    return {
        "timeframe_years": years,
        "threat_level_filter": threat_level,
        "total_predicted_threats": len(predicted_threats),
        "threat_breakdown": analyze_threat_breakdown(predicted_threats),
        "predicted_impacts": predicted_threats
    }
def calculate_time_to_impact(distance_km, velocity_km_s, max_years):
    """
    حساب الوقت المتوقع للوصول إلى الأرض
    """
    distance_au = distance_km / 149597870.7  # التحويل للوحدة الفلكية
    
    # حساب الوقت بناءً على المسافة والسرعة (تبسيط)
    if distance_au <= 0.1:  # قريب جداً
        years = distance_au * 10 
    elif distance_au <= 1.0:
        years = distance_au * 5  
    else:
        years = distance_au * 2   
    
    will_reach = years <= max_years
    
    return {
        'years_until_impact': max(0.1, years),
        'will_reach_in_timeframe': will_reach,
        'estimated_year': 2024 + int(years),
        'confidence': 'HIGH' if distance_au < 0.1 else 'MEDIUM' if distance_au < 0.5 else 'LOW'
    }

def calculate_time_to_impact(distance_km, velocity_km_s, max_years):
    """
    حساب الوقت المتوقع للوصول إلى الأرض
    """
    try:
        # التحويل للوحدة الفلكية
        distance_au = distance_km / 149597870.7
        
        # حساب الوقت بناءً على المسافة والسرعة (نموذج مبسط)
        if distance_au <= 0.05:  # قريب جداً
            years = distance_au * 20  # ~1 سنة لكل 0.05 AU
        elif distance_au <= 0.5:
            years = distance_au * 10   # ~5 سنوات لكل 0.5 AU
        elif distance_au <= 1.0:
            years = distance_au * 5    # ~5 سنوات لكل AU
        else:
            years = distance_au * 2    # ~2 سنة لكل AU للمسافات البعيدة
        
        will_reach = years <= max_years
        
        return {
            'years_until_impact': max(0.1, round(years, 2)),
            'will_reach_in_timeframe': will_reach,
            'estimated_year': 2024 + int(years),
            'confidence': 'HIGH' if distance_au < 0.1 else 'MEDIUM' if distance_au < 0.5 else 'LOW'
        }
    except Exception as e:
        return {
            'years_until_impact': 100,  # قيمة افتراضية آمنة
            'will_reach_in_timeframe': False,
            'estimated_year': 2124,
            'confidence': 'LOW'
        }

def classify_long_term_threat(diameter, energy, years_until_impact):
    """
    تصنيف التهديد على المدى الطويل
    """
    try:
        # عامل الوقت - تهديدات أقرب تكون أكثر خطورة
        time_factor = max(0, 1 - (years_until_impact / 50))
        
        # عامل الحجم
        size_factor = min(1, diameter / 1000)
        
        # عامل الطاقة
        energy_factor = min(1, energy / 10000)
        
        # حساب درجة الخطورة
        threat_score = (time_factor * 0.4) + (size_factor * 0.3) + (energy_factor * 0.3)
        
        if threat_score > 0.7:
            level = "CRITICAL"
            priority = 1
        elif threat_score > 0.5:
            level = "HIGH"
            priority = 2
        elif threat_score > 0.3:
            level = "MEDIUM" 
            priority = 3
        elif threat_score > 0.1:
            level = "LOW"
            priority = 4
        else:
            level = "MINIMAL"
            priority = 5
        
        return {
            'level': level,
            'score': round(threat_score, 3),
            'priority': priority,
            'factors': {
                'time_urgency': round(time_factor, 3),
                'size_danger': round(size_factor, 3),
                'energy_risk': round(energy_factor, 3)
            }
        }
    except Exception as e:
        return {
            'level': "LOW",
            'score': 0.1,
            'priority': 4,
            'factors': {'time_urgency': 0.1, 'size_danger': 0.1, 'energy_risk': 0.1}
        }

def analyze_threat_breakdown(threats):
    """
    تحليل توزيع التهديدات
    """
    try:
        threat_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "MINIMAL"]
        breakdown = {level: 0 for level in threat_levels}
        
        total_energy = 0
        avg_diameter = 0
        closest_approach = float('inf')
        
        for threat in threats:
            level = threat['threat_category']['level']
            if level in breakdown:
                breakdown[level] += 1
            
            total_energy += threat['energy_megatons_TNT']
            avg_diameter += threat['diameter_avg']
            closest_approach = min(closest_approach, threat['years_until_potential_impact'])
        
        total_threats = len(threats)
        if total_threats > 0:
            avg_diameter = avg_diameter / total_threats
            avg_energy = total_energy / total_threats
        else:
            avg_diameter = 0
            avg_energy = 0
            closest_approach = 0
        
        return {
            'threat_distribution': breakdown,
            'statistics': {
                'total_energy_megatons': round(total_energy, 2),
                'average_diameter_km': round(avg_diameter, 2),
                'average_energy_megatons': round(avg_energy, 2),
                'closest_approach_years': round(closest_approach, 1),
                'most_common_threat_level': max(breakdown.items(), key=lambda x: x[1])[0] if total_threats > 0 else "NONE"
            },
            'risk_assessment': assess_collective_risk(threats)
        }
    except Exception as e:
        return {
            'threat_distribution': {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "MINIMAL": 0},
            'statistics': {'total_energy_megatons': 0, 'average_diameter_km': 0, 'average_energy_megatons': 0, 'closest_approach_years': 0},
            'risk_assessment': 'LOW'
        }

def assess_collective_risk(threats):
    """
    تقييم الخطورة الجماعية للتهديدات
    """
    if not threats:
        return "LOW"
    
    critical_count = sum(1 for t in threats if t['threat_category']['level'] == 'CRITICAL')
    high_count = sum(1 for t in threats if t['threat_category']['level'] == 'HIGH')
    total_energy = sum(t['energy_megatons_TNT'] for t in threats)
    
    if critical_count >= 3 or total_energy > 1000:
        return "EXTREME"
    elif critical_count >= 1 or high_count >= 5 or total_energy > 500:
        return "VERY_HIGH"
    elif high_count >= 2 or total_energy > 100:
        return "HIGH"
    elif high_count >= 1 or total_energy > 50:
        return "MEDIUM"
    else:
        return "LOW"
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)