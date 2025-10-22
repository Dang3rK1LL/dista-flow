import pandas as pd
import numpy as np

def compute_headways(df, train_length=120.0):
    """Compute headway gaps between consecutive trains at each time step"""
    if df.empty:
        return pd.DataFrame(columns=['t', 'gap_m'])
    
    # Check required columns
    required_cols = ['t', 'pos_m']
    for col in required_cols:
        if col not in df.columns:
            print(f"Warning: Missing column '{col}' in DataFrame")
            return pd.DataFrame(columns=['t', 'gap_m'])
    
    hw = []
    for t, g in df.groupby('t'):
        if len(g) <= 1:
            continue  # Need at least 2 trains to compute headway
        
        g = g.sort_values('pos_m').reset_index(drop=True)
        for i in range(1, len(g)):
            # Gap = distance between front of train i and rear of train i-1
            gap = g.iloc[i]['pos_m'] - (g.iloc[i-1]['pos_m'] + train_length)
            hw.append(dict(t=t, gap_m=max(gap, 0.0)))
    
    return pd.DataFrame(hw)

def throughput(df, line_length_m):
    """Count how many trains reached the end of the line"""
    if df.empty:
        return 0
    
    finished = df.groupby('id')['pos_m'].max()
    return int((finished >= line_length_m - 1.0).sum())
