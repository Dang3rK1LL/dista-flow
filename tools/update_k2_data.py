#!/usr/bin/env python3
"""
K2 Data Update Tool
Standalone script to check and update K2 EHÜSZ data
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.data.k2_fetcher import K2DataFetcher

def main():
    """Main update script"""
    print("🚂 K2 EHÜSZ Data Update Tool")
    print("=" * 40)
    
    fetcher = K2DataFetcher()
    
    # Show current status
    print("\n📊 Current Status:")
    status = fetcher.get_status()
    
    print(f"   Last checked: {status.get('last_checked', 'Never')}")
    print(f"   Current version: {status.get('current_version', 'Unknown')}")
    print(f"   Total lines: {status.get('total_lines', 0)}")
    print(f"   ETCS coverage: {status.get('etcs_coverage_ratio', 0):.1%}")
    print(f"   Status: {status.get('fetch_status', 'Unknown')}")
    
    # Check for updates
    print("\n🔍 Checking for updates...")
    current_version, is_newer = fetcher.check_version()
    
    if is_newer or not status.get('files_exist', {}).get('all_lines', False):
        print("📥 Update needed. Starting data fetch...")
        success = fetcher.update_all(force=False)
        
        if success:
            print("✅ Update completed successfully!")
            
            # Show updated status
            new_status = fetcher.get_status()
            print(f"\n📈 Updated Status:")
            print(f"   Version: {new_status.get('current_version')}")
            print(f"   Total lines: {new_status.get('total_lines')}")
            print(f"   ETCS segments: {new_status.get('etcs_segments', 0)}")
            print(f"   Coverage: {new_status.get('etcs_coverage_ratio', 0):.1%}")
        else:
            print("❌ Update failed!")
            sys.exit(1)
    else:
        print("✅ Data is up to date!")
    
    print("\n🎯 Available ETCS lines for simulation:")
    
    # List available ETCS lines
    etcs_file = Path("data/etcs_enabled.csv")
    if etcs_file.exists():
        import pandas as pd
        etcs_df = pd.read_csv(etcs_file)
        
        # Group by line number
        for line_num, group in etcs_df.groupby('line_number'):
            total_length = group['length_km'].sum()
            max_speed = group['max_speed_kmh'].max()
            segments = len(group)
            
            print(f"   Line {line_num}: {total_length:.1f}km, {segments} segments, max {max_speed}km/h")
            
        print(f"\n💡 Use these line numbers in simulation configs!")
    else:
        print("   No ETCS data available. Run update first.")

if __name__ == "__main__":
    main()