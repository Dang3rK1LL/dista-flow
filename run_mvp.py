import pandas as pd
import os
from pathlib import Path
from src.model import Line
from src.train import TrainState
from src.controllers import EtcsBaseline, DistaAI_Simple
from src.sim import run_sim
from src.plots import time_distance

# Create outputs directory
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

# ===== ETCS baseline =====
etcs_trains = [
    TrainState('ETCS_T1', pos_m=0.0,    length_m=120, a_max=0.7, a_brake=0.7),
    TrainState('ETCS_T2', pos_m=800.0,  length_m=120, a_max=0.7, a_brake=0.7),
    TrainState('ETCS_T3', pos_m=1600.0, length_m=120, a_max=0.7, a_brake=0.7),
]
etcs_ctrl = {t.id: EtcsBaseline(reaction_s=2.0, margin_m=180.0) for t in etcs_trains}
df_etcs = run_sim(line, etcs_trains, etcs_ctrl, dt=0.5, T=3600)
time_distance(df_etcs, 'outputs/time_distance_etcs.png')

# ===== DISTA (agresszívebb, de shieldelt) =====
dista_trains = [
    TrainState('DISTA_T1', pos_m=0.0,    length_m=120, a_max=0.7, a_brake=0.7),
    TrainState('DISTA_T2', pos_m=800.0,  length_m=120, a_max=0.7, a_brake=0.7),
    TrainState('DISTA_T3', pos_m=1600.0, length_m=120, a_max=0.7, a_brake=0.7),
]
dista_ctrl = {t.id: DistaAI_Simple(reaction_s=0.8, margin_m=90.0) for t in dista_trains}
df_dista = run_sim(line, dista_trains, dista_ctrl, dt=0.5, T=3600)
time_distance(df_dista, 'outputs/time_distance_dista.png')
print("Új grafikonok mentve: outputs/time_distance_*.png")
