#!/usr/bin/env python3
"""
Enhanced MVP with GeoJSON export for Kepler.gl visualization
"""
import pandas as pd
import os
import sys
from pathlib import Path
from src.model import Line
from src.train import TrainState
from src.controllers import EtcsBaseline, DistaAI_Simple
from src.sim import run_sim
from src.plots import time_distance

# Add visualization module
sys.path.append(str(Path(__file__).parent))
from src.visualization.geojson_exporter import GeoJSONExporter

# Create outputs directory
os.makedirs('outputs', exist_ok=True)

# Load data with K2 integration
data_options = ['data/etcs_enabled.csv', 'data/k2_all_lines.csv', 'data/segments_mav1.csv', 'data/segments_long.csv', 'data/segments.csv']
segments_file = None
for f in data_options:
    if Path(f).exists():
        segments_file = f
        break

if not segments_file:
    raise FileNotFoundError("No segments data file found! Try running tools/update_k2_data.py first.")

print(f"Using data file: {segments_file}")
segments = pd.read_csv(segments_file)
line = Line(segments)

print(f"Line: {line.total_m/1000:.1f} km total length")

# ===== ETCS baseline =====
etcs_trains = [
    TrainState('ETCS_T1', pos_m=0.0,    length_m=120, a_max=0.7, a_brake=0.7),
    TrainState('ETCS_T2', pos_m=800.0,  length_m=120, a_max=0.7, a_brake=0.7),
    TrainState('ETCS_T3', pos_m=1600.0, length_m=120, a_max=0.7, a_brake=0.7),
]
etcs_ctrl = {t.id: EtcsBaseline(reaction_s=2.0, margin_m=180.0) for t in etcs_trains}
df_etcs = run_sim(line, etcs_trains, etcs_ctrl, dt=0.5, T=3600)
time_distance(df_etcs, 'outputs/time_distance_etcs.png')

# ===== DISTA (aggressive but shielded) =====
dista_trains = [
    TrainState('DISTA_T1', pos_m=0.0,    length_m=120, a_max=0.7, a_brake=0.7),
    TrainState('DISTA_T2', pos_m=800.0,  length_m=120, a_max=0.7, a_brake=0.7),
    TrainState('DISTA_T3', pos_m=1600.0, length_m=120, a_max=0.7, a_brake=0.7),
]
dista_ctrl = {t.id: DistaAI_Simple(reaction_s=0.8, margin_m=90.0) for t in dista_trains}
df_dista = run_sim(line, dista_trains, dista_ctrl, dt=0.5, T=3600)
time_distance(df_dista, 'outputs/time_distance_dista.png')

print("Grafikonok mentve: outputs/time_distance_*.png")

# ===== Export to GeoJSON for Kepler.gl =====
print("\n🗺️ Exporting GeoJSON for Kepler.gl visualization...")

exporter = GeoJSONExporter()

# Export railway segments
segments_geojson = exporter.segments_to_geojson(Path(segments_file))

# Export ETCS simulation
etcs_geojson = exporter.simulation_to_geojson(
    df_etcs, 
    Path(segments_file), 
    Path("outputs/etcs_train_movements.geojson")
)

# Export DISTA simulation  
dista_geojson = exporter.simulation_to_geojson(
    df_dista, 
    Path(segments_file), 
    Path("outputs/dista_train_movements.geojson")
)

# Create Kepler.gl config
config_file = exporter.create_kepler_config(
    segments_geojson, 
    etcs_geojson,
    Path("outputs/kepler_config.json")
)

print("✅ GeoJSON export completed!")
print(f"   Railway segments: {segments_geojson}")
print(f"   ETCS movements: {etcs_geojson}")
print(f"   DISTA movements: {dista_geojson}")
print(f"   Kepler config: {config_file}")
print("\n💡 Upload these files to kepler.gl to visualize the simulation!")