"""
Quantum Optimizer for Asteroid Defense Strategy Selection

This module uses Qiskit's QAOA (Quantum Approximate Optimization Algorithm) 
to solve the optimization problem of selecting the best defense strategy
for asteroid threats based on cost minimization.
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import logging

logger = logging.getLogger(__name__)

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.algorithms import QAOA
    from qiskit_optimization.converters import QuadraticProgramToQubo
    from qiskit.algorithms.optimizers import COBYLA
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    logger.warning("Qiskit not available, using classical optimization fallback")

class QuantumDefenseOptimizer:
    """
    Quantum optimizer for asteroid defense strategy selection using QAOA.
    
    Defense strategies and their costs:
    - Kinetic: 3 (lowest cost, proven technology)
    - Nuclear: 8 (highest cost, most effective)
    - Laser: 5 (medium cost, experimental)
    - Gravity: 2 (lowest cost, long-term solution)
    """
    
    # Defense strategies with their costs
    DEFENSE_STRATEGIES = {
        "Kinetic": 3,
        "Nuclear": 8, 
        "Laser": 5,
        "Gravity": 2
    }
    
    def __init__(self, backend_name: str = "aer_simulator"):
        """
        Initialize the quantum optimizer.
        
        Args:
            backend_name: Name of the quantum backend to use
        """
        self.backend_name = backend_name
        self.qiskit_available = QISKIT_AVAILABLE
        
        if QISKIT_AVAILABLE:
            try:
                self.backend = AerSimulator()
                self.optimizer = COBYLA(maxiter=100)
            except Exception as e:
                logger.warning(f"Failed to initialize Qiskit components: {e}")
                self.qiskit_available = False
        else:
            self.backend = None
            self.optimizer = None
        
    def create_optimization_problem(self, asteroid_params: Dict):
        """
        Create a quadratic program for defense strategy optimization.
        
        Args:
            asteroid_params: Dictionary containing mass, velocity, time_to_impact
            
        Returns:
            QuadraticProgram or dict: The optimization problem or classical representation
        """
        if not self.qiskit_available:
            # Return classical problem representation
            return {
                "strategies": list(self.DEFENSE_STRATEGIES.keys()),
                "costs": list(self.DEFENSE_STRATEGIES.values()),
                "constraint": "exactly_one_strategy"
            }
        
        # Create quadratic program
        qp = QuadraticProgram("asteroid_defense_optimization")
        
        # Add binary variables for each defense strategy
        for strategy in self.DEFENSE_STRATEGIES.keys():
            qp.binary_var(strategy)
        
        # Constraint: exactly one strategy must be selected
        qp.linear_constraint(
            linear={strategy: 1 for strategy in self.DEFENSE_STRATEGIES.keys()},
            sense="==",
            rhs=1,
            name="one_strategy_constraint"
        )
        
        # Objective: minimize total cost
        # We want to minimize the sum of (cost * strategy_selected)
        linear_terms = {}
        for strategy, cost in self.DEFENSE_STRATEGIES.items():
            linear_terms[strategy] = cost
            
        qp.minimize(linear=linear_terms)
        
        return qp
    
    def solve_with_qaoa(self, problem) -> Tuple[str, Dict]:
        """
        Solve the optimization problem using QAOA or classical fallback.
        
        Args:
            problem: The quadratic program or classical problem representation
            
        Returns:
            Tuple of (best_strategy, solution_info)
        """
        if not self.qiskit_available or isinstance(problem, dict):
            # Classical optimization fallback
            best_strategy = min(self.DEFENSE_STRATEGIES, key=self.DEFENSE_STRATEGIES.get)
            
            solution_info = {
                "optimal_value": self.DEFENSE_STRATEGIES[best_strategy],
                "optimal_solution": [1 if s == best_strategy else 0 for s in self.DEFENSE_STRATEGIES.keys()],
                "strategy_costs": self.DEFENSE_STRATEGIES,
                "selected_strategy_cost": self.DEFENSE_STRATEGIES[best_strategy],
                "quantum_algorithm": "Classical_Optimization",
                "backend": "Classical",
                "optimization_successful": True,
                "note": "Using classical optimization due to Qiskit unavailability"
            }
            
            return best_strategy, solution_info
        
        try:
            # Convert to QUBO
            converter = QuadraticProgramToQubo()
            qubo = converter.convert(problem)
            
            # Initialize QAOA
            qaoa = QAOA(
                optimizer=self.optimizer,
                quantum_instance=self.backend,
                reps=2  # Number of QAOA layers
            )
            
            # Solve the problem
            result = qaoa.solve(qubo)
            
            # Extract the best strategy
            best_strategy = None
            for strategy in self.DEFENSE_STRATEGIES.keys():
                if result.x[list(self.DEFENSE_STRATEGIES.keys()).index(strategy)] == 1:
                    best_strategy = strategy
                    break
            
            if best_strategy is None:
                # Fallback to classical minimum
                best_strategy = min(self.DEFENSE_STRATEGIES, key=self.DEFENSE_STRATEGIES.get)
            
            solution_info = {
                "optimal_value": result.fval,
                "optimal_solution": result.x.tolist(),
                "strategy_costs": self.DEFENSE_STRATEGIES,
                "selected_strategy_cost": self.DEFENSE_STRATEGIES[best_strategy],
                "quantum_algorithm": "QAOA",
                "backend": self.backend_name,
                "optimization_successful": True
            }
            
            return best_strategy, solution_info
            
        except Exception as e:
            logger.error(f"QAOA optimization failed: {e}")
            # Fallback to classical solution
            best_strategy = min(self.DEFENSE_STRATEGIES, key=self.DEFENSE_STRATEGIES.get)
            
            solution_info = {
                "optimal_value": self.DEFENSE_STRATEGIES[best_strategy],
                "optimal_solution": [1 if s == best_strategy else 0 for s in self.DEFENSE_STRATEGIES.keys()],
                "strategy_costs": self.DEFENSE_STRATEGIES,
                "selected_strategy_cost": self.DEFENSE_STRATEGIES[best_strategy],
                "quantum_algorithm": "Classical_Fallback",
                "backend": "N/A",
                "optimization_successful": False,
                "error": str(e)
            }
            
            return best_strategy, solution_info
    
    def optimize_defense_strategy(self, asteroid_params: Dict) -> Dict:
        """
        Optimize defense strategy for given asteroid parameters.
        
        Args:
            asteroid_params: Dictionary containing:
                - mass: Asteroid mass in kg
                - velocity: Asteroid velocity in km/s  
                - time_to_impact: Time to impact in days
                
        Returns:
            Dictionary containing optimization results
        """
        try:
            # Validate input parameters
            required_params = ["mass", "velocity", "time_to_impact"]
            for param in required_params:
                if param not in asteroid_params:
                    raise ValueError(f"Missing required parameter: {param}")
            
            # Create and solve optimization problem
            qp = self.create_optimization_problem(asteroid_params)
            best_strategy, solution_info = self.solve_with_qaoa(qp)
            
            # Calculate execution time (time_to_impact - 1 day buffer)
            time_to_impact = asteroid_params["time_to_impact"]
            buffer_time = 1  # 1 day buffer
            execution_time = datetime.now() + timedelta(days=time_to_impact - buffer_time)
            
            return {
                "best_strategy": best_strategy,
                "execution_time": execution_time.isoformat() + "Z",
                "optimization_details": solution_info,
                "asteroid_parameters": asteroid_params,
                "strategy_justification": self._get_strategy_justification(
                    best_strategy, asteroid_params
                )
            }
            
        except Exception as e:
            logger.error(f"Defense strategy optimization failed: {e}")
            # Return fallback solution
            fallback_strategy = min(self.DEFENSE_STRATEGIES, key=self.DEFENSE_STRATEGIES.get)
            execution_time = datetime.now() + timedelta(days=asteroid_params.get("time_to_impact", 30) - 1)
            
            return {
                "best_strategy": fallback_strategy,
                "execution_time": execution_time.isoformat() + "Z",
                "optimization_details": {
                    "error": str(e),
                    "fallback_used": True
                },
                "asteroid_parameters": asteroid_params,
                "strategy_justification": "Fallback to lowest cost strategy due to optimization error"
            }
    
    def _get_strategy_justification(self, strategy: str, asteroid_params: Dict) -> str:
        """
        Provide justification for the selected strategy.
        
        Args:
            strategy: The selected defense strategy
            asteroid_params: Asteroid parameters
            
        Returns:
            String justification for the strategy selection
        """
        mass = asteroid_params.get("mass", 0)
        velocity = asteroid_params.get("velocity", 0)
        time_to_impact = asteroid_params.get("time_to_impact", 0)
        
        justifications = {
            "Gravity": f"Selected Gravity Tractor (cost: 2) - Most cost-effective for long-term deflection. "
                      f"Mass: {mass:.2e} kg, Velocity: {velocity} km/s, Time: {time_to_impact} days",
            
            "Kinetic": f"Selected Kinetic Impactor (cost: 3) - Proven technology with moderate cost. "
                      f"Effective for medium-sized asteroids. Mass: {mass:.2e} kg",
            
            "Laser": f"Selected Laser Ablation (cost: 5) - Advanced technology for precise deflection. "
                    f"Good for smaller asteroids with sufficient preparation time.",
            
            "Nuclear": f"Selected Nuclear Deflection (cost: 8) - Maximum effectiveness for large threats. "
                      f"High cost justified by asteroid mass: {mass:.2e} kg and velocity: {velocity} km/s"
        }
        
        return justifications.get(strategy, "Strategy selected based on cost optimization")
    
    def get_available_strategies(self) -> Dict:
        """
        Get information about all available defense strategies.
        
        Returns:
            Dictionary with strategy information
        """
        return {
            "strategies": self.DEFENSE_STRATEGIES,
            "total_strategies": len(self.DEFENSE_STRATEGIES),
            "lowest_cost": min(self.DEFENSE_STRATEGIES.values()),
            "highest_cost": max(self.DEFENSE_STRATEGIES.values()),
            "description": "Quantum-optimized defense strategy selection based on cost minimization"
        }

# Global instance for use in the API
quantum_optimizer = QuantumDefenseOptimizer()
