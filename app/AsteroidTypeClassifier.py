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

# Initialize classifier
asteroid_classifier = AsteroidTypeClassifier()