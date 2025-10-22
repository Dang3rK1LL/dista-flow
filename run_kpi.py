import pandas as pd, os
from pathlib import Path
from src.model import Line
from src.train import TrainState
from src.controllers import EtcsBaseline, DistaAI_Simple
from src.sim import run_sim
from src.metrics import compute_headways, throughput
from src.plots import headway_hist

os.makedirs('outputs', exist_ok=True)

# Load data with K2 integration
data_options = ['data/etcs_enabled.csv', 'data/k2_all_lines.csv', 'data/segments_mav1.csv', 'data/segments_long.csv', 'data/segments.csv']
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

# ugyanaz a setup, mint a frissített run_mvp-ben
def make_trains(prefix):
    return [
        TrainState(f'{prefix}_T1', pos_m=0.0,    length_m=120, a_max=0.7, a_brake=0.7),
        TrainState(f'{prefix}_T2', pos_m=800.0,  length_m=120, a_max=0.7, a_brake=0.7),
        TrainState(f'{prefix}_T3', pos_m=1600.0, length_m=120, a_max=0.7, a_brake=0.7),
    ]

etcs = make_trains('ETCS')
df_etcs = run_sim(line, etcs, {t.id: EtcsBaseline(2.0, 180.0) for t in etcs}, dt=0.5, T=3600)

dista = make_trains('DISTA')
df_dista = run_sim(line, dista, {t.id: DistaAI_Simple(0.8, 90.0) for t in dista}, dt=0.5, T=3600)

# KPI-k
hw_etcs = compute_headways(df_etcs); hw_dista = compute_headways(df_dista)
headway_hist(hw_etcs, 'outputs/headway_etcs.png')
headway_hist(hw_dista, 'outputs/headway_dista.png')

print("ETCS   átlag headway [m]:", hw_etcs['gap_m'].mean().round(1))
print("DISTA  átlag headway [m]:", hw_dista['gap_m'].mean().round(1))
print("ETCS   throughput [db vonat]:", throughput(df_etcs, line.total_m))
print("DISTA  throughput [db vonat]:", throughput(df_dista, line.total_m))
