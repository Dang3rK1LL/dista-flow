import pandas as pd
from src.model import Line
from src.train import TrainState
from src.sim import run_sim
from src.controllers import DistaAI_Simple

# Load test data
segments = pd.read_csv('data/segments.csv')
line = Line(segments)

# Create multiple trains
num_trains = 5
trains = []
for i in range(num_trains):
    train = TrainState(i, pos_m=i * 1000.0)  # Start trains 1km apart
    trains.append(train)

controller = DistaAI_Simple()
controller_map = {train.id: controller for train in trains}

# Run simulation
results = run_sim(line, trains, controller_map, dt=0.5, T=3600)

# Print statistics
print(f'Total line distance: {line.total_m:.1f}m ({line.total_m/1000:.1f} km)')
print(f'Number of trains: {num_trains}')
print(f'Simulation time: 3600s = 1 hour')
print(f'Positions logged: {len(results)}')

# Check each train
for train_id in range(num_trains):
    train_results = results[results['id'] == train_id]
    final_pos = train_results['pos_m'].iloc[-1]
    max_speed = train_results['v'].max() * 3.6
    avg_speed = train_results['v'].mean() * 3.6
    print(f'\nTrain {train_id}:')
    print(f'  Final position: {final_pos:.1f}m ({final_pos/1000:.1f} km)')
    print(f'  Max speed: {max_speed:.1f} km/h')
    print(f'  Avg speed: {avg_speed:.1f} km/h')

# Check for collisions
print(f'\nChecking for collisions...')
for t in [300, 600, 900, 1200, 1800, 3600]:
    rows = results[results['t'] == t]
    if not rows.empty:
        positions = rows.sort_values('id')['pos_m'].values
        print(f't={t:4d}s: positions = {[f"{p/1000:.2f}" for p in positions]} km')
        
        # Check minimum gap
        for i in range(len(positions)-1):
            gap = positions[i+1] - positions[i]
            if gap < 120:  # Train length
                print(f'  WARNING: Trains {i} and {i+1} too close! Gap = {gap:.1f}m')
