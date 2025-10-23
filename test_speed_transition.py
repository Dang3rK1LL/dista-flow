import pandas as pd
from src.model import Line
from src.train import TrainState
from src.sim import run_sim
from src.controllers import DistaAI_Simple

# Load test data
segments = pd.read_csv('data/segments.csv')
line = Line(segments)

# Create a single train to observe speed transition
train = TrainState(0, pos_m=0.0)
trains = [train]
controller = DistaAI_Simple()
controller_map = {0: controller}

# Run simulation
results = run_sim(line, trains, controller_map, dt=0.5, T=3600)

# Analyze transition from 80 km/h zone to 40 km/h zone
# First boundary is at 6900m
print("=== SPEED TRANSITION ANALYSIS: 80 km/h → 40 km/h ===\n")

# Get data around the boundary (6900m)
transition_data = results[(results['pos_m'] > 6000) & (results['pos_m'] < 8000)].copy()
transition_data['v_kmh'] = transition_data['v'] * 3.6

print("Position range: 6000m - 8000m (boundary at 6900m)")
print("\nSample data points:")
print(transition_data[['t', 'pos_m', 'v_kmh']].to_string(index=False))

# Calculate when train started slowing down
v_80 = results[results['v'] * 3.6 > 79.9].iloc[-1]
v_40 = results[results['v'] * 3.6 < 40.1].iloc[0]

print(f"\n=== Deceleration Timeline ===")
print(f"Last moment at 80 km/h: t={v_80['t']:.1f}s, pos={v_80['pos_m']:.1f}m")
print(f"First moment at 40 km/h: t={v_40['t']:.1f}s, pos={v_40['pos_m']:.1f}m")
print(f"Distance traveled during deceleration: {v_40['pos_m'] - v_80['pos_m']:.1f}m")
print(f"Time taken: {v_40['t'] - v_80['t']:.1f}s")

# Calculate theoretical braking distance
v_initial = 80 / 3.6  # m/s
v_final = 40 / 3.6    # m/s
a_brake = 0.7         # m/s²

# Using v² = u² + 2as → s = (v² - u²) / (2a)
theoretical_distance = (v_final**2 - v_initial**2) / (2 * (-a_brake))
theoretical_time = (v_final - v_initial) / (-a_brake)

print(f"\n=== Theoretical vs Actual ===")
print(f"Theoretical braking distance: {theoretical_distance:.1f}m")
print(f"Actual braking distance: {v_40['pos_m'] - v_80['pos_m']:.1f}m")
print(f"Theoretical braking time: {theoretical_time:.1f}s")
print(f"Actual braking time: {v_40['t'] - v_80['t']:.1f}s")

# Check if train slowed down BEFORE reaching the boundary
print(f"\n=== Safety Check ===")
if v_80['pos_m'] < 6900:
    print(f"✅ Train started slowing down {6900 - v_80['pos_m']:.1f}m BEFORE the boundary")
    print(f"   This is correct - anticipatory braking!")
else:
    print(f"❌ Train entered 40 km/h zone at {v_80['v']*3.6:.1f} km/h!")
    print(f"   This is a safety violation!")
