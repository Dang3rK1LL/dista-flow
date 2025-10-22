# DISTA-Flow 🚄

**Distance Intelligence System for Train Autonomy - Railway Capacity Simulation Framework**

## 🎯 Project Vision

DISTA-Flow aims to empirically demonstrate through simulation **how much railway network capacity can be increased** when ETCS fixed safety margins are replaced by dynamic, AI-assisted train following logic.

**Goal**: Provide quantitative evidence that AI-driven adaptive train spacing (DISTA) can significantly improve throughput compared to traditional ETCS baseline operations, using real Hungarian railway topology data.

## 🧩 Architecture Overview

```
ETCS Baseline          vs.          DISTA AI-Enhanced
┌─────────────────┐                ┌─────────────────┐
│ Fixed margins   │                │ Dynamic margins │
│ Static reaction │       →        │ Predictive AI   │
│ Conservative    │                │ Optimized flow  │
└─────────────────┘                └─────────────────┘
      ↓                                     ↓
 Lower capacity                      Higher capacity
 Larger headways                     Smaller headways
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Windows/PowerShell environment (tested)
- Virtual environment recommended

### Installation

```powershell
# Clone and setup
git clone https://github.com/Dang3rK1LL/dista-flow.git
cd dista-flow

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate demo railway data (K2 file is corrupted, so we use demo)
python tools/convert_k2_to_segments.py
```

### Run MVP Scenarios

```powershell
# Quick comparison: ETCS vs DISTA with 3 trains
python run_mvp.py
# → Generates: outputs/time_distance_*.png

# Detailed KPI analysis with headway distributions
python run_kpi.py
# → Generates: outputs/headway_*.png
# → Console: Average headway and throughput metrics

# Parameter sweep across reaction times, margins, train counts
python run_sweep.py
# → Generates: outputs/sweep_summary.csv, outputs/sweep_analysis.png
```

## 📊 Expected Results (MVP)

Based on the current mathematical model:

| Metric | ETCS Baseline | DISTA AI | Improvement |
|--------|---------------|----------|-------------|
| Avg Headway | ~1088m | ~959m | **~12% reduction** |
| Throughput | Baseline | Higher | **10-15% increase** |
| Safety | Conservative | Optimized | Maintained |

## 🗂 Project Structure

```
dista-flow/
├── data/
│   ├── segments.csv           # Demo short line
│   ├── segments_long.csv      # Demo long line  
│   └── segments_mav1.csv      # Generated Hungarian Line 1 (184km)
├── src/
│   ├── model.py              # Line topology & speed limits
│   ├── train.py              # Train physics & state
│   ├── controllers.py        # ETCS vs DISTA algorithms
│   ├── sim.py                # Discrete-time simulation engine
│   ├── metrics.py            # KPI calculations (headway, throughput)
│   ├── plots.py              # Time-distance & headway visualizations
│   └── export_geo.py         # Future: GeoJSON for Kepler.gl
├── tools/
│   └── convert_k2_to_segments.py  # VPE K2 → CSV converter
├── outputs/                  # Generated plots & results
├── run_mvp.py               # Quick ETCS vs DISTA demo
├── run_kpi.py               # Detailed KPI analysis
├── run_sweep.py             # Parameter space exploration
└── test_basic.py            # Unit tests
```

## 🔬 Data Sources

### Current: Demo Data
- **Budapest-Sopron corridor** (184 km, 8 segments)
- Speeds: 100-140 km/h, mostly double-track
- ETCS signalling throughout

### Target: Real VPE K2 EHÜSZ Data
- Hungarian railway network (Lines 1-140)
- Station positions, track speeds, signalling
- Grades, slow orders, track restrictions

## 🤖 AI Evolution Roadmap

### Phase 1: Mathematical Model (✅ Current)
```python
# ETCS: Fixed safety distance
d_safe = v²/(2*a_brake) + reaction_time*v + fixed_margin

# DISTA: Reduced margins with intelligent prediction
d_safe = v²/(2*a_brake) + dynamic_reaction*v + adaptive_margin
```

### Phase 2: Machine Learning (🔄 Next)
```python
# XGBoost/LightGBM model predicting optimal following distance
features = [speed, acceleration, leader_speed, track_grade, weather]
d_safe = ai_model.predict(features)
```

### Phase 3: Real-time Optimization (🎯 Future)
- Multi-train coordination
- Traffic flow optimization
- Predictive maintenance integration

## 📈 Key Performance Indicators

| KPI | Description | Research Value |
|-----|-------------|----------------|
| **Headway Distribution** | Gap between consecutive trains | Shows safety margin optimization |
| **Throughput (TPH)** | Trains per hour through bottleneck | Direct capacity measurement |
| **Speed Variance** | Smoothness of train flow | Passenger comfort & efficiency |
| **Delay Propagation** | How disturbances spread | System stability |
| **Occupancy Ratio** | Track utilization percentage | Infrastructure efficiency |

## 🛠 Development Status

- ✅ **MVP Complete**: ETCS vs DISTA comparison working
- ✅ **Robust Error Handling**: Empty dataframes, file I/O, parameter validation
- ✅ **Unit Testing**: Core components validated
- ✅ **Parameter Sweeps**: Systematic exploration of control parameters
- 🔄 **K2 Integration**: Working on robust real data import
- 🔄 **AI Preparation**: Logging framework for ML training data
- 🎯 **Visualization**: Kepler.gl integration planned

## 🧪 Testing & Validation

```powershell
# Run unit tests
python test_basic.py

# Quick validation sweep
python test_sweep.py

# Full parameter exploration (may take hours)
python run_sweep.py
```

## 📚 Research Applications

### Academic Use Cases
- **TDK/OTDK Projects**: Railway capacity optimization research
- **Transportation Engineering**: AI in rail traffic management
- **Operations Research**: Multi-agent system optimization

### Industry Relevance
- **MÁV-Rail**: Hungarian railway capacity planning
- **EU-Rail**: European railway digitalization initiatives
- **ETCS Evolution**: Next-generation train control systems

## 🎨 Visualization Examples

### Time-Distance Diagrams
- **X-axis**: Time (minutes)
- **Y-axis**: Distance along line (km)
- **Lines**: Individual train trajectories
- **Colors**: ETCS (conservative) vs DISTA (optimized)

### Headway Distributions
- **Histogram**: Gap distances between trains
- **Comparison**: ETCS vs DISTA safety margins
- **Metrics**: Mean, P95 percentile, standard deviation

## 🔧 Configuration

Key simulation parameters in each script:

```python
# Train characteristics
length_m = 120        # Train length
a_max = 0.7          # Max acceleration [m/s²]
a_brake = 0.7        # Braking capability [m/s²]

# Controller parameters
reaction_s = 2.0     # ETCS reaction time
margin_m = 180       # ETCS safety margin
dt = 0.5            # Simulation time step [s]
T = 3600            # Total simulation time [s]
```

## 🤝 Contributing

This is a research project. Contributions welcome in:
- **Data Integration**: More realistic railway topology
- **AI Models**: Advanced train following algorithms  
- **Visualization**: Better plotting and geographic display
- **Validation**: Comparison with real-world data

## 📖 Technical Notes

### Simulation Engine
- **Discrete-time**: Fixed time steps (0.5s default)
- **Physics**: Simplified point-mass dynamics
- **Safety**: Non-negative speed/position constraints
- **Finish Detection**: Trains completing full line distance

### Controller Interface
```python
def desired_speed(self, me: TrainState, leader: TrainState, line: Line) -> float:
    """Return target speed based on current situation"""
    pass
```

### Data Format
```csv
from_name,to_name,length_km,speed_kmh,tracks,signalling
Budapest-Kelenföld,Érd,15.2,120,2,ETCS
```

## 📄 License

MIT License - see LICENSE file for details.

## 🎯 Project Goals Summary

> **"Demonstrate that AI-assisted train spacing can increase railway capacity by 10-30% while maintaining safety, using empirical simulation on real Hungarian railway topology."**

---

**Built with** 🐍 Python | 📊 Pandas/NumPy | 🎨 Matplotlib | 🚄 SimPy

**Research Focus**: Railway Capacity Optimization • AI in Transportation • ETCS Evolution
