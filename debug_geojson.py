#!/usr/bin/env python3
"""
Debug script for GeoJSON export error
"""
import sys
import os
import pandas as pd
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from visualization.geojson_exporter import GeoJSONExporter

def debug_geojson_error():
    """Debug the 'argument of type 'int' is not iterable' error"""
    print("🔍 Debugging GeoJSON export error...")
    
    # Create test segments from ETCS data
    etcs_file = Path("src/data/data/etcs_enabled.csv")
    if not etcs_file.exists():
        print(f"❌ ETCS file not found: {etcs_file}")
        return
    
    # Read ETCS data and select Line 1
    etcs_df = pd.read_csv(etcs_file)
    selected_segments = etcs_df[etcs_df['line_number'] == 1]
    
    print(f"📊 Selected segments for Line 1:")
    print(selected_segments[['from_station', 'to_station', 'length_km']])
    
    # Save to temporary file
    temp_csv = Path("debug_segments.csv")
    selected_segments.to_csv(temp_csv, index=False)
    
    # Create test simulation data
    test_simulation = pd.DataFrame({
        't': [0, 30, 60, 90, 120],
        'id': [0, 0, 0, 0, 0],  # Use integer IDs like the real simulation
        'pos_m': [0, 5000, 15000, 25000, 35000],
        'v': [25, 35, 40, 35, 30],  # m/s
        'finished': [False, False, False, False, True]
    })
    
    print(f"📊 Test simulation data:")
    print(test_simulation)
    
    # Try GeoJSON export
    try:
        exporter = GeoJSONExporter()
        
        # Test segments export
        print("\n🧪 Testing segments export...")
        segments_geojson = exporter.segments_to_geojson(temp_csv)
        print(f"✅ Segments exported to: {segments_geojson}")
        
        # Test movements export
        print("\n🧪 Testing movements export...")
        movements_geojson = exporter.simulation_to_geojson(test_simulation, temp_csv)
        print(f"✅ Movements exported to: {movements_geojson}")
        
    except Exception as e:
        print(f"❌ Error during export: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        temp_csv.unlink(missing_ok=True)

if __name__ == "__main__":
    debug_geojson_error()