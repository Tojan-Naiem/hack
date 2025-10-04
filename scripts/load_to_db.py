import pandas as pd
from sqlalchemy import create_engine
from app.models import Base, Asteroid
from sqlalchemy.orm import sessionmaker
import math

DB_URL = "sqlite:///./data/asteroids.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def compute_avg(dmin, dmax):
    return (dmin + dmax) / 2 if pd.notnull(dmin) and pd.notnull(dmax) else None

# density default (kg/m3) — يمكن تعدلي على حسب نوع الكويكب
DEFAULT_DENSITY = 3000.0

def mass_from_diameter(diameter_m, density=DEFAULT_DENSITY):
    if pd.isnull(diameter_m): return None
    r = diameter_m / 2.0
    volume = (4.0/3.0) * math.pi * (r**3)
    return density * volume

def energy_joules(mass_kg, velocity_km_s):
    if mass_kg is None or pd.isnull(velocity_km_s): return None
    v = velocity_km_s * 1000.0  # km/s -> m/s
    return 0.5 * mass_kg * (v**2)

def load_file_to_db(path):
    # الخاطف: كشف صيغة الملف
    if path.suffix == ".csv":
        df = pd.read_csv(path)
    elif path.suffix == ".xlsx":
        df = pd.read_excel(path)
    else:
        df = pd.read_json(path)
    # افتراضي: أعمدة اسمية؛ لازم تعدلي أسماء الأعمدة حسب الفحص
    records = []
    for _, row in df.iterrows():
        dmin = row.get("diameter_min") or row.get("estimated_diameter_min")
        dmax = row.get("diameter_max") or row.get("estimated_diameter_max")
        diam_avg = compute_avg(dmin, dmax)
        m = mass_from_diameter(diam_avg)
        e = energy_joules(m, row.get("velocity_km_s") or row.get("relative_velocity_km_s"))
        rec = Asteroid(
            id=str(row.get("id") or row.get("neo_reference_id") or ""),
            name=row.get("name"),
            close_approach_date=row.get("close_approach_date") or row.get("date"),
            diameter_min=dmin,
            diameter_max=dmax,
            diameter_avg=diam_avg,
            velocity_km_s=row.get("velocity_km_s") or row.get("relative_velocity_km_s"),
            miss_distance_km=float(row.get("miss_distance_km") or row.get("miss_distance") or 0),
            is_potentially_hazardous=bool(row.get("is_potentially_hazardous") or False)
        )
        records.append(rec)

    session = Session()
    for r in records:
        session.merge(r)  # merge لتجنب duplicates على نفس primary key
    session.commit()
    session.close()
