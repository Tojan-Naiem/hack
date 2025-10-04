import os
from pathlib import Path

class Config:
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    INCOMING_DIR = DATA_DIR / "incoming"
    
    # Database
    DB_PATH = DATA_DIR / "asteroids.db"
    
    # CSV Files
    ASTEROIDS_DANGEROUS_CSV = INCOMING_DIR / "asteroids_dangerous.csv"
    ASTEROIDS_SUMMARY_CSV = INCOMING_DIR / "asteroids_summary.csv"
    
    # NASA API
    NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
    NASA_BASE_URL = "https://api.nasa.gov/neo/rest/v1"
    
    # Server
    HOST = "0.0.0.0"
    PORT = 8000
