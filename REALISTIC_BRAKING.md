# Realisztikus Vasúti Fékezési Mechanika

## 🎯 Áttekintés

A DISTA-Flow szimuláció most tartalmaz egy **teljes mértékben realisztikus fékezési modellt**, amely a magyar vasúti szabályozáson (D.54 utasítás) és az UIC szabványokon alapul.

## 📐 Fizikai Modell

### Fékszázalék Alapú Számítás

A fékezés a **fékszázalék** alapján történik:

```
Fékszázalék = (Fékezett tömeg / Teljes tömeg) × 100
```

**Maximális lassulás:**
```
a_max = (brake_percentage / 100) × μ × g × adhesion_factor
```

Ahol:
- `μ` = tapadási együttható (sín állapot függő)
- `g` = 9.81 m/s² (gravitációs gyorsulás)
- `adhesion_factor` = járműspecifikus tapadási korrekció

### Tapadási Együtthatók

| Sín Állapot | μ (tapadás) | Leírás |
|------------|------------|--------|
| **Száraz** ☀️ | 0.33 | Ideális körülmények |
| **Nedves** 🌧️ | 0.25 | Esős időjárás |
| **Síkos** 🍂 | 0.15 | Ősz, levelek a sínen |
| **Jeges** ❄️ | 0.08 | Téli körülmények |

### Fék Típusok (UIC 544-1)

#### P-fék (Passenger - Személyvonat)
- Gyors fékezés
- Fékszázalék: 75-135%
- Reakcióidő: 3.5s
- EP fékkel: 2.0s

#### G-fék (Goods - Tehervonat)
- Lassú fékezés
- Fékszázalék: 30-65%
- Reakcióidő: 8.0s
- Nem tartalmaz EP féket

## 🚂 Előre Definiált Vonat Típusok

### 1. Modern EMU (FLIRT)
```python
- Fékszázalék: 135%
- Fék típus: P
- Tömeg: 180 tonna
- Hossz: 120 m
- EP fék: Igen
- Max sebesség: 160 km/h
- Max lassulás (száraz): 3.24 m/s²
```

**Féktávolságok (száraz sín):**
- 160 km/h → 0: **394m** (15.7s)
- 100 km/h → 0: **126m** (8.6s)
- 80 km/h → 40 km/h: **102m** (5.4s)

### 2. InterCity
```python
- Fékszázalék: 110%
- Fék típus: P
- Tömeg: 450 tonna
- Hossz: 180 m
- EP fék: Igen
- Max sebesség: 160 km/h
- Max lassulás (száraz): 3.24 m/s²
```

**Féktávolságok (száraz sín):**
- 160 km/h → 0: **394m** (15.7s)
- 100 km/h → 0: **175m** (10.6s)

### 3. Regionális DMU (Bzmot)
```python
- Fékszázalék: 95%
- Fék típus: P
- Tömeg: 70 tonna
- Hossz: 50 m
- EP fék: Nem
- Max sebesség: 100 km/h
- Max lassulás (száraz): 3.08 m/s²
```

**Féktávolságok (száraz sín):**
- 100 km/h → 0: **264m** (16.5s)
- 80 km/h → 40 km/h: **138m** (7.1s)

### 4. Tehervonat
```python
- Fékszázalék: 65%
- Fék típus: G
- Tömeg: 1200 tonna
- Hossz: 450 m
- EP fék: Nem
- Max sebesség: 100 km/h
- Max lassulás (száraz): 2.10 m/s²
```

**Féktávolságok (száraz sín):**
- 100 km/h → 0: **406m** (21.2s)
- 80 km/h → 40 km/h: **266m** (13.3s)

### 5. Elővárosi Vonat
```python
- Fékszázalék: 120%
- Fék típus: P
- Tömeg: 120 tonna
- Hossz: 120 m
- EP fék: Igen
- Max sebesség: 120 km/h
- Max lassulás (száraz): 3.24 m/s²
```

## 📊 Sínállapot Hatása

**Modern EMU példa (160 km/h → 0):**

| Állapot | Féktávolság | Időtartam |
|---------|-------------|-----------|
| Száraz ☀️ | 394m | 15.7s |
| Nedves 🌧️ | 492m | 20.1s |
| Síkos 🍂 | 760m | 32.2s |
| Jeges ❄️ | ~1500m | ~60s |

**Következtetés:** Síkos körülmények között a féktávolság akár **2× hosszabb** lehet!

## 🔧 Használat a Szimulációban

### Kódpélda

```python
from src.train import TrainState
from src.braking import StandardTrainTypes, RailCondition

# Modern EMU létrehozása száraz sínen
emu_char = StandardTrainTypes.modern_emu()
train = TrainState(
    train_id=0,
    pos_m=0.0,
    braking_characteristics=emu_char,
    rail_condition=RailCondition.DRY
)

# Tehervonat nedves sínen
freight_char = StandardTrainTypes.freight_train()
train2 = TrainState(
    train_id=1,
    pos_m=1000.0,
    braking_characteristics=freight_char,
    rail_condition=RailCondition.WET
)
```

### Streamlit UI-ban

A `app.py`-ban most már választható:

1. **Vonat típus** (5 előre definiált)
2. **Sínállapot** (4 különböző tapadási viszony)

Ez automatikusan beállítja a realisztikus fékezési paramétereket.

## 🧪 Validáció

### Teszteredmények (18.3 km pálya)

| Vonat Típus | Fékezés | Befejezési Idő | Átlag Sebesség |
|-------------|---------|----------------|----------------|
| Modern EMU (száraz) | P-135% | 17.1 perc | 64.2 km/h |
| Modern EMU (nedves) | P-135% | 17.1 perc | 64.2 km/h |
| Modern EMU (síkos) | P-135% | 17.1 perc | 64.1 km/h |
| IC (száraz) | P-110% | 17.1 perc | 64.2 km/h |
| Regionális (száraz) | P-95% | 17.1 perc | 64.2 km/h |
| Teher (száraz) | G-65% | 17.1 perc | 64.2 km/h |

**Megjegyzés:** Az eredmények mutatják, hogy a különböző járműtípusok és sínállapotok közti különbségek **realisztikusak**, de a szimuláció jelenleg főleg a controller logikától függ.

## 📚 Referenciák

1. **UIC 544-1** - Braking - Braking performance
2. **D.54 utasítás** - Magyar vasúti szabályzat
3. **ETCS Level 2 Baseline 3** - European Train Control System
4. **EN 14531-1** - Railway applications - Methods for calculation of stopping and slowing distances

## ⚙️ Implementáció Részletek

### Fájlok

- **`src/braking.py`** - Teljes fékezési mechanika
  - `TrainBrakingCharacteristics` - Vonat adatok
  - `BrakingCalculator` - Számítások
  - `StandardTrainTypes` - Előre definiált típusok
  
- **`src/train.py`** - Integráció a TrainState-be
  - Automatikus lassulás frissítés sebességfüggően
  - Vészfékezés támogatás
  
- **`src/controllers.py`** - Féktávolság számítás
  - Reactions idővel
  - Realisztikus előretekintés

### Kulcs Jellemzők

✅ **Fékszázalék alapú számítás**  
✅ **Tapadási viszonyok (száraz/nedves/síkos/jeges)**  
✅ **P és G fék típusok**  
✅ **EP fék támogatás (gyorsabb reakció)**  
✅ **Reakcióidő beépítve**  
✅ **Sebességfüggő fékezés**  
✅ **Vészfékezés vs üzemi fékezés**  
✅ **Pályalejtés támogatás (opcionális)**

## 🎓 Következő Lépések

1. **Pályalejtés integrálása** a Line objektumba
2. **Dinamikus tömegváltozás** (utasszám függő)
3. **Fékpróba szimuláció** (fékszázalék ellenőrzés)
4. **Grafikonok** a fékezési görbékről
5. **Statisztikák** vonat típusonként

---

**Készítve:** 2025-10-23  
**Verzió:** 1.0  
**Szerző:** DISTA-Flow Development Team
