# 🚂 DISTA-Flow Futtatási Útmutató

## 🎯 Gyors Start (3 lépés)

### 1️⃣ Adatok előkészítése
```bash
# Python environment aktiválása (ha szükséges)
D:/Programming/dista-flow/.venv/Scripts/python.exe

# K2 adatok letöltése és ETCS szűrés
D:/Programming/dista-flow/.venv/Scripts/python.exe tools/update_k2_data.py
```

### 2️⃣ Interaktív UI indítása
```bash
# Streamlit alkalmazás indítása
D:/Programming/dista-flow/.venv/Scripts/python.exe -m streamlit run app.py
```

### 3️⃣ Kepler.gl vizualizáció
- Böngészőben nyissa meg: http://localhost:8501
- Válasszon railway line-t és futtassa a szimulációt
- Töltse fel a generált GeoJSON fájlokat a [kepler.gl](https://kepler.gl/)-be

---

## 📊 Kepler.gl Integráció - Lépésről Lépésre

### A. GeoJSON Fájlok Generálása

1. **Streamlit UI-ban futtatás:**
   - Válasszon egy ETCS-enabled vonalat
   - Állítsa be a paramétereket (vonat szám, szimuláció idő)
   - Kattintson a "🚀 Run Simulation" gombra

2. **Parancssorból futtatás:**
```bash
# Teljes MVP futtatás GeoJSON exporttal
D:/Programming/dista-flow/.venv/Scripts/python.exe run_mvp_geo.py

# Vagy egyedi vonal futtatása
D:/Programming/dista-flow/.venv/Scripts/python.exe run_mvp.py
```

### B. Kepler.gl Megnyitása

1. **Böngészőben:** [kepler.gl](https://kepler.gl/)
2. **Fájlok feltöltése:** Drag & drop a generált GeoJSON fájlokat

### C. Rétegek Konfigurálása

#### 🛤️ Railway Segments Layer
- **Fájl:** `railway_segments.geojson`
- **Layer Type:** Line
- **Color:** Blue (#1f77b4)
- **Width:** 3-5 pixels
- **Tooltip:** `line_name`, `length_km`, `etcs_equipped`

#### 🚂 Train Movements Layer
- **Fájl:** `train_movements.geojson` 
- **Layer Type:** Point
- **Color by:** `speed` (heatmap)
- **Size by:** `speed` 
- **Animated:** Enable time animation
- **Time Field:** `timestamp`

### D. Animáció Beállítása

1. **Time Control Panel:** Bal alsó sarokban
2. **Animation Speed:** 1x - 10x
3. **Time Window:** 30 minutes - 2 hours
4. **Loop:** Enable for continuous playback

---

## 🔧 Alternatív Futtatási Módok

### 1. Csak Szimuláció (terminál)
```bash
# Egyszerű MVP futtatás
D:/Programming/dista-flow/.venv/Scripts/python.exe run_mvp.py

# KPI analízis
D:/Programming/dista-flow/.venv/Scripts/python.exe run_kpi.py
```

### 2. K2 Adatok Frissítése
```bash
# Standalone K2 update
D:/Programming/dista-flow/.venv/Scripts/python.exe tools/update_k2_data.py
```

### 3. Fejlesztői Módok
```bash
# Parameter sweep futtatás
D:/Programming/dista-flow/.venv/Scripts/python.exe run_sweep.py

# Egyedi controller tesztelés
D:/Programming/dista-flow/.venv/Scripts/python.exe -c "
from src.controllers.ai_controllers import create_controller
controller = create_controller('DistaAI_Predictive')
print(controller.get_control_action(80, 0.5))
"
```

---

## 📁 Generált Fájlok

### GeoJSON Vizualizációs Fájlok
- `railway_segments.geojson` - Vasútvonalak geometriája
- `etcs_train_movements.geojson` - ETCS vonatok mozgása
- `dista_train_movements.geojson` - DISTA kontrollerrel irányított vonatok

### Adatbázis Fájlok
- `data/etcs_enabled.csv` - ETCS-equipped vonalak listája
- `data/k2_meta.json` - K2 adatok metainfó
- `data/segments_*.csv` - Vonali szegmens adatok

### Szimuláció Eredmények
- `simulation_results.csv` - Részletes szimulációs eredmények
- `kpi_analysis.json` - Teljesítménymutatók

---

## 🎨 Kepler.gl Konfigurációs Tippek

### Színpaletta Javaslatok
- **Railway Lines:** Blue gradients (#1f77b4 → #aec7e8)
- **ETCS Trains:** Green heatmap (#2ca02c → #98df8a) 
- **DISTA Trains:** Orange heatmap (#ff7f0e → #ffbb78)
- **Speed Visualization:** Red-Yellow-Green (#d62728 → #ffff00 → #2ca02c)

### Teljesítmény Optimalizálás
- **Nagy adathalmazokhoz:** Csökkentse a point size-t
- **Smooth animation:** 30-60 fps setting
- **Memory optimization:** Használjon time window filtering-et

### Exportálási Lehetőségek
- **PNG/JPG:** Statikus képek
- **GIF:** Animált export
- **HTML:** Interaktív megosztáshoz
- **JSON:** Konfiguráció mentése

---

## ❗ Hibakeresés

### Gyakori Problémák

1. **"No ETCS data found"**
   - Futassa: `python tools/update_k2_data.py`

2. **"Import could not be resolved"**
   - Ellenőrizze a Python environment aktiválást
   - Telepítse: `pip install -r requirements.txt`

3. **GeoJSON fájlok üresek**
   - Ellenőrizze a szimuláció eredményeit
   - Futtassa újra a teljes pipeline-t

4. **Kepler.gl nem tölti be a fájlokat**
   - Ellenőrizze a GeoJSON szintaxist
   - Próbálja kisebb fájlmérettel

### Logolás és Debug
```bash
# Debug módban futtatás
D:/Programming/dista-flow/.venv/Scripts/python.exe -u run_mvp_geo.py

# Streamlit debug információ
D:/Programming/dista-flow/.venv/Scripts/python.exe -m streamlit run app.py --logger.level=debug
```