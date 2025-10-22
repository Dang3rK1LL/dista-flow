#!/usr/bin/env python3
"""
Quick test sweep with reduced parameters for validation
"""
import pandas as pd
import os
import numpy as np
from pathlib import Path
from src.model import Line
from src.train import TrainState
from src.controllers import EtcsBaseline, DistaAI_Simple
from src.sim import run_sim
from src.metrics import compute_headways, throughput
import matplotlib.pyplot as plt

os.makedirs('outputs', exist_ok=True)

# Load data with fallback logic: try mav1.csv first, then demo files
data_options = ['data/segments_mav1.csv', 'data/segments_long.csv', 'data/segments.csv']
segments_file = None
for f in data_options:
    if Path(f).exists():
        segments_file = f
        break

if not segments_file:
    raise FileNotFoundError("No segments data file found!")

print(f"Using data file: {segments_file}")
segments = pd.read_csv(segments_file)
line = Line(segments)

print(f"Line length: {line.total_m/1000:.1f} km")

def make_trains(n_trains, prefix, spacing_m=1000):
    """Create n trains with specified spacing"""
    trains = []
    for i in range(n_trains):
        train = TrainState(
            train_id=f'{prefix}_T{i+1}',
            pos_m=i * spacing_m,
            length_m=120,
            a_max=0.7,
            a_brake=0.7
        )
        trains.append(train)
    return trains

def run_scenario(n_trains, reaction_s, margin_m, controller_type='ETCS'):
    """Run single scenario and return metrics"""
    trains = make_trains(n_trains, controller_type)
    
    if controller_type == 'ETCS':
        controllers = {t.id: EtcsBaseline(reaction_s, margin_m) for t in trains}
    else:  # DISTA
        controllers = {t.id: DistaAI_Simple(reaction_s, margin_m) for t in trains}
    
    # Longer simulation for the long line
    sim_time = 7200  # 2 hours
    df = run_sim(line, trains, controllers, dt=0.5, T=sim_time)
    
    # Calculate metrics
    hw_df = compute_headways(df)
    avg_headway = hw_df['gap_m'].mean() if len(hw_df) > 0 else np.nan
    tph_val = throughput(df, line.total_m)
    
    return {
        'n_trains': n_trains,
        'reaction_s': reaction_s,
        'margin_m': margin_m,
        'controller': controller_type,
        'avg_headway_m': avg_headway,
        'throughput': tph_val,
        'line_length_km': line.total_m / 1000.0,
        'total_records': len(df)
    }

# Reduced parameter ranges for quick test
reaction_times = [1.0, 2.0]
margins = [100, 200]
train_counts = [2, 3]

print("Starting quick parameter sweep...")
results = []

for n_trains in train_counts:
    for reaction_s in reaction_times:
        for margin_m in margins:
            print(f"Testing: n={n_trains}, reaction={reaction_s}s, margin={margin_m}m")
            
            # ETCS baseline
            try:
                result_etcs = run_scenario(n_trains, reaction_s, margin_m, 'ETCS')
                results.append(result_etcs)
                print(f"  ETCS: headway={result_etcs['avg_headway_m']:.1f}m, throughput={result_etcs['throughput']}")
            except Exception as e:
                print(f"  ETCS failed: {e}")
            
            # DISTA
            try:
                result_dista = run_scenario(n_trains, reaction_s, margin_m, 'DISTA')
                results.append(result_dista)
                print(f"  DISTA: headway={result_dista['avg_headway_m']:.1f}m, throughput={result_dista['throughput']}")
            except Exception as e:
                print(f"  DISTA failed: {e}")

# Save results
df_results = pd.DataFrame(results)
df_results.to_csv('outputs/quick_sweep_summary.csv', index=False)
print(f"\nResults saved to outputs/quick_sweep_summary.csv ({len(results)} rows)")

if len(df_results) > 0:
    print("\n=== QUICK SWEEP SUMMARY ===")
    summary = df_results.groupby('controller').agg({
        'avg_headway_m': ['mean', 'std', 'min', 'max'],
        'throughput': ['mean', 'std', 'min', 'max']
    }).round(2)
    print(summary)
    
    print("\nSample results:")
    print(df_results[['controller', 'n_trains', 'reaction_s', 'margin_m', 'avg_headway_m', 'throughput']].head(8).to_string(index=False))
else:
    print("No successful runs!")

print("Quick sweep test completed!")