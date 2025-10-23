import pandas as pd
from src.model import Line
from src.train import TrainState
from src.sim import run_sim
from src.controllers import DistaAI_Simple

# Load test data
segments = pd.read_csv('data/segments.csv')
line = Line(segments)

# Create a single train
train = TrainState(0, pos_m=0.0)
trains = [train]
controller = DistaAI_Simple()
controller_map = {0: controller}

# Run longer simulation (3600 seconds = 1 hour)
results = run_sim(line, trains, controller_map, dt=0.5, T=3600)

# Print statistics
print(f'Total line distance: {line.total_m:.1f}m ({line.total_m/1000:.1f} km)')
print(f'Simulation time: 3600s = 1 hour')
print(f'Positions logged: {len(results)}')
print(f'\nMax speed: {results["v"].max() * 3.6:.1f} km/h')
print(f'Avg speed: {results["v"].mean() * 3.6:.1f} km/h')
print(f'Final position: {results["pos_m"].iloc[-1]:.1f}m ({results["pos_m"].iloc[-1]/1000:.1f} km)')

# Check position at different times
times_to_check = [60, 300, 600, 1200, 1800, 2400, 3000, 3600]
print(f'\nPosition over time:')
for t in times_to_check:
    rows = results[results['t'] == t]
    if not rows.empty:
        pos = rows.iloc[0]['pos_m']
        vel = rows.iloc[0]['v']
        print(f't={t:4d}s: pos={pos:8.1f}m ({pos/1000:5.2f}km), v={vel*3.6:5.1f} km/h')

# Check when train reaches 6.9km (first segment boundary)
rows_6900 = results[results['pos_m'] >= 6900]
if not rows_6900.empty:
    first_cross = rows_6900.iloc[0]
    print(f'\nCrossed 6.9km boundary at t={first_cross["t"]:.1f}s, v={first_cross["v"]*3.6:.1f} km/h')
