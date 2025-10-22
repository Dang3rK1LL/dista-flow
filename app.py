"""
DISTA-Flow Interactive Dashboard
Streamlit web interface for railway simulation and Kepler.gl visualization
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from data.k2_fetcher import K2DataFetcher
from visualization.geojson_exporter import GeoJSONExporter
from model import Line
from sim import run_sim
from train import TrainState
from controllers import DistaAI_Simple

# Try to import AI controllers, fallback to simple if not available
try:
    from controllers.ai_controllers import create_controller
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    def create_controller(controller_type):
        return DistaAI_Simple()

# Page config
st.set_page_config(
    page_title="DISTA-Flow Railway Simulation",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="expanded"
)

def simulate_trains(line, num_trains, simulation_time_hours, controller):
    """Wrapper function for running train simulation"""
    # Create trains
    trains = []
    for i in range(num_trains):
        train = TrainState(i, pos_m=i * 1000.0)  # Start trains 1km apart
        trains.append(train)
    
    # Create controller map
    controller_map = {train.id: controller for train in trains}
    
    # Run simulation (convert hours to seconds)
    simulation_time_seconds = simulation_time_hours * 3600
    results_df = run_sim(line, trains, controller_map, dt=0.5, T=simulation_time_seconds)
    
    # Convert DataFrame to list of result objects for compatibility
    class SimResult:
        def __init__(self, row):
            self.train_id = row['id']
            self.time = row['t']
            self.position = row['pos_m']
            self.speed = row['v'] * 3.6  # Convert m/s to km/h
            self.timestamp = row['t']
    
    results = [SimResult(row) for _, row in results_df.iterrows()]
    return results

def load_etcs_lines():
    """Load available ETCS-enabled lines"""
    etcs_file = Path("data/etcs_enabled.csv")
    if etcs_file.exists():
        return pd.read_csv(etcs_file)
    else:
        st.warning("⚠️ ETCS data not found. Run K2 data fetching first.")
        return pd.DataFrame()

def main():
    st.title("🚂 DISTA-Flow Railway Simulation")
    st.markdown("*Advanced Railway Traffic Simulation with AI Controllers*")
    
    # Sidebar controls
    st.sidebar.header("📊 Simulation Controls")
    
    # Load available lines
    etcs_df = load_etcs_lines()
    
    if not etcs_df.empty:
        # Line selection - group by line number and create display names
        line_groups = etcs_df.groupby('line_number').agg({
            'from_station': 'first',
            'to_station': 'last',
            'length_km': 'sum',
            'max_speed_kmh': 'max'
        }).reset_index()
        
        # Create display names
        line_groups['display_name'] = (
            "Line " + line_groups['line_number'].astype(str) + 
            ": " + line_groups['from_station'] + 
            " → " + line_groups['to_station'] +
            " (" + line_groups['length_km'].round(1).astype(str) + " km)"
        )
        
        st.sidebar.subheader("🛤️ Railway Line Selection")
        line_options = line_groups['display_name'].tolist()
        selected_line_display = st.sidebar.selectbox("Choose line:", line_options)
        
        # Get selected line number
        selected_idx = line_groups[line_groups['display_name'] == selected_line_display].index[0]
        selected_line_number = line_groups.loc[selected_idx, 'line_number']
        line_info = line_groups.loc[selected_idx]
        
        st.sidebar.info(f"**Length:** {line_info['length_km']:.1f} km\n\n**Max Speed:** {line_info['max_speed_kmh']} km/h")
        
        # Controller selection
        st.sidebar.subheader("🤖 AI Controller")
        if AI_AVAILABLE:
            controller_options = ["Simple", "DistaAI_Predictive", "DistaAI_RL"]
        else:
            controller_options = ["Simple"]
            st.sidebar.info("💡 Install XGBoost/RL libraries for AI controllers")
        
        controller_type = st.sidebar.selectbox("Controller:", controller_options)
        
        # Simulation parameters
        st.sidebar.subheader("⚙️ Parameters")
        num_trains = st.sidebar.slider("Number of trains:", 1, 20, 5)
        simulation_time = st.sidebar.slider("Simulation time (hours):", 1, 24, 8)
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("🎯 Simulation Results")
            
            # Run simulation button
            if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
                with st.spinner("Running simulation..."):
                    # Load line data - use the line number to find the right CSV file
                    line_file = f"data/segments_{selected_line_number}.csv"
                    
                    # Check if file exists, fallback to segments.csv if not
                    if not Path(line_file).exists():
                        line_file = "data/segments.csv"
                        st.warning(f"Using fallback segments.csv file")
                    
                    # Load the DataFrame and create Line object
                    segments_df = pd.read_csv(line_file)
                    line = Line(segments_df)
                    
                    # Create controller
                    if controller_type == "Simple" or not AI_AVAILABLE:
                        controller = DistaAI_Simple()
                    else:
                        controller = create_controller(controller_type)
                    
                    # Run simulation
                    results = simulate_trains(line, num_trains, simulation_time, controller)
                    
                    # Display results
                    st.success(f"✅ Simulation completed! Generated {len(results)} train positions")
                    
                    # Export GeoJSON
                    exporter = GeoJSONExporter(line)
                    
                    # Export segments
                    segments_geojson = exporter.segments_to_geojson()
                    with open("railway_segments.geojson", "w") as f:
                        json.dump(segments_geojson, f)
                    
                    # Export train movements
                    movements_geojson = exporter.simulation_to_geojson(results)
                    with open("train_movements.geojson", "w") as f:
                        json.dump(movements_geojson, f)
                    
                    st.success("📊 GeoJSON files exported for Kepler.gl!")
                    
                    # Show basic stats
                    st.subheader("📈 Statistics")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Total Distance", f"{line.total_length:.1f} km")
                    with col_b:
                        st.metric("Train Positions", len(results))
                    with col_c:
                        avg_speed = sum(r.speed for r in results) / len(results)
                        st.metric("Avg Speed", f"{avg_speed:.1f} km/h")
        
        with col2:
            st.header("🗺️ Kepler.gl Integration")
            
            # Kepler.gl instructions
            st.markdown("""
            ### How to use with Kepler.gl:
            
            1. **Open** [kepler.gl](https://kepler.gl/)
            2. **Upload** generated GeoJSON files:
               - `railway_segments.geojson`
               - `train_movements.geojson`
            3. **Configure** visualization layers
            4. **Animate** train movements
            
            ### Generated Files:
            """)
            
            # List generated files
            geojson_files = [f for f in os.listdir(".") if f.endswith(".geojson")]
            for file in geojson_files:
                file_size = os.path.getsize(file) / 1024  # KB
                st.code(f"📁 {file} ({file_size:.1f} KB)")
            
            # K2 data management
            st.header("📡 K2 Data Management")
            
            if st.button("🔄 Update K2 Data", use_container_width=True):
                with st.spinner("Fetching K2 data..."):
                    fetcher = K2DataFetcher()
                    fetcher.update_data()
                    st.success("✅ K2 data updated!")
                    st.rerun()
            
            # Show K2 metadata
            meta_file = Path("data/k2_meta.json")
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                
                st.subheader("📊 K2 Status")
                st.json({
                    "Last Update": meta.get("last_update", "Unknown"),
                    "ETCS Coverage": f"{meta.get('etcs_coverage_ratio', 0):.1%}",
                    "Total Lines": meta.get("total_lines", 0)
                })
    
    else:
        # No data available
        st.warning("⚠️ No railway data found!")
        st.markdown("""
        ### 🚀 Getting Started:
        
        1. **Fetch K2 data** first
        2. **Select a railway line**
        3. **Run simulation**
        4. **Visualize in Kepler.gl**
        """)
        
        if st.button("🔄 Fetch K2 Data Now", type="primary"):
            with st.spinner("Fetching K2 data..."):
                fetcher = K2DataFetcher()
                fetcher.update_data()
                st.success("✅ K2 data fetched!")
                st.rerun()

if __name__ == "__main__":
    main()