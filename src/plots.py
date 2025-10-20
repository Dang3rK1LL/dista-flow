import matplotlib.pyplot as plt

def time_distance(df, outfile):
    plt.figure(figsize=(8,4))
    for tid, g in df.groupby('id'):
        plt.plot(g['t']/60.0, g['pos_m']/1000.0, label=tid)
    plt.xlabel('Time [min]'); plt.ylabel('Distance [km]'); plt.legend()
    plt.tight_layout(); plt.savefig(outfile, dpi=160); plt.close()

def headway_hist(df_hw, outfile):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(6,4))
    plt.hist(df_hw['gap_m']/1.0, bins=40)
    plt.xlabel('Headway [m]'); plt.ylabel('Count')
    plt.tight_layout(); plt.savefig(outfile, dpi=160); plt.close()
