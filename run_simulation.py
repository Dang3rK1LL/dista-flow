#!/usr/bin/env python3
"""
DISTA-Flow Unified Runner
Comprehensive simulation with GeoJSON export and KPI analysis
"""
import pandas as pd
import os
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from model import Line
from train import TrainState
from controllers import EtcsBaseline, DistaAI_Simple
from sim import run_sim
from plots import time_distance, headway_hist
from metrics import compute_headways, throughput
from visualization.geojson_exporter import GeoJSONExporter

def load_data():
    """Load railway data with fallback logic"""
    data_options = [
        'data/etcs_enabled.csv', 
        'data/k2_all_lines.csv', 
        'data/segments_mav1.csv', 
        'data/segments_long.csv', 
        'data/segments.csv'
    ]
    
    for segments_file in data_options:
        if Path(segments_file).exists():
            print(f"Using data file: {segments_file}")
            return pd.read_csv(segments_file), segments_file
    
    raise FileNotFoundError("No segments data file found! Try running tools/update_k2_data.py first.")

def create_trains(prefix: str, count: int = 3, spacing: int = 800):
    """Create train fleet with specified parameters"""
    return [
        TrainState(f'{prefix}_T{i+1}', pos_m=i*spacing, length_m=120, a_max=0.7, a_brake=0.7)
        for i in range(count)
    ]

def run_simulation(line: Line, mode: str = "comparison", 
                  train_count: int = 3, sim_time: int = 3600):
    """Run simulation based on mode"""
    results = {}
    
    # ETCS Baseline
    etcs_trains = create_trains("ETCS", train_count)
    etcs_ctrl = {t.id: EtcsBaseline(reaction_s=2.0, margin_m=180.0) for t in etcs_trains}
    results['etcs'] = {
        'trains': etcs_trains,
        'data': run_sim(line, etcs_trains, etcs_ctrl, dt=0.5, T=sim_time)
    }
    
    # DISTA Controller
    if mode in ["comparison", "geo", "kpi"]:
        dista_trains = create_trains("DISTA", train_count)
        dista_ctrl = {t.id: DistaAI_Simple(reaction_s=0.8, margin_m=120.0) for t in dista_trains}
        results['dista'] = {
            'trains': dista_trains,
            'data': run_sim(line, dista_trains, dista_ctrl, dt=0.5, T=sim_time)
        }
    
    return results

def generate_plots(results: dict, line: Line):
    """Generate visualization plots"""
    print("📊 Generating plots...")
    
    # Time-distance plots
    for name, result in results.items():
        time_distance(result['data'], f"outputs/time_distance_{name}.png", 
                     f"{name.upper()} Controller", line.total_m/1000)
    
    # Headway analysis
    for name, result in results.items():
        headways = compute_headways(result['data'])
        if len(headways) > 0:
            headway_hist(headways, f"outputs/headway_{name}.png", 
                        f"{name.upper()} Headway Distribution")

def generate_kpi(results: dict, line: Line):
    """Generate KPI analysis"""
    print("📈 Computing KPI metrics...")
    
    kpi_results = {}
    for name, result in results.items():
        headways = compute_headways(result['data'])
        thru = throughput(result['data'], line.total_m)
        
        kpi_results[name] = {
            'avg_headway_m': float(headways.mean()) if len(headways) > 0 else 0,
            'min_headway_m': float(headways.min()) if len(headways) > 0 else 0,
            'throughput_trains_per_hour': thru,
            'simulation_time_hours': result['data']['t'].max() / 3600,
            'completed_trains': len(result['data'][result['data'].get('finished', False) == True]['id'].unique())
        }
    
    # Save KPI results
    import json
    with open('outputs/kpi_analysis.json', 'w') as f:
        json.dump(kpi_results, f, indent=2)
    
    # Print summary
    print("\n📊 KPI Summary:")
    for name, kpi in kpi_results.items():
        print(f"  {name.upper()}:")
        print(f"    Avg Headway: {kpi['avg_headway_m']:.1f}m")
        print(f"    Throughput: {kpi['throughput_trains_per_hour']:.1f} trains/hour")

def generate_geojson(results: dict, segments_file: str):
    """Generate GeoJSON files for Kepler.gl"""
    print("🗺️ Exporting GeoJSON for Kepler.gl...")
    
    exporter = GeoJSONExporter()
    
    # Export railway segments
    segments_geojson = exporter.segments_to_geojson(Path(segments_file))
    
    geojson_files = [segments_geojson]
    
    # Export train movements
    for name, result in results.items():
        output_file = Path(f"outputs/{name}_train_movements.geojson")
        movement_geojson = exporter.simulation_to_geojson(
            result['data'], Path(segments_file), output_file
        )
        geojson_files.append(movement_geojson)
    
    # Create Kepler.gl config
    if len(geojson_files) >= 2:
        config_file = exporter.create_kepler_config(
            geojson_files[0], geojson_files[1], Path("outputs/kepler_config.json")
        )
        geojson_files.append(config_file)
    
    print("✅ GeoJSON export completed!")
    for file in geojson_files:
        print(f"   📁 {file}")

def main():
    parser = argparse.ArgumentParser(description="DISTA-Flow Unified Runner")
    parser.add_argument("--mode", default="full", 
                       choices=["basic", "geo", "kpi", "full"],
                       help="Simulation mode")
    parser.add_argument("--trains", type=int, default=3,
                       help="Number of trains per controller")
    parser.add_argument("--time", type=int, default=3600,
                       help="Simulation time in seconds")
    
    args = parser.parse_args()
    
    # Create outputs directory
    os.makedirs('outputs', exist_ok=True)
    
    # Load data
    segments, segments_file = load_data()
    line = Line(segments)
    
    print(f"📏 Line: {line.total_m/1000:.1f} km total length")
    
    # Run simulation
    results = run_simulation(line, args.mode, args.trains, args.time)
    
    # Generate outputs based on mode
    if args.mode in ["basic", "full"]:
        generate_plots(results, line)
    
    if args.mode in ["kpi", "full"]:
        generate_kpi(results, line)
    
    if args.mode in ["geo", "full"]:
        generate_geojson(results, segments_file)
    
    print(f"\n🎉 Simulation completed! Check outputs/ directory.")
    print("💡 For Kepler.gl visualization, upload GeoJSON files to kepler.gl")

if __name__ == "__main__":
    main()