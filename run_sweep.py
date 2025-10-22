#!/usr/bin/env python3
"""
Parameter sweep script for DISTA-Flow
Tests different reaction times, margins, and train counts
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
    raise FileNotFoundError("No segments data file found! Try running tools/convert_k2_to_segments.py first.")

print(f"Using data file: {segments_file}")
segments = pd.read_csv(segments_file)
line = Line(segments)

def make_trains(n_trains, prefix, spacing_m=800):
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
    
    df = run_sim(line, trains, controllers, dt=0.5, T=3600)
    
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
        'line_length_km': line.total_m / 1000.0
    }

# Parameter ranges for sweep
reaction_times = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
margins = [50, 100, 150, 200, 250]
train_counts = [2, 3, 4, 5]

print("Starting parameter sweep...")
results = []

total_runs = len(reaction_times) * len(margins) * len(train_counts) * 2  # *2 for ETCS+DISTA
current_run = 0

for n_trains in train_counts:
    for reaction_s in reaction_times:
        for margin_m in margins:
            current_run += 1
            print(f"Run {current_run}/{total_runs}: n={n_trains}, reaction={reaction_s}s, margin={margin_m}m")
            
            # ETCS baseline
            try:
                result_etcs = run_scenario(n_trains, reaction_s, margin_m, 'ETCS')
                results.append(result_etcs)
            except Exception as e:
                print(f"  ETCS failed: {e}")
            
            current_run += 1
            print(f"Run {current_run}/{total_runs}: n={n_trains}, reaction={reaction_s}s, margin={margin_m}m")
            
            # DISTA
            try:
                result_dista = run_scenario(n_trains, reaction_s, margin_m, 'DISTA')
                results.append(result_dista)
            except Exception as e:
                print(f"  DISTA failed: {e}")

# Save results
df_results = pd.DataFrame(results)
df_results.to_csv('outputs/sweep_summary.csv', index=False)
print(f"Results saved to outputs/sweep_summary.csv ({len(results)} rows)")

# Create visualization
if len(df_results) > 0:
    # Headway vs reaction time plot
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    for controller in ['ETCS', 'DISTA']:
        data = df_results[df_results['controller'] == controller]
        if len(data) > 0:
            grouped = data.groupby('reaction_s')['avg_headway_m'].mean()
            plt.plot(grouped.index, grouped.values, 'o-', label=controller)
    plt.xlabel('Reaction Time [s]')
    plt.ylabel('Avg Headway [m]')
    plt.title('Headway vs Reaction Time')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 2, 2)
    for controller in ['ETCS', 'DISTA']:
        data = df_results[df_results['controller'] == controller]
        if len(data) > 0:
            grouped = data.groupby('margin_m')['avg_headway_m'].mean()
            plt.plot(grouped.index, grouped.values, 'o-', label=controller)
    plt.xlabel('Margin [m]')
    plt.ylabel('Avg Headway [m]')
    plt.title('Headway vs Margin')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 2, 3)
    for controller in ['ETCS', 'DISTA']:
        data = df_results[df_results['controller'] == controller]
        if len(data) > 0:
            grouped = data.groupby('n_trains')['throughput'].mean()
            plt.plot(grouped.index, grouped.values, 'o-', label=controller)
    plt.xlabel('Number of Trains')
    plt.ylabel('Throughput [trains]')
    plt.title('Throughput vs Train Count')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 2, 4)
    # Scatter: headway vs throughput
    for controller in ['ETCS', 'DISTA']:
        data = df_results[df_results['controller'] == controller]
        plt.scatter(data['avg_headway_m'], data['throughput'], 
                   label=controller, alpha=0.6)
    plt.xlabel('Avg Headway [m]')
    plt.ylabel('Throughput [trains]')
    plt.title('Throughput vs Headway')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('outputs/sweep_analysis.png', dpi=160, bbox_inches='tight')
    plt.close()
    
    print("Analysis plots saved to outputs/sweep_analysis.png")
    
    # Summary statistics
    print("\n=== SWEEP SUMMARY ===")
    summary = df_results.groupby('controller').agg({
        'avg_headway_m': ['mean', 'std', 'min', 'max'],
        'throughput': ['mean', 'std', 'min', 'max']
    }).round(2)
    print(summary)
else:
    print("No successful runs to plot!")

print("Parameter sweep completed!")