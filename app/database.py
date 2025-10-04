import sqlite3
import pandas as pd
from typing import List, Optional
from app.models import Asteroid
from app.config import Config

class AsteroidDB:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DB_PATH
        self.init_database()
    
    def init_database(self):
        """إنشاء قاعدة البيانات والجداول"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asteroids (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                diameter_avg REAL,
                velocity_km_s REAL,
                miss_distance_km REAL,
                energy_megatons_TNT REAL,
                is_potentially_hazardous BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON asteroids(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hazardous ON asteroids(is_potentially_hazardous)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy ON asteroids(energy_megatons_TNT)')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized: {self.db_path}")
    
    def load_from_csv(self, csv_path):
        """تحميل البيانات من CSV"""
        try:
            df = pd.read_csv(csv_path)
            print(f"📊 Loaded {len(df)} rows from {csv_path}")
            
            # تحديد is_potentially_hazardous
            if 'is_potentially_hazardous' not in df.columns:
                df['is_potentially_hazardous'] = (
                    (df['diameter_avg'] >= 140) & 
                    (df['miss_distance_km'] <= 7479893.535)  # 0.05 AU
                )
            
            conn = sqlite3.connect(str(self.db_path))
            
            for _, row in df.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO asteroids 
                    (id, name, date, diameter_avg, velocity_km_s, miss_distance_km, 
                     energy_megatons_TNT, is_potentially_hazardous)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['id'], row['name'], row['date'],
                    row['diameter_avg'], row['velocity_km_s'],
                    row['miss_distance_km'], row['energy_megatons_TNT'],
                    row.get('is_potentially_hazardous', False)
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ Inserted {len(df)} asteroids into database")
            return True
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return False
    
    def get_all_asteroids(self) -> pd.DataFrame:
        conn = sqlite3.connect(str(self.db_path))
        df = pd.read_sql_query("SELECT * FROM asteroids ORDER BY date", conn)
        conn.close()
        return df
    
    def get_dangerous_asteroids(self, min_diameter=140, max_distance_au=0.05) -> pd.DataFrame:
        max_distance_km = max_distance_au * 149597870.7
        conn = sqlite3.connect(str(self.db_path))
        query = f'''
            SELECT * FROM asteroids 
            WHERE diameter_avg >= {min_diameter} 
            AND miss_distance_km <= {max_distance_km}
            ORDER BY miss_distance_km ASC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_asteroid_by_id(self, asteroid_id: int) -> Optional[dict]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM asteroids WHERE id = ?", (asteroid_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'name', 'date', 'diameter_avg', 'velocity_km_s', 
                      'miss_distance_km', 'energy_megatons_TNT', 'is_potentially_hazardous', 'created_at']
            return dict(zip(columns, row))
        return None
    
    def get_by_date(self, date: str) -> pd.DataFrame:
        conn = sqlite3.connect(str(self.db_path))
        df = pd.read_sql_query("SELECT * FROM asteroids WHERE date = ?", conn, params=(date,))
        conn.close()
        return df
