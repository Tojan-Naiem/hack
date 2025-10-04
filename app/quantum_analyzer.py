# app/quantum_analyzer.py - ملف جديد نظيف
import numpy as np
from typing import Dict

class QuantumAsteroidAnalyzer:
    """محلل كويكبات مستوحى من الحوسبة الكمومية"""
    
    def __init__(self):
        self.superposition_states = {
            'safe': np.array([1, 0]),      # |0⟩
            'dangerous': np.array([0, 1]), # |1⟩  
            'uncertain': np.array([1, 1])/np.sqrt(2) # |+⟩
        }
    
    def quantum_risk_calculation(self, asteroid_data: Dict) -> Dict:
        """حساب الخطورة باستخدام مبادئ كمومية"""
        try:
            # تحويل البيانات لحالات كمومية
            energy_state = self.energy_to_quantum_state(asteroid_data['energy_megatons_TNT'])
            distance_state = self.distance_to_quantum_state(asteroid_data['miss_distance_km'])
            size_state = self.size_to_quantum_state(asteroid_data['diameter_avg'])
            
            # تشابك كمومي مبسط
            risk_probability = self.simulate_quantum_entanglement(energy_state, distance_state, size_state)
            
            return {
                'quantum_risk_score': risk_probability,
                'quantum_state': 'superposition',
                'certainty_level': self.calculate_uncertainty(asteroid_data),
                'interpretation': self.get_quantum_interpretation(risk_probability)
            }
        except Exception as e:
            return {
                'quantum_risk_score': 0.5,
                'quantum_state': 'error',
                'certainty_level': 'unknown',
                'interpretation': f'خطأ في الحساب: {str(e)}'
            }
    
    def energy_to_quantum_state(self, energy: float) -> np.ndarray:
        """تحويل الطاقة لحالة كمومية"""
        if energy > 100:
            return np.array([0.2, 0.8])
        elif energy > 50:
            return np.array([0.5, 0.5])
        else:
            return np.array([0.8, 0.2])
    
    def distance_to_quantum_state(self, distance: float) -> np.ndarray:
        """تحويل المسافة لحالة كمومية"""
        distance_au = distance / 149597870.7
        
        if distance_au < 0.05:
            return np.array([0.1, 0.9])
        elif distance_au < 0.1:
            return np.array([0.4, 0.6])
        else:
            return np.array([0.9, 0.1])
    
    def size_to_quantum_state(self, size: float) -> np.ndarray:
        """تحويل الحجم لحالة كمومية"""
        if size > 140:
            return np.array([0.3, 0.7])
        elif size > 50:
            return np.array([0.6, 0.4])
        else:
            return np.array([0.8, 0.2])
    
    def simulate_quantum_entanglement(self, energy_state: np.ndarray, 
                                    distance_state: np.ndarray, 
                                    size_state: np.ndarray) -> float:
        """محاكاة التشابك الكمومي بين العوامل"""
        risk_prob = (energy_state[1] + distance_state[1] + size_state[1]) / 3
        return min(risk_prob * 1.2, 1.0)
    
    def calculate_uncertainty(self, asteroid_data: Dict) -> str:
        """حساب مستوى عدم التأكد"""
        energy = asteroid_data['energy_megatons_TNT']
        distance = asteroid_data['miss_distance_km']
        
        uncertainty_score = (energy / 100) * (10000000 / distance)
        
        if uncertainty_score > 0.7:
            return "high"
        elif uncertainty_score > 0.3:
            return "medium"
        else:
            return "low"
    
    def get_quantum_interpretation(self, risk_score: float) -> str:
        """تفسير النتائج الكمومية"""
        if risk_score > 0.7:
            return "🌀 حالة كمومية عالية الخطورة"
        elif risk_score > 0.4:
            return "⚡ حالة تراكب - احتمال متساوي"
        else:
            return "💫 حالة كمومية آمنة"

# إنشاء instance عام
quantum_analyzer = QuantumAsteroidAnalyzer()