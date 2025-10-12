#!/usr/bin/env python3
"""Reload asteroids_summary.csv into the SQLite DB (callable script).
Usage: ./.venv/bin/python scripts/reload_csv.py
"""
import sys
from app.database import AsteroidDB
from app.config import Config

print(f"Loading CSV: {Config.ASTEROIDS_SUMMARY_CSV}")
try:
    db = AsteroidDB()
    ok = db.load_from_csv(Config.ASTEROIDS_SUMMARY_CSV)
    print("load_from_csv returned:", ok)
except Exception as e:
    print("Error:", e)
    sys.exit(2)
