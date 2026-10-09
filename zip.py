import numpy as np

def estimate_pi(num_samples: int = 1_000_000_000) -> float:
    # 1. Initialize NumPy's modern random number generator
    rng = np.random.default_rng(seed=42)
    
    # 2. Generate random (x, y) coordinates uniformly distributed between -1 and 1
    x = rng.uniform(-1, 1, num_samples)
    y = rng.uniform(-1, 1, num_samples)
    
    # 3. Calculate Euclidean distance from the origin (0, 0)
    # The equation for a unit circle is x^2 + y^2 <= 1
    distance_squared = x**2 + y**2
    
    # 4. Count how many points fell inside the circle
    inside_circle = np.sum(distance_squared <= 1)
    
    # 5. Estimate Pi 
    # (Area of Circle / Area of Square) = (pi * r^2) / (2r * 2r) = pi / 4
    # Therefore: pi = 4 * (points inside circle / total points)
    pi_estimate = 4 * (inside_circle / num_samples)
    
    return pi_estimate

# Run the simulation with 1 billion iterations
simulated_pi = estimate_pi()
print(f"Estimated Pi: {simulated_pi}")
print(f"Actual Pi:    {np.pi}")
print(f"Error:         {abs(np.pi - simulated_pi):.6f}")
