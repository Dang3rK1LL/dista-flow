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

# Run short simulation
results = run_sim(line, trains, controller_map, dt=0.5, T=300)

# Print statistics
print(f'Total line distance: {line.total_m:.1f}m ({line.total_m/1000:.1f} km)')
print(f'Positions logged: {len(results)}')
print(f'\nFirst 10 records:')
print(results.head(10))
print(f'\nLast 10 records:')
print(results.tail(10))
print(f'\nMax speed: {results["v"].max() * 3.6:.1f} km/h')
print(f'Avg speed: {results["v"].mean() * 3.6:.1f} km/h')
print(f'Final position: {results["pos_m"].iloc[-1]:.1f}m ({results["pos_m"].iloc[-1]/1000:.1f} km)')

# Check segment speeds
print(f'\nSegment information:')
for i, seg in enumerate(line.segments):
    print(f'Segment {i}: {seg.frm} -> {seg.to}, Length: {seg.length_m/1000:.1f}km, Speed: {seg.speed_mps*3.6:.0f} km/h')
