"""
DISTA-Flow Interactive Dashboard
Modern railway simulation interface with dark theme
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.data.k2_fetcher import K2DataFetcher
from src.visualization.geojson_exporter import GeoJSONExporter
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

# Modern dark theme configuration
st.set_page_config(
    page_title="DISTA-Flow Railway Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark theme
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global theme - Unified color palette */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        font-family: 'Inter', sans-serif;
        color: #f1f5f9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
        border-right: 1px solid #475569;
    }
    
    /* Main content area */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: transparent;
    }
    
    /* Headers - Consistent typography */
    h1 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    h2 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 1.8rem !important;
        margin-top: 2rem !important;
        border-bottom: 2px solid #334155;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        font-size: 1.3rem !important;
    }
    
    /* Metric cards - Unified styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
        border: 1px solid #64748b;
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.4);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.6);
        border-color: #94a3b8;
    }
    
    [data-testid="metric-container"] > div {
        color: #f8fafc !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #fbbf24 !important;
        font-weight: 700 !important;
    }
    
    /* Buttons - Unified color scheme */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
        text-transform: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }
    
    /* Secondary button */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        box-shadow: 0 4px 14px rgba(100, 116, 139, 0.3);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #475569 0%, #334155 100%);
        box-shadow: 0 6px 20px rgba(100, 116, 139, 0.4);
    }
    
    /* Form inputs - Consistent styling */
    .stSelectbox > div > div {
        background: #334155;
        border: 1px solid #64748b;
        border-radius: 8px;
        color: #f8fafc;
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .stSlider > div > div {
        background: #334155;
    }
    
    .stSlider [data-testid="stSlider"] {
        color: #3b82f6;
    }
    
    /* Alert boxes - Consistent colors */
    .stAlert {
        background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        color: #f8fafc;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
    }
    
    /* Success messages */
    .stSuccess {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        color: #f8fafc;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
    }
    
    /* Warning messages */
    .stWarning {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        border: 1px solid #fbbf24;
        border-radius: 12px;
        color: #f8fafc;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.2);
    }
    
    /* Error messages */
    .stError {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        border: 1px solid #f87171;
        border-radius: 12px;
        color: #f8fafc;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
    }
    
    /* Info messages */
    .stInfo {
        background: linear-gradient(135deg, #0891b2 0%, #0ea5e9 100%);
        border: 1px solid #38bdf8;
        border-radius: 12px;
        color: #f8fafc;
        box-shadow: 0 4px 12px rgba(8, 145, 178, 0.2);
    }
    
    /* Warning messages */
    .stWarning {
        background: linear-gradient(135deg, #d69e2e 0%, #ed8936 100%);
        border: 1px solid #f6ad55;
        border-radius: 12px;
        color: #f7fafc;
    }
    
    /* Code blocks */
    .stCode {
        background: #1a202c;
        border: 1px solid #4a5568;
        border-radius: 8px;
        color: #a0aec0;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: #2d3748;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Sidebar elements */
    .css-1d391kg .stSelectbox > div > div {
        background: #1a202c;
        border: 1px solid #4a5568;
    }
    
    .css-1d391kg .stSlider > div > div {
        background: #1a202c;
    }
    
    /* Progress bars - Enhanced styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);
        border-radius: 8px;
    }
    
    .stProgress > div {
        background: #334155;
        border-radius: 8px;
    }
    
    /* Spinner */
    .stSpinner > div {
        color: #3b82f6 !important;
    }
    
    /* Sidebar elements */
    .css-1d391kg .stSelectbox > div > div {
        background: #475569;
        border-color: #64748b;
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: #f8fafc !important;
    }
    
    /* Tables */
    .stDataFrame {
        background: #334155;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.3);
    }
    
    /* Caption text */
    .caption {
        color: #94a3b8 !important;
        font-size: 0.875rem;
        font-style: italic;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #64748b;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

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
    
    # Return DataFrame directly for GeoJSON export
    return results_df

def load_etcs_lines():
    """Load available railway lines (K2 data)"""
    # Load the complete K2 dataset for more detailed segments
    k2_file = Path("src/data/data/k2_all_lines.csv")
    if k2_file.exists():
        return pd.read_csv(k2_file)
    
    # Fallback to ETCS-only data
    etcs_file = Path("src/data/data/etcs_enabled.csv")
    if etcs_file.exists():
        return pd.read_csv(etcs_file)
    
    # Last fallback to old location
    etcs_file = Path("data/etcs_enabled.csv")
    if etcs_file.exists():
        return pd.read_csv(etcs_file)
    else:
        st.warning("Railway data not found. Run K2 data fetching first.")
        return pd.DataFrame()

def main():
    # Header with modern typography
    st.markdown("""
    <div style="
        text-align: center; 
        padding: 2rem 0; 
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(15, 23, 42, 0.4);
        border: 1px solid #334155;
    ">
        <h1 style="
            margin-bottom: 0.5rem;
            color: #f8fafc;
            text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        ">DISTA-Flow Railway Simulation</h1>
        <p style="
            font-size: 1.2rem; 
            color: #cbd5e1; 
            font-weight: 300;
            margin: 0;
        ">
            Advanced Railway Traffic Simulation Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("Simulation Controls")
    
    # Load available lines
    etcs_df = load_etcs_lines()
    
    if not etcs_df.empty:
        # Filter to ETCS lines only for display
        etcs_lines = etcs_df[etcs_df['signalling'].str.contains('ETCS', na=False)]
        
        if etcs_lines.empty:
            st.sidebar.warning("No ETCS-enabled lines available")
            st.sidebar.info("DISTA simulation requires ETCS infrastructure")
            return
        
        # Line selection - group by line number and create display names (ETCS only)
        line_groups = etcs_lines.groupby('line_number').agg({
            'from_station': 'first',
            'to_station': 'last',
            'length_km': 'sum',
            'max_speed_kmh': 'max',
            'signalling': lambda x: "ETCS L" + x.str.extract(r'ETCS L(\d+)')[0].mode()[0] if not x.empty else "ETCS"
        }).reset_index()
        
        # Create display names with ETCS level indication
        line_groups['display_name'] = (
            "Line " + line_groups['line_number'].astype(str) + 
            " (" + line_groups['signalling'] + "): " +
            line_groups['from_station'] + 
            " → " + line_groups['to_station'] +
            " (" + line_groups['length_km'].round(1).astype(str) + " km)"
        )
        
        st.sidebar.subheader("Railway Line Selection")
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
            st.sidebar.info("Install XGBoost/RL libraries for AI controllers")
        
        controller_type = st.sidebar.selectbox("Controller:", controller_options)
        
        # Simulation parameters
        st.sidebar.subheader("Parameters")
        num_trains = st.sidebar.slider("Number of trains:", 1, 20, 5)
        simulation_time = st.sidebar.slider("Simulation time (hours):", 1, 24, 8)
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("Simulation Results")
            
            # Run simulation button
            if st.button("Run Simulation", type="primary", use_container_width=True):
                with st.spinner("Running simulation..."):
                    # Get the selected line data from K2 DataFrame - ETCS ONLY
                    selected_segments = etcs_df[etcs_df['line_number'] == selected_line_number]
                    
                    # Filter to ETCS segments only - no DISTA where no ETCS
                    etcs_only_segments = selected_segments[
                        selected_segments['signalling'].str.contains('ETCS', na=False)
                    ]
                    
                    if etcs_only_segments.empty:
                        st.error(f"No ETCS segments found for line {selected_line_number}")
                        st.info("DISTA simulation not available on non-ETCS segments")
                        return
                    
                    st.info(f"Using {len(etcs_only_segments)} ETCS segments for simulation")
                    
                    # Create Line object from ETCS segments only
                    line = Line(etcs_only_segments)
                    
                    # Create controller
                    if controller_type == "Simple" or not AI_AVAILABLE:
                        controller = DistaAI_Simple()
                    else:
                        controller = create_controller(controller_type)
                    
                    # Run simulation
                    results = simulate_trains(line, num_trains, simulation_time, controller)
                    
                    # Display results
                    st.success(f"Simulation completed! Generated {len(results)} train positions")
                    
                    # Export GeoJSON using ETCS data
                    exporter = GeoJSONExporter()
                    
                    # Save selected segments to temporary file for export
                    temp_segments_file = Path("temp_selected_segments.csv")
                    selected_segments.to_csv(temp_segments_file, index=False)
                    
                    # Export segments using the temporary file
                    try:
                        segments_geojson_file = exporter.segments_to_geojson(temp_segments_file)
                        
                        # Copy to root directory for easy access
                        import shutil
                        shutil.copy(segments_geojson_file, "railway_segments.geojson")
                        
                        # Export train movements - results is already a DataFrame
                        if not results.empty:
                            movements_geojson_file = exporter.simulation_to_geojson(results, temp_segments_file)
                            
                            # Copy to root directory
                            shutil.copy(movements_geojson_file, "train_movements.geojson")
                            
                            st.success("GeoJSON files exported for Kepler.gl!")
                            st.info(f"Exported {len(results)} train position records")
                        else:
                            st.warning("No simulation data to export")
                        
                        # Clean up temporary file
                        temp_segments_file.unlink(missing_ok=True)
                        
                    except Exception as e:
                        st.error(f"GeoJSON export failed: {e}")
                        # Clean up temporary file on error
                        temp_segments_file.unlink(missing_ok=True)
                    
                    # Show basic stats
                    st.subheader("Statistics")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Total Distance", f"{line.total_m/1000:.1f} km")
                    with col_b:
                        st.metric("Train Positions", len(results))
                    with col_c:
                        # Calculate average speed from DataFrame
                        avg_speed = results['v'].mean() * 3.6  # Convert m/s to km/h
                        st.metric("Avg Speed", f"{avg_speed:.1f} km/h")
        
        with col2:
            st.header("Kepler.gl Map Integration")
            
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
                st.code(f"{file} ({file_size:.1f} KB)")
            
            # K2 data management - Enhanced 227-line coverage
            st.header("K2 Railway Infrastructure")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Update K2 Data", use_container_width=True):
                    with st.spinner("Fetching K2 EHÜSZ data (227 lines)..."):
                        fetcher = K2DataFetcher()
                        metadata = fetcher.update_data()
                        st.success(f"{metadata['total_lines']} lines updated!")
                        st.rerun()
            
            with col2:
                # Show current status
                try:
                    fetcher = K2DataFetcher()
                    status = fetcher.get_status()
                    
                    if status.get("files_exist", {}).get("metadata", False):
                        # Load metadata from new location
                        meta_file = Path("src/data/data/k2_meta.json")
                        if meta_file.exists():
                            with open(meta_file) as f:
                                meta = json.load(f)
                            
                            st.metric("Total Lines", meta.get("total_lines", "N/A"))
                            st.metric("ETCS Lines", meta.get("etcs_lines", "N/A"))
                        else:
                            st.warning("Metadata not found")
                    else:
                        st.warning("Data not available")
                except Exception as e:
                    st.error(f"Status error: {e}")
            
            with col3:
                try:
                    meta_file = Path("src/data/data/k2_meta.json")
                    if meta_file.exists():
                        with open(meta_file) as f:
                            meta = json.load(f)
                        
                        etcs_coverage = meta.get("etcs_coverage_ratio", 0) * 100
                        total_km = meta.get("total_km", 0)
                        
                        st.metric("ETCS Coverage", f"{etcs_coverage:.1f}%")
                        st.metric("Total Network", f"{total_km:.0f} km")
                    else:
                        st.info("Update required")
                except Exception as e:
                    st.info("Loading data...")
            
            # Enhanced K2 status display
            meta_file = Path("src/data/data/k2_meta.json")
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                
                st.subheader("K2 EHÜSZ Details")
                
                # Create enhanced metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Infrastructure Version", meta.get("infrastructure_version", "N/A"))
                
                with col2:
                    st.metric("Station Coordinates", meta.get("station_coordinates", "N/A"))
                
                with col3:
                    etcs_km = meta.get("etcs_km", 0)
                    st.metric("ETCS Network", f"{etcs_km:.0f} km")
                
                with col4:
                    fetch_time = meta.get("fetch_duration_seconds", 0)
                    st.metric("Fetch Duration", f"{fetch_time:.1f}s")
                
                # Show data source and last update
                st.caption(f"Last update: {meta.get('last_update', 'Unknown')}")
                st.caption(f"Data source: {meta.get('data_source', 'N/A')}")
                
                # ETCS coverage visualization
                if meta.get("total_lines", 0) > 0:
                    etcs_ratio = meta.get("etcs_coverage_ratio", 0)
                    st.progress(etcs_ratio, text=f"ETCS coverage: {etcs_ratio:.1%}")
            else:
                st.info("Click 'Update K2 Data' to download all 227 lines")
    
    else:
        # No data available
        st.warning("No railway data found!")
        st.markdown("""
        ### Getting Started:
        
        1. **Fetch K2 data** first
        2. **Select a railway line**
        3. **Run simulation**
        4. **Visualize in Kepler.gl**
        """)
        
        if st.button("Fetch K2 Data Now", type="primary"):
            with st.spinner("Fetching K2 data..."):
                fetcher = K2DataFetcher()
                fetcher.update_data()
                st.success("K2 data fetched!")
                st.rerun()

if __name__ == "__main__":
    main()