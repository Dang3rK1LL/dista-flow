#!/usr/bin/env python3
"""
Analyze K2 data for Line 1 ETCS coverage
"""
import pandas as pd
from pathlib import Path

def analyze_line_etcs():
    """Analyze ETCS coverage on railway lines"""
    k2_file = Path("src/data/data/k2_all_lines.csv")
    df = pd.read_csv(k2_file)
    
    # Check Line 1 specifically
    line1 = df[df['line_number'] == 1]
    print("=== LINE 1 ANALYSIS ===")
    print(f"Total segments: {len(line1)}")
    print("\nAll Line 1 segments:")
    for _, row in line1.iterrows():
        print(f"{row['from_station']} → {row['to_station']} | {row['signalling']} | {row['length_km']}km")
    
    # Count ETCS vs Conventional
    etcs_segments = line1[line1['signalling'].str.contains('ETCS', na=False)]
    conv_segments = line1[line1['signalling'].str.contains('Conventional', na=False)]
    
    print(f"\nETCS segments: {len(etcs_segments)}")
    print(f"Conventional segments: {len(conv_segments)}")
    
    # Check if we have detailed station-by-station data
    print("\n=== ETCS SEGMENTS ONLY ===")
    for _, row in etcs_segments.iterrows():
        print(f"{row['from_station']} → {row['to_station']} | {row['signalling']}")
    
    # Look for more detailed segments in the data
    print("\n=== SEARCHING FOR MORE DETAILED DATA ===")
    budapest_segments = df[df['from_station'].str.contains('Budapest', na=False) | 
                          df['to_station'].str.contains('Budapest', na=False)]
    print(f"Budapest-related segments: {len(budapest_segments)}")
    
    # Check if there are intermediate stations
    stations_on_line1 = set()
    for _, row in line1.iterrows():
        stations_on_line1.add(row['from_station'])
        stations_on_line1.add(row['to_station'])
    
    print(f"\nUnique stations on Line 1: {len(stations_on_line1)}")
    for station in sorted(stations_on_line1):
        print(f"  - {station}")

if __name__ == "__main__":
    analyze_line_etcs()