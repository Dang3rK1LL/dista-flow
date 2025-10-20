import pandas as pd

def compute_headways(df, train_length=120.0):
    hw = []
    for t, g in df.groupby('t'):
        g = g.sort_values('pos_m')
        for i in range(1, len(g)):
            gap = (g.iloc[i]['pos_m'] - g.iloc[i-1]['pos_m']) - train_length
            hw.append(dict(t=t, gap_m=max(gap, 0.0)))
    return pd.DataFrame(hw)

def throughput(df, line_length_m):
    # hány vonat érte el a vonal végét
    finished = df.groupby('id')['pos_m'].max()
    return int((finished >= line_length_m - 1.0).sum())
