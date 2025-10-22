#!/usr/bin/env python3
"""
DISTA-Flow Parameter Sweep
Optimized parameter testing for reaction times, margins, and train counts
"""
import pandas as pd
import os
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from model import Line
from train import TrainState
from controllers import EtcsBaseline, DistaAI_Simple
from sim import run_sim
from metrics import compute_headways, throughput

def load_data():
    """Load railway data with fallback logic"""
    data_options = [
        'data/etcs_enabled.csv', 
        'data/segments_mav1.csv', 
        'data/segments_long.csv', 
        'data/segments.csv'
    ]
    
    for segments_file in data_options:
        if Path(segments_file).exists():
            print(f"Using data file: {segments_file}")
            return pd.read_csv(segments_file)
    
    raise FileNotFoundError("No segments data file found!")

def create_trains(n_trains: int, prefix: str, spacing_m: float = 1000):
    """Create train fleet with specified spacing"""
    return [
        TrainState(f'{prefix}_T{i+1}', pos_m=i*spacing_m, length_m=120, a_max=0.7, a_brake=0.7)
        for i in range(n_trains)
    ]

def run_scenario(line: Line, n_trains: int, reaction_s: float, margin_m: float, controller_type: str = 'ETCS'):
    """Run single scenario and return metrics"""
    trains = create_trains(n_trains, controller_type)
    
    if controller_type == 'ETCS':
        controllers = {t.id: EtcsBaseline(reaction_s=reaction_s, margin_m=margin_m) for t in trains}
    else:
        controllers = {t.id: DistaAI_Simple(reaction_s=reaction_s, margin_m=margin_m) for t in trains}
    
    # Run simulation
    df = run_sim(line, trains, controllers, dt=0.5, T=3600)
    
    # Compute metrics
    headways = compute_headways(df)
    thru = throughput(df, line.total_m)
    
    return {
        'controller': controller_type,
        'n_trains': n_trains,
        'reaction_s': reaction_s,
        'margin_m': margin_m,
        'avg_headway_m': float(headways.mean()) if len(headways) > 0 else 0,
        'min_headway_m': float(headways.min()) if len(headways) > 0 else 0,
        'throughput': thru,
        'completed_trains': len(df[df.get('finished', False) == True]['id'].unique())
    }

def main():
    """Run parameter sweep"""
    os.makedirs('outputs', exist_ok=True)
    
    # Load data
    segments = load_data()
    line = Line(segments)
    
    print(f"Line length: {line.total_m/1000:.1f} km")
    
    # Parameter ranges (optimized for faster execution)
    reaction_times = [1.0, 1.5, 2.0, 2.5]
    margins = [100, 150, 200, 250]
    train_counts = [2, 3, 4, 5]
    controllers = ['ETCS', 'DISTA']
    
    print("Starting parameter sweep...")
    results = []
    
    total_scenarios = len(reaction_times) * len(margins) * len(train_counts) * len(controllers)
    scenario_count = 0
    
    for controller_type in controllers:
        for n_trains in train_counts:
            for reaction_s in reaction_times:
                for margin_m in margins:
                    scenario_count += 1
                    print(f"[{scenario_count}/{total_scenarios}] {controller_type}: n={n_trains}, reaction={reaction_s}s, margin={margin_m}m")
                    
                    try:
                        result = run_scenario(line, n_trains, reaction_s, margin_m, controller_type)
                        results.append(result)
                        print(f"  Result: headway={result['avg_headway_m']:.1f}m, throughput={result['throughput']:.1f}")
                    except Exception as e:
                        print(f"  Error: {e}")
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv('outputs/parameter_sweep_results.csv', index=False)
    
    # Summary analysis
    print("\n📊 Parameter Sweep Summary:")
    for controller in controllers:
        controller_data = results_df[results_df['controller'] == controller]
        if not controller_data.empty:
            best_result = controller_data.loc[controller_data['throughput'].idxmax()]
            print(f"\n{controller} Best Configuration:")
            print(f"  Trains: {best_result['n_trains']}")
            print(f"  Reaction: {best_result['reaction_s']}s")
            print(f"  Margin: {best_result['margin_m']}m")
            print(f"  Throughput: {best_result['throughput']:.2f} trains/hour")
            print(f"  Avg Headway: {best_result['avg_headway_m']:.1f}m")
    
    print(f"\n✅ Parameter sweep completed! Results saved to outputs/parameter_sweep_results.csv")

if __name__ == "__main__":
    main()