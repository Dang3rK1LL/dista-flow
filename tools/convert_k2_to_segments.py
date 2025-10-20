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

def main():
    assert SRC_XLS.exists(), f"Nem találom: {SRC_XLS}"
    out_dir = OUT_CSV.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    xl = pd.ExcelFile(SRC_XLS)

    # próbáljuk kiválasztani a „leginkább táblázat jellegű” sheetet
    candidates = []
    for s in xl.sheet_names:
        try:
            df = xl.parse(s)
            if df.shape[1] >= 4 and df.dropna(how="all").shape[0] > 5:
                candidates.append((s, df))
        except:
            pass
    assert candidates, "Nem találtam használható munkalapot az XLS fájlban."

    sheet_name, raw = max(candidates, key=lambda x: x[1].shape[0])
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
