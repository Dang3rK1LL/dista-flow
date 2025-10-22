# 🗺️ Kepler.gl Integráció - Teljes Útmutató

## 🎯 DISTA-Flow → Kepler.gl Workflow

### ✅ Lépés 1: GeoJSON Fájlok Generálása

```bash
# Opció A: Interaktív UI (Ajánlott)
D:/Programming/dista-flow/.venv/Scripts/python.exe -m streamlit run app.py
# → Böngésző: http://localhost:8501

# Opció B: Parancssorból
D:/Programming/dista-flow/.venv/Scripts/python.exe run_mvp_geo.py
```

### ✅ Lépés 2: Kepler.gl Megnyitása

1. **Böngésző:** [kepler.gl](https://kepler.gl/)
2. **"Get Started" / "Add Data"**

### ✅ Lépés 3: Fájlok Feltöltése

Húzza a következő fájlokat a Kepler.gl-be:

#### 📁 Generált Fájlok (`outputs/` folder):
- **`railway_segments.geojson`** - Vasútvonalak térképe (11 szegmens, 818.3 km)
- **`etcs_train_movements.geojson`** - ETCS vonatok mozgása (21,600 pozíció)
- **`dista_train_movements.geojson`** - DISTA AI vonatok mozgása (21,600 pozíció)
- **`kepler_config.json`** - Előre konfigurált layer beállítások

---

## 🎨 Kepler.gl Konfigurálás

### A. Layer Beállítások

#### 🛤️ **Railway Segments** (Lines)
```json
Layer Type: Line
Data: railway_segments.geojson
Color by: max_speed_kmh (Speed Limit)
Color Scale: Quantile
Color Range: Blue → Green → Red
Stroke Width: 3-5 pixels
Opacity: 0.8
```

#### 🚂 **Train Movements** (Points)
```json
Layer Type: Point  
Data: etcs_train_movements.geojson / dista_train_movements.geojson
Color by: train_id (Train Number)
Size by: speed (Current Speed)
Radius Range: 3-15 pixels
Animation: ENABLED
Time Field: timestamp
```

### B. Animáció Beállítások

1. **Time Control Panel:** Bal alsó sarokban 🕐
2. **Animation Speed:** 1x-10x sebességbeállítás
3. **Time Window:** 30 perc - 2 óra ablakméret
4. **Loop:** Ismétlődő lejátszás engedélyezése

### C. Tooltip Konfiguráció

#### Railway Segments Tooltip:
- `from_station` - Kezdőállomás
- `to_station` - Végállomás  
- `length_km` - Távolság
- `max_speed_kmh` - Max sebesség
- `signalling` - Jelzőrendszer (ETCS L1/L2)

#### Train Movements Tooltip:
- `train_id` - Vonat azonosító
- `speed` - Pillanatnyi sebesség (km/h)
- `timestamp` - Időbélyeg (másodperc)

---

## 🎯 Vizualizációs Lehetőségek

### 1. 🚄 **Teljesítmény Összehasonlítás**
- **ETCS vs DISTA vonatok** melletti lejátszása
- **Sebességprofilok** összehasonlítása
- **Követési távolságok** elemzése

### 2. 📊 **Sebességanalízis**
- **Heatmap:** Sebesség szerinti színkódolás
- **Size mapping:** Gyorsabb vonatok = nagyobb pontok
- **Real-time tracking:** Élő sebesség követés

### 3. 🛤️ **Infrastruktúra Elemzés**
- **ETCS zónák** megjelenítése
- **Sebességlimits** vizualizációja
- **Kritikus szegmensek** azonosítása

### 4. ⏰ **Időalapú Elemzés**
- **Rush hour patterns** csúcsidő minták
- **Delay propagation** késés terjedése
- **Throughput optimization** áteresztőképesség

---

## 🔧 Fejlett Beállítások

### A. Szűrők és Filterek

```javascript
// Csak ETCS L2 vonalak
signalling == "ETCS L2"

// Nagy sebességű vonatok (>100 km/h)
speed > 100

// Időintervallum szűrés
timestamp >= 3600 && timestamp <= 7200
```

### B. Színpaletta Javaslatok

#### Infrastruktúra:
- **ETCS L1:** #2E8B57 (Sea Green)
- **ETCS L2:** #4169E1 (Royal Blue)  
- **Conventional:** #708090 (Slate Gray)

#### Vonatok:
- **Speed Heatmap:** #00FF00 → #FFFF00 → #FF0000
- **Train ID:** Kategoriális színek (Kepler default)
- **Controller Type:** ETCS=#1F77B4, DISTA=#FF7F0E

### C. Performance Optimization

#### Nagy Adathalmazokhoz:
```json
Point Size: 2-8 pixels (kisebb mint 15)
Animation Speed: 2x-5x (nem 10x)
Time Window: 1 hour max
GPU Acceleration: Auto-detect
```

#### Memory Management:
- **Batch Loading:** 10,000 pontok batch-enként  
- **LOD (Level of Detail):** Zoom-based simplification
- **Temporal Filtering:** Csak visible time range

---

## 📤 Export és Megosztás

### A. Statikus Exportok
- **PNG/JPG:** High-resolution képek
- **SVG:** Vektorgrafikus formátum
- **PDF:** Dokumentációhoz

### B. Interaktív Exportok  
- **HTML:** Standalone interactive map
- **JSON Config:** Konfiguráció mentése/betöltése
- **GIF Animation:** Animált exportok

### C. Megosztási Opciók
```bash
# URL Sharing (Kepler.gl Pro)
https://kepler.gl/demo/config-link

# Configuration Export
Save → Download Config → kepler_custom.json

# Embed Code
<iframe src="kepler.gl/embed/..."></iframe>
```

---

## ❗ Hibaelhárítás

### Gyakori Problémák:

#### 1. **"No data loaded"**
```bash
# Ellenőrizze a fájl formátumot
head -5 outputs/railway_segments.geojson

# GeoJSON validáció  
python -c "import json; json.load(open('outputs/railway_segments.geojson'))"
```

#### 2. **"Animation not working"**  
- Ellenőrizze `timestamp` mező típusát (number)
- Time field beállítás: layers → timestamp
- Animation panel engedélyezése

#### 3. **"Points not visible"**
- Zoom out térképen
- Layer visibility check
- Opacity > 0.5 beállítás

#### 4. **"Slow performance"**
- Csökkentse point size-t
- Time window szűkítése  
- GPU acceleration engedélyezése

### Debug Parancsok:
```bash
# GeoJSON fájl méret ellenőrzés
ls -la outputs/*.geojson

# Koordináta validáció
python -c "
import json
data = json.load(open('outputs/railway_segments.geojson'))
print(f'Features: {len(data[\"features\"])}')
print(f'First coordinate: {data[\"features\"][0][\"geometry\"][\"coordinates\"][0]}')
"

# Timestamp range
python -c "
import json
data = json.load(open('outputs/etcs_train_movements.geojson'))
times = [f['properties']['timestamp'] for f in data['features']]
print(f'Time range: {min(times):.1f} - {max(times):.1f} seconds')
"
```

---

## 🌟 Pro Tippek

### 1. **Layer Order Optimization**
```
Bottom → Top:
1. Railway Segments (lines)
2. Speed Zones (polygons) 
3. Train Movements (points)
4. Labels (text)
```

### 2. **Animation Best Practices**
- **Pre-buffer:** 30 másodperc előtöltés
- **Smooth playback:** 30-60 FPS target
- **Loop seamlessly:** Start/end position egyeztetése

### 3. **Data Storytelling**
- **Sequential reveals:** Layerek fokozatos bekapcsolása
- **Temporal focus:** Kritikus events highlighting
- **Comparative views:** Split screen ETCS vs DISTA

### 4. **Custom Interactions**
```javascript
// Onclick event handling
map.on('click', 'train-layer', (e) => {
  console.log('Train data:', e.features[0].properties);
});

// Custom tooltip
tooltip: {
  format: {
    speed: (value) => `${value.toFixed(1)} km/h`,
    timestamp: (value) => new Date(value * 1000).toLocaleTimeString()
  }
}
```

---

## 🔗 Hasznos Linkek

- **Kepler.gl Docs:** [docs.kepler.gl](https://docs.kepler.gl/)
- **GeoJSON Spec:** [geojson.org](https://geojson.org/)
- **MapBox GL:** [docs.mapbox.com/mapbox-gl-js](https://docs.mapbox.com/mapbox-gl-js/)
- **Deck.gl:** [deck.gl](https://deck.gl/) (Kepler.gl engine)

---

## 📊 Példa Eredmények

```
✅ Generated Files:
   📁 railway_segments.geojson (11 segments, 818.3 km total)
   📁 etcs_train_movements.geojson (21,600 positions, 3 trains)  
   📁 dista_train_movements.geojson (21,600 positions, 3 trains)
   📁 kepler_config.json (Pre-configured layers)

✅ Visualization Stats:
   🚂 Total Trains: 6 (3 ETCS + 3 DISTA)
   ⏱️ Simulation Time: 6 hours (21,600 seconds)
   📍 Position Updates: 43,200 total points
   🛤️ Railway Network: 5 ETCS lines covered
```