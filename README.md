# DISTA-Flow 🚄# DISTA-Flow 🚄



**Advanced Railway Traffic Simulation with AI Controllers****Distance Intelligence System for Train Autonomy - Railway Capacity Simulation Framework**



A comprehensive railway simulation framework with Kepler.gl visualization and K2 EHÜSZ integration for ETCS-equipped Hungarian railway lines.## 🎯 Project Vision



## 🚀 Quick StartDISTA-Flow is a railway simulation framework for studying train following algorithms and their impact on railway operations. The project compares traditional ETCS-based approaches with alternative control strategies.



### 1. Installation**Goal**: Develop and analyze different train control methodologies using simulation on Hungarian railway network data.

```bash

pip install -r requirements.txt## 🧩 Architecture Overview

```

```

### 2. Data SetupETCS Baseline          vs.          Alternative Approach

```bash┌─────────────────┐                ┌─────────────────┐

# Fetch K2 EHÜSZ railway data│ Standard logic  │                │ Modified logic  │

python tools/update_k2_data.py│ Fixed parameters│       →        │ Adaptive params │

```│ Traditional     │                │ Research-based  │

└─────────────────┘                └─────────────────┘

### 3. Interactive Dashboard      ↓                                     ↓

```bash    Baseline                        Experimental

# Launch Streamlit web interface   Performance                       Performance

streamlit run app.py```

# Open: http://localhost:8501

```## 🚀 Quick Start



### 4. Command Line Simulation### Prerequisites

```bash- Python 3.11+

# Full simulation with GeoJSON export- Windows/PowerShell environment (tested)

python run_simulation.py --mode full- Virtual environment recommended



# Specific modes### Installation

python run_simulation.py --mode geo --trains 5 --time 7200

python run_simulation.py --mode kpi --trains 3```powershell

```# Clone and setup

git clone https://github.com/Dang3rK1LL/dista-flow.git

## 🎯 Key Featurescd dista-flow



- **K2 EHÜSZ Integration** - Automatic Hungarian railway data fetching# Create virtual environment

- **ETCS Line Support** - 818.3 km across 5 ETCS-equipped lines  python -m venv .venv

- **AI Controllers** - Predictive and RL-based train control algorithms.venv\Scripts\activate

- **Kepler.gl Visualization** - Interactive train movement animation

- **Performance Analysis** - Headway, throughput, and safety metrics# Install dependencies

pip install -r requirements.txt

## 🗺️ Kepler.gl Visualization

# Generate demo railway data (K2 file is corrupted, so we use demo)

1. Run simulation: `python run_simulation.py --mode geo`python tools/convert_k2_to_segments.py

2. Open [kepler.gl](https://kepler.gl/)```

3. Upload generated GeoJSON files from `outputs/` directory

4. Configure animation and enjoy real-time train visualization!### Run MVP Scenarios



## 🗂 Project Structure```powershell

# Quick comparison: Baseline vs Alternative approach with 3 trains

```python run_mvp.py

dista-flow/# → Generates: outputs/time_distance_*.png

├── src/

│   ├── data/k2_fetcher.py           # K2 EHÜSZ data pipeline# Detailed analysis with performance distributions

│   ├── visualization/geojson_exporter.py  # Kepler.gl exportpython run_kpi.py

│   ├── controllers/ai_controllers.py      # AI controllers# → Generates: outputs/headway_*.png

│   ├── model.py                     # Railway line modeling# → Console: Performance metrics and statistics

│   ├── sim.py                       # Simulation engine

│   ├── train.py                     # Train physics# Parameter sweep across reaction times, margins, train counts

│   ├── controllers.py               # Control algorithmspython run_sweep.py

│   ├── metrics.py                   # Performance analysis# → Generates: outputs/sweep_summary.csv, outputs/sweep_analysis.png

│   └── plots.py                     # Plotting utilities```

├── data/                            # Railway datasets

├── outputs/                         # Generated results## 📊 Simulation Capabilities

├── tools/update_k2_data.py          # K2 data fetcher

├── app.py                          # Streamlit dashboardThe framework enables comparison of different control approaches:

├── run_simulation.py               # Unified runner

└── run_sweep.py                    # Parameter optimization| Aspect | Baseline Method | Alternative Method | Analysis |

```|--------|-----------------|-------------------|----------|

| Following Distance | Standard calculation | Modified approach | Comparative study |

## 📊 Available Datasets| System Response | Traditional timing | Adjusted parameters | Performance metrics |

| Safety Margins | Conservative | Research-based | Maintained standards |

- **ETCS Lines:** 11 segments, 818.3 km total

- **Coverage:** 61.1% of Hungarian main lines## 🗂 Project Structure

- **Lines:** 1 (Bp-Vienna), 30 (Bp-Debrecen), 40 (Bp-Dombóvár), 70 (Bp-Szeged), 80 (Bp-Miskolc)

```

## 🎮 Usage Examplesdista-flow/

├── data/

### Interactive Mode│   ├── segments.csv           # Demo short line

```bash│   ├── segments_long.csv      # Demo long line  

streamlit run app.py│   └── segments_mav1.csv      # Generated Hungarian Line 1 (184km)

# Select line → Configure parameters → Run simulation → Export GeoJSON├── src/

```│   ├── model.py              # Line topology & speed limits

│   ├── train.py              # Train physics & state

### Batch Processing│   ├── controllers.py        # Control algorithms (baseline & alternative)

```bash│   ├── sim.py                # Discrete-time simulation engine

# Complete analysis│   ├── metrics.py            # Performance calculations

python run_simulation.py --mode full --trains 5 --time 21600│   ├── plots.py              # Visualization tools

│   └── export_geo.py         # Geographic data export

# Parameter sweep├── tools/

python run_sweep.py│   └── convert_k2_to_segments.py  # VPE K2 → CSV converter

```├── outputs/                  # Generated plots & results

├── run_mvp.py               # Quick comparative demo

### Kepler.gl Workflow├── run_kpi.py               # Detailed performance analysis

```bash├── run_sweep.py             # Parameter space exploration

python run_simulation.py --mode geo└── test_basic.py            # Unit tests

# Upload outputs/*.geojson to kepler.gl```

# Configure animation layers

# Watch trains move!## 🔬 Data Sources

```

### Current: Demo Data

## 🔬 Research Applications- **Budapest-Sopron corridor** (184 km, 8 segments)

- Speeds: 100-140 km/h, mostly double-track

- **ETCS vs AI Controller** performance comparison- ETCS signalling throughout

- **Safety analysis** - minimum headway and collision avoidance

- **Capacity optimization** - throughput maximization### Target: Real VPE K2 EHÜSZ Data

- **Infrastructure planning** - ETCS deployment ROI- Hungarian railway network (Lines 1-140)

- Station positions, track speeds, signalling

## 📈 Generated Outputs- Grades, slow orders, track restrictions



- **GeoJSON Files** - Railway segments and train movements## 🤖 AI Evolution Roadmap

- **Performance Plots** - Time-distance diagrams, headway distributions  

- **KPI Analysis** - JSON format metrics and statistics### Phase 1: Mathematical Models (✅ Current)

- **Kepler.gl Config** - Pre-configured visualization settings```python

# Baseline approach: Standard calculations

## 🛠️ Technical Requirements# Alternative approach: Modified parameters and logic

# Both implemented for comparative analysis

- Python 3.11+```

- Core: pandas, numpy, simpy, matplotlib

- Web UI: streamlit, plotly### Phase 2: Advanced Methods (🔄 Research)

- Visualization: geojson, kepler.gl```python

- Optional AI: xgboost, stable-baselines3# Investigating different algorithmic approaches

# Data-driven optimization techniques

## 📚 Documentation# Performance enhancement strategies

```

- **[Run Guide](RUN_GUIDE.md)** - Complete execution instructions

- **[Kepler Guide](KEPLER_GUIDE.md)** - Visualization setup details### Phase 3: System Integration (🎯 Future)

- **[System Overview](SYSTEM_COMPLETE.md)** - Architecture documentation- Multi-agent coordination

- System-wide optimization

## 🏆 System Status- Advanced control strategies



- ✅ **K2 Data Pipeline** - Automated EHÜSZ integration## 📈 Key Performance Indicators

- ✅ **ETCS Filtering** - 61.1% coverage, production-ready

- ✅ **GeoJSON Export** - Full Kepler.gl compatibility  | KPI | Description | Research Value |

- ✅ **AI Controllers** - Level 2 & 3 implementations|-----|-------------|----------------|

- ✅ **Interactive UI** - Streamlit dashboard operational| **Headway Distribution** | Gap between consecutive trains | Shows safety margin optimization |

- ✅ **Documentation** - Complete user guides| **Throughput (TPH)** | Trains per hour through bottleneck | Direct capacity measurement |

| **Speed Variance** | Smoothness of train flow | Passenger comfort & efficiency |

**Ready for TDK research and railway industry analysis!** 🚂✨| **Delay Propagation** | How disturbances spread | System stability |
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
- **Student Research Projects**: Transportation systems analysis
- **Engineering Studies**: Railway operations research
- **System Analysis**: Multi-agent simulation studies

### Research Areas
- Railway operations optimization
- Transportation system modeling
- Control system comparative analysis

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

> **"Develop a comprehensive railway simulation framework for comparative analysis of train control methodologies using Hungarian railway network data."**

---

**Built with** 🐍 Python | 📊 Pandas/NumPy | 🎨 Matplotlib | 🚄 SimPy

**Research Focus**: Railway Operations Research • Transportation System Modeling • Control Algorithm Analysis
