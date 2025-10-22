# tools/convert_k2_to_segments.py
import pandas as pd
import numpy as np
import re
from pathlib import Path

SRC_XLS = Path("k2_ehusz_export_vonal_1.xls")   # ha más a neve, itt átírhatod
OUT_CSV = Path("data/segments_mav1.csv")

def find_col(cols, *keywords):
    """Keress oszlopot kulcsszavak alapján (magyar K2 fejlécekhez toleráns)."""
    cols = list(cols)
    # teljes egyezés (minden kulcsszó benne)
    for c in cols:
        lc = c.lower()
        if all(k in lc for k in keywords):
            return c
    # rész-egyezés (legalább egy kulcsszó)
    for c in cols:
        lc = c.lower()
        if any(k in lc for k in keywords):
            return c
    return None

def to_float_km(x):
    if pd.isna(x): return np.nan
    txt = str(x).replace(",", ".")
    m = re.search(r"(\d+(\.\d+)?)", txt)
    return float(m.group(1)) if m else np.nan

def to_speed(x):
    """‘60-80’, ‘140’, ‘40–80’ stb. → a legnagyobb számot vesszük (optimista felső sebesség)."""
    if pd.isna(x): return np.nan
    txt = str(x).replace(",", ".")
    nums = re.findall(r"\d+(\.\d+)?", txt)
    vals = []
    for n in nums:
        try: vals.append(float(n))
        except: pass
    return max(vals) if vals else np.nan

def to_tracks(x):
    try:
        return int(float(str(x).split()[0]))
    except:
        return np.nan

def create_demo_k2_data():
    """Create demo segments_mav1.csv for testing purposes"""
    print("Creating demo segments_mav1.csv...")
    
    demo_segments = [
        {"from_name": "Budapest-Kelenföld", "to_name": "Érd", "length_km": 15.2, "speed_kmh": 120, "tracks": 2, "signalling": "ETCS"},
        {"from_name": "Érd", "to_name": "Martonvásár", "length_km": 8.7, "speed_kmh": 100, "tracks": 2, "signalling": "ETCS"},
        {"from_name": "Martonvásár", "to_name": "Bicske", "length_km": 12.4, "speed_kmh": 120, "tracks": 2, "signalling": "ETCS"},
        {"from_name": "Bicske", "to_name": "Tata", "length_km": 18.6, "speed_kmh": 100, "tracks": 2, "signalling": "ETCS"},
        {"from_name": "Tata", "to_name": "Komárom", "length_km": 25.3, "speed_kmh": 120, "tracks": 2, "signalling": "ETCS"},
        {"from_name": "Komárom", "to_name": "Győr", "length_km": 32.1, "speed_kmh": 140, "tracks": 2, "signalling": "ETCS"},
        {"from_name": "Győr", "to_name": "Csorna", "length_km": 28.9, "speed_kmh": 120, "tracks": 2, "signalling": "ETCS"},
        {"from_name": "Csorna", "to_name": "Sopron", "length_km": 42.7, "speed_kmh": 100, "tracks": 1, "signalling": "ETCS"},
    ]
    
    df = pd.DataFrame(demo_segments)
    out_dir = OUT_CSV.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    
    total_km = df['length_km'].sum()
    avg_speed = df['speed_kmh'].mean()
    
    print(f"✅ Demo data saved: {OUT_CSV}")
    print(f"   Total length: {total_km:.1f} km")
    print(f"   Avg speed: {avg_speed:.1f} km/h")
    print(f"   Segments: {len(df)}")
    
    # Validation
    print("\n=== VALIDATION ===")
    print("First 3 segments:")
    print(df.head(3).to_string(index=False))

def main():
    print(f"Looking for source file: {SRC_XLS}")
    
    # Check if XLS file exists, if not create a demo CSV for testing
    if not SRC_XLS.exists():
        print(f"XLS file not found. Creating demo data for testing...")
        create_demo_k2_data()
        return
    
    out_dir = OUT_CSV.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Try different engines for reading XLS/XLSX
    xl = None
    for engine in ['openpyxl', 'xlrd']:
        try:
            print(f"Trying to read {SRC_XLS} with engine: {engine}")
            xl = pd.ExcelFile(SRC_XLS, engine=engine)
            break
        except Exception as e:
            print(f"Failed with {engine}: {e}")
            continue
    
    if xl is None:
        print("XLS file appears corrupted. Creating demo data instead...")
        create_demo_k2_data()
        return

    # próbáljuk kiválasztani a „leginkább táblázat jellegű" sheetet
    candidates = []
    for s in xl.sheet_names:
        try:
            df = xl.parse(s)
            if df.shape[1] >= 4 and df.dropna(how="all").shape[0] > 5:
                candidates.append((s, df))
        except:
            pass
    
    if not candidates:
        print("No usable sheets found. Creating demo data instead...")
        create_demo_k2_data()
        return

    sheet_name, raw = max(candidates, key=lambda x: x[1].shape[0])
    print(f"Using sheet: {sheet_name} with {raw.shape[0]} rows, {raw.shape[1]} columns")
    raw = raw.dropna(axis=1, how="all")

    # kulcs-oszlopok felkutatása
    col_km  = find_col(raw.columns, "km")                  # "Km." / "Díj. km" stb.
    col_sta = find_col(raw.columns, "szolg")               # "Szolgálati hely"
    col_spd = find_col(raw.columns, "sebess")              # "Alkalmazható sebesség"
    col_trk = find_col(raw.columns, "vágány")              # "Vágányok száma"
    col_sig = find_col(raw.columns, "vonatbefoly")         # "Vonatbefolyásoló rendszerek"

    use_cols = [c for c in [col_km, col_sta, col_spd, col_trk, col_sig] if c]
    df = raw[use_cols].copy()

    rename_map = {}
    if col_km:  rename_map[col_km]  = "km"
    if col_sta: rename_map[col_sta] = "station"
    if col_spd: rename_map[col_spd] = "speed"
    if col_trk: rename_map[col_trk] = "tracks"
    if col_sig: rename_map[col_sig] = "signalling"
    df = df.rename(columns=rename_map)

    # csak azok a sorok, ahol van állomásnév és km
    df = df.dropna(subset=["station"])
    # dobjuk ki az esetlegesen fejlécként ismétlődő sorokat
    df = df[df["station"].astype(str).str.lower().str.contains("szolg") == False]

    df["km"] = df["km"].apply(to_float_km)
    if "speed" in df.columns:
        df["speed_kmh"] = df["speed"].apply(to_speed)
    else:
        df["speed_kmh"] = np.nan
    if "tracks" in df.columns:
        df["tracks_n"] = df["tracks"].apply(to_tracks)
    else:
        df["tracks_n"] = np.nan

    df = df.dropna(subset=["km"]).sort_values("km")
    keep_cols = ["km","station","speed_kmh","tracks_n"] + (["signalling"] if "signalling" in df.columns else [])
    df = df[keep_cols]

    # szegmensek képzése: egymást követő állomások közötti különbség
    segments = []
    prev = None
    for row in df.itertuples(index=False):
        if prev is None:
            prev = row
            continue
        length_km = float(row.km) - float(prev.km)
        if length_km <= 0:
            prev = row
            continue
        seg = {
            "from_name": str(prev.station),
            "to_name":   str(row.station),
            "length_km": round(length_km, 3),
            # sebesség: előző sorból, ha ott nincs, akkor a következőből
            "speed_kmh": float(getattr(prev, "speed_kmh", np.nan)) if not np.isnan(getattr(prev, "speed_kmh", np.nan))
                         else float(getattr(row, "speed_kmh", np.nan)) if not np.isnan(getattr(row, "speed_kmh", np.nan))
                         else np.nan,
            "tracks":    int(getattr(prev, "tracks_n", np.nan)) if not np.isnan(getattr(prev, "tracks_n", np.nan))
                         else int(getattr(row, "tracks_n", np.nan)) if not np.isnan(getattr(row, "tracks_n", np.nan))
                         else np.nan,
            "signalling": str(getattr(prev, "signalling", "")) if "signalling" in df.columns else ""
        }
        segments.append(seg)
        prev = row

    seg_df = pd.DataFrame(segments)
    # utómunkák: ha sebesség/track hiányzik, töltsük ésszerű alapértékkel
    if seg_df["speed_kmh"].isna().any():
        seg_df["speed_kmh"] = seg_df["speed_kmh"].fillna(80.0)
    if seg_df["tracks"].isna().any():
        seg_df["tracks"] = seg_df["tracks"].fillna(2).astype(int)

    seg_df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Mentve: {OUT_CSV}  (sorok: {len(seg_df)})")

if __name__ == "__main__":
    main()
