# Quantum Defense Strategy Endpoint

## Overview

The `/asteroids/{id}/quantum-defense` endpoint uses quantum computing (Qiskit's QAOA algorithm) to optimize asteroid defense strategy selection based on cost minimization.

## Endpoint Details

- **Path**: `POST /asteroids/{id}/quantum-defense`
- **Method**: POST
- **Description**: Get quantum-optimized defense strategy for asteroid threat

## Parameters

### Path Parameters
- `asteroid_id` (int): The ID of the asteroid in the database

### Query Parameters
- `mass` (float, required): Asteroid mass in kg
- `velocity` (float, required): Asteroid velocity in km/s  
- `time_to_impact` (float, required): Time to impact in days

## Defense Strategies

The quantum optimizer considers four defense strategies with their costs:

| Strategy | Cost | Description |
|----------|------|-------------|
| Gravity | 2 | Gravity Tractor - Long-term solution, lowest cost |
| Kinetic | 3 | Kinetic Impactor - Proven technology, moderate cost |
| Laser | 5 | Laser Ablation - Experimental, medium cost |
| Nuclear | 8 | Nuclear Deflection - Maximum effectiveness, highest cost |

## Response Format

```json
{
  "asteroid_id": "123",
  "best_strategy": "Gravity",
  "execution_time": "2025-10-05T14:00:00Z",
  "optimization_details": {
    "optimal_value": 2,
    "selected_strategy_cost": 2,
    "quantum_algorithm": "QAOA",
    "backend": "aer_simulator",
    "optimization_successful": true
  },
  "strategy_justification": "Selected Gravity Tractor (cost: 2) - Most cost-effective for long-term deflection...",
  "asteroid_info": {
    "name": "Asteroid Name",
    "input_mass_kg": 1e12,
    "input_velocity_km_s": 20.0,
    "input_time_to_impact_days": 30.0
  }
}
```

## Example Usage

### cURL
```bash
curl -X POST "http://localhost:8000/asteroids/123/quantum-defense?mass=1e12&velocity=20&time_to_impact=30"
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/asteroids/123/quantum-defense",
    params={
        "mass": 1e12,
        "velocity": 20,
        "time_to_impact": 30
    }
)

result = response.json()
print(f"Best strategy: {result['best_strategy']}")
print(f"Execution time: {result['execution_time']}")
```

### JavaScript
```javascript
const response = await fetch('/asteroids/123/quantum-defense?mass=1e12&velocity=20&time_to_impact=30', {
    method: 'POST'
});

const result = await response.json();
console.log('Best strategy:', result.best_strategy);
console.log('Execution time:', result.execution_time);
```

## Quantum Algorithm Details

- **Algorithm**: QAOA (Quantum Approximate Optimization Algorithm)
- **Backend**: Aer Simulator (local quantum simulation)
- **Optimization**: Cost minimization with constraint that exactly one strategy must be selected
- **Fallback**: Classical optimization if quantum computation fails

## Error Handling

- **404**: Asteroid not found in database
- **500**: Quantum optimization failed (with fallback to classical solution)
- **400**: Missing required parameters

## Dependencies

The following packages are required:
- `qiskit==0.45.0`
- `qiskit-aer==0.13.0`
- `qiskit-optimization==0.6.0`

Install with:
```bash
pip install -r requirements.txt
```

## Testing

Run the test script to verify functionality:
```bash
python test_quantum_endpoint.py
```
