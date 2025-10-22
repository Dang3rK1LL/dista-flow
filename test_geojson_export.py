#!/usr/bin/env python3
"""
Test script for GeoJSON export functionality
"""
import sys
import os
import pandas as pd
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from visualization.geojson_exporter import GeoJSONExporter

def test_geojson_export():
    """Test the GeoJSON export functionality"""
    print("🧪 Testing GeoJSON Export...")
    
    # Create test data
    test_segments = pd.DataFrame({
        'line_number': [1, 1, 30, 30],
        'from_station': ['Budapest-Kelenföld', 'Érd', 'Budapest-Nyugati', 'Szolnok'],
        'to_station': ['Érd', 'Bicske', 'Szolnok', 'Debrecen'],
        'length_km': [15.2, 21.1, 92.3, 95.7],
        'max_speed_kmh': [120, 120, 140, 120],
        'tracks': [2, 2, 2, 2],
        'signalling': ['ETCS L1', 'ETCS L1', 'ETCS L1', 'ETCS L1'],
        'electrification': ['25kV AC', '25kV AC', '25kV AC', '25kV AC']
    })
    
    # Save test segments to CSV
    test_csv = Path("test_segments.csv")
    test_segments.to_csv(test_csv, index=False)
    print(f"✅ Created test segments CSV: {test_csv}")
    
    # Create exporter
    exporter = GeoJSONExporter()
    
    # Test segments export
    try:
        segments_geojson = exporter.segments_to_geojson(test_csv)
        print(f"✅ Segments exported to: {segments_geojson}")
        
        # Check file size
        geojson_path = Path(segments_geojson)
        file_size = geojson_path.stat().st_size
        print(f"📊 GeoJSON file size: {file_size} bytes")
        
        if file_size > 0:
            # Read and display first few characters
            with open(geojson_path, 'r', encoding='utf-8') as f:
                content = f.read()[:200]
                print(f"📄 GeoJSON content preview:\n{content}...")
        else:
            print("❌ GeoJSON file is empty!")
            
    except Exception as e:
        print(f"❌ Error exporting segments: {e}")
        import traceback
        traceback.print_exc()
    
    # Test simulation export
    try:
        test_simulation = pd.DataFrame({
            't': [0, 30, 60, 90, 120],
            'id': ['Train_1', 'Train_1', 'Train_1', 'Train_1', 'Train_1'],
            'pos_m': [0, 5000, 15000, 25000, 35000],
            'v': [25, 35, 40, 35, 30],  # m/s
            'finished': [False, False, False, False, True]
        })
        
        movements_geojson = exporter.simulation_to_geojson(test_simulation, test_csv)
        print(f"✅ Train movements exported to: {movements_geojson}")
        
        # Check file size
        movements_path = Path(movements_geojson)
        file_size = movements_path.stat().st_size
        print(f"📊 Movements GeoJSON file size: {file_size} bytes")
        
        if file_size > 0:
            # Read and display first few characters
            with open(movements_path, 'r', encoding='utf-8') as f:
                content = f.read()[:200]
                print(f"📄 Movements GeoJSON content preview:\n{content}...")
        else:
            print("❌ Movements GeoJSON file is empty!")
            
    except Exception as e:
        print(f"❌ Error exporting movements: {e}")
        import traceback
        traceback.print_exc()
    
    # Clean up
    test_csv.unlink(missing_ok=True)
    print("🧹 Cleaned up test files")

if __name__ == "__main__":
    test_geojson_export()