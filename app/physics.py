import numpy as np

class AsteroidPhysics:
    @staticmethod
    def calculate_mass(diameter_m: float, density=2600) -> float:
        """حساب الكتلة (kg)"""
        radius_m = diameter_m / 2
        volume_m3 = (4/3) * np.pi * (radius_m ** 3)
        return volume_m3 * density
    
    @staticmethod
    def calculate_kinetic_energy(mass_kg: float, velocity_km_s: float) -> dict:
        """حساب الطاقة الحركية"""
        velocity_m_s = velocity_km_s * 1000
        energy_joules = 0.5 * mass_kg * (velocity_m_s ** 2)
        energy_megatons = energy_joules / 4.184e15
        hiroshima_bombs = energy_megatons / 0.015
        
        return {
            'energy_joules': energy_joules,
            'energy_megatons_TNT': energy_megatons,
            'hiroshima_equivalent': hiroshima_bombs
        }
    
    @staticmethod
    def calculate_impact_effects(energy_megatons: float) -> dict:
        """حساب تأثيرات الاصطدام"""
        crater_diameter_km = 0.0177 * (energy_megatons ** 0.3658)
        destruction_radius_km = crater_diameter_km * 10
        shock_wave_velocity_km_s = 0.4 * (energy_megatons ** 0.25)
        
        return {
            'crater_diameter_km': crater_diameter_km,
            'destruction_radius_km': destruction_radius_km,
            'shock_wave_velocity_km_s': shock_wave_velocity_km_s,
            'affected_area_km2': np.pi * (destruction_radius_km ** 2)
        }
    
    @staticmethod
    def classify_hazard(diameter_m: float, distance_km: float, energy_mt: float) -> str:
        """تصنيف مستوى الخطورة"""
        distance_au = distance_km / 149597870.7
        
        if diameter_m >= 1000 and distance_au < 0.05:
            return "EXTINCTION_LEVEL"
        elif diameter_m >= 300 and distance_au < 0.1 and energy_mt > 1000:
            return "CIVILIZATION_THREAT"
        elif diameter_m >= 140 and distance_au < 0.05:
            return "REGIONAL_DEVASTATION"
        elif diameter_m >= 50 and distance_au < 0.01:
            return "CITY_DESTROYER"
        else:
            return "LOW_RISK"
