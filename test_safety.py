import pandas as pd
from src.model import Line
from src.train import TrainState
from src.sim import run_sim
from src.controllers import DistaAI_Simple

# Load test data
segments = pd.read_csv('data/segments.csv')
line = Line(segments)

# Create multiple trains with different starting positions
num_trains = 5
trains = []
for i in range(num_trains):
    train = TrainState(i, pos_m=i * 1000.0)
    trains.append(train)

controller = DistaAI_Simple()
controller_map = {train.id: controller for train in trains}

# Run simulation
results = run_sim(line, trains, controller_map, dt=0.5, T=3600)

# Check for minimum gaps (safety check)
print("=== SAFETY CHECK: Minimum Gaps Between Trains ===\n")
min_gaps = {}

for t in sorted(results['t'].unique()):
    rows = results[results['t'] == t].sort_values('pos_m')
    positions = rows['pos_m'].values
    train_ids = rows['id'].values
    
    for i in range(len(positions) - 1):
        gap = positions[i+1] - positions[i]
        pair = (train_ids[i], train_ids[i+1])
        
        if pair not in min_gaps:
            min_gaps[pair] = gap
        else:
            min_gaps[pair] = min(min_gaps[pair], gap)
        
        if gap < 120:  # Less than train length
            print(f"⚠️  COLLISION RISK at t={t:.1f}s:")
            print(f"    Train {train_ids[i]} at {positions[i]:.1f}m")
            print(f"    Train {train_ids[i+1]} at {positions[i+1]:.1f}m")
            print(f"    Gap: {gap:.1f}m (train length: 120m)")

print("\n=== Minimum Gaps Between Train Pairs ===")
for pair, gap in sorted(min_gaps.items()):
    print(f"Trains {pair[0]} and {pair[1]}: minimum gap = {gap:.1f}m")
    if gap < 120:
        print(f"  ❌ UNSAFE: Gap less than train length!")
    elif gap < 200:
        print(f"  ⚠️  WARNING: Gap less than 200m")
    else:
        print(f"  ✅ SAFE")

# Check speed transitions at segment boundaries
print("\n=== SPEED TRANSITIONS AT SEGMENT BOUNDARIES ===")
boundaries = [6900, 12600]

for boundary in boundaries:
    print(f"\nBoundary at {boundary}m ({boundary/1000}km):")
    for train_id in range(num_trains):
        train_data = results[results['id'] == train_id]
        
        # Find rows near boundary
        before = train_data[train_data['pos_m'] < boundary]
        after = train_data[train_data['pos_m'] >= boundary]
        
        if not before.empty and not after.empty:
            v_before = before.iloc[-1]['v'] * 3.6
            v_after = after.iloc[0]['v'] * 3.6
            t_cross = after.iloc[0]['t']
            
            print(f"  Train {train_id}: {v_before:.1f} km/h -> {v_after:.1f} km/h at t={t_cross:.1f}s")

# Check acceleration/deceleration rates
print("\n=== ACCELERATION/DECELERATION CHECK ===")
for train_id in range(min(2, num_trains)):  # Check first 2 trains
    train_data = results[results['id'] == train_id].sort_values('t')
    velocities = train_data['v'].values
    times = train_data['t'].values
    
    max_accel = 0
    max_decel = 0
    
    for i in range(1, len(velocities)):
        dt = times[i] - times[i-1]
        if dt > 0:
            accel = (velocities[i] - velocities[i-1]) / dt
            if accel > max_accel:
                max_accel = accel
            if accel < max_decel:
                max_decel = accel
    
    print(f"\nTrain {train_id}:")
    print(f"  Max acceleration: {max_accel:.3f} m/s² (limit: 0.7 m/s²)")
    print(f"  Max deceleration: {max_decel:.3f} m/s² (limit: -0.7 m/s²)")
    
    if max_accel > 0.75:
        print(f"  ⚠️  WARNING: Acceleration exceeds limit!")
    if max_decel < -0.75:
        print(f"  ⚠️  WARNING: Deceleration exceeds limit!")
