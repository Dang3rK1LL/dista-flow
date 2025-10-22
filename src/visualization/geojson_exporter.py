#!/usr/bin/env python3
"""
GeoJSON Export Module for Kepler.gl Integration
Converts railway segments and simulation results to geographic format
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from geojson import Feature, FeatureCollection, LineString, Point

class GeoJSONExporter:
    """
    Handles conversion of railway data and simulation results to GeoJSON format
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Comprehensive coordinates for Hungarian railway stations from ETCS data
        self.station_coords = {
            # Main Budapest terminals
            "Budapest-Kelenföld": [19.0406, 47.4642],
            "Budapest-Nyugati": [19.0566, 47.5103],
            "Budapest-Déli": [19.0236, 47.4756],
            "Budapest-Keleti": [19.0844, 47.5000],
            
            # Line 1 - Budapest to Vienna border
            "Érd": [18.9135, 47.3622],
            "Martonvásár": [18.7822, 47.3142],
            "Bicske": [18.6364, 47.4886],
            "Tata": [18.3167, 47.6500],
            "Komárom": [18.1265, 47.7423],
            "Győr": [17.6352, 47.6875],
            "Csorna": [17.2592, 47.6103],
            "Sopron": [16.5986, 47.6858],
            "Hegyeshalom": [17.1189, 47.8875],
            
            # Line 30 - Budapest to Debrecen  
            "Szolnok": [20.1996, 47.1735],
            "Debrecen": [21.6280, 47.5329],
            "Püspökladány": [21.1167, 47.3167],
            
            # Line 40 - Budapest to Pécs
            "Dombóvár": [18.1380, 46.3754],
            "Pécs": [18.2323, 46.0727],
            "Mohács": [18.6833, 45.9833],
            
            # Line 70 - Budapest to Szeged
            "Kecskemét": [19.6914, 46.9067],
            "Szeged": [20.1472, 46.2530],
            "Kiskunfélegyháza": [19.8500, 46.7167],
            
            # Line 80 - Budapest to Miskolc
            "Hatvan": [19.6833, 47.6667],
            "Miskolc": [20.7784, 48.1034],
            "Szerencs": [21.2167, 48.1500],
            
            # Line 6 stations
            "Székesfehérvár": [18.4108, 47.1926],
            "Pusztaszabolcs": [18.7500, 47.1500],
            
            # Line 8 stations
            "Békéscsaba": [21.0964, 46.6783],
            "Gyula": [21.2833, 46.6500],
            
            # Line 24 stations
            "Szombathely": [16.6231, 47.2309],
            "Körmend": [16.6167, 47.0167],
            
            # Secondary stations
            "Veszprém": [17.9104, 47.0929],
            "Celldömölk": [17.1667, 47.2500],
        }
    
    def interpolate_coordinates(self, start_coord: List[float], end_coord: List[float], 
                              segments: int = 10) -> List[List[float]]:
        """
        Interpolate coordinates between two points for smoother lines
        """
        coords = []
        for i in range(segments + 1):
            ratio = i / segments
            lon = start_coord[0] + (end_coord[0] - start_coord[0]) * ratio
            lat = start_coord[1] + (end_coord[1] - start_coord[1]) * ratio
            coords.append([lon, lat])
        return coords
    
    def segments_to_geojson(self, segments_file: Path, output_file: Path = None) -> str:
        """
        Convert railway segments CSV to GeoJSON for Kepler.gl visualization
        """
        if output_file is None:
            output_file = self.output_dir / "railway_segments.geojson"
        
        # Load segments data
        df = pd.read_csv(segments_file)
        
        features = []
        
        for _, row in df.iterrows():
            from_station = row.get('from_name', row.get('from_station', ''))
            to_station = row.get('to_name', row.get('to_station', ''))
            
            # Get coordinates
            start_coord = self.station_coords.get(from_station)
            end_coord = self.station_coords.get(to_station)
            
            if start_coord and end_coord:
                # Create smooth line with interpolated points
                line_coords = self.interpolate_coordinates(start_coord, end_coord, 5)
                
                # Create feature properties
                properties = {
                    "line_number": str(row.get('line_number', '')),
                    "from_station": from_station,
                    "to_station": to_station,
                    "length_km": float(row.get('length_km', 0)),
                    "max_speed_kmh": int(row.get('max_speed_kmh', row.get('speed_kmh', 0))),
                    "tracks": int(row.get('tracks', 1)),
                    "signalling": str(row.get('signalling', 'Unknown')),
                    "electrification": str(row.get('electrification', 'Unknown')),
                    "is_etcs": "ETCS" in str(row.get('signalling', '')).upper(),
                    "segment_id": f"{from_station}_{to_station}".replace(' ', '_')
                }
                
                # Create LineString feature
                feature = Feature(
                    geometry=LineString(line_coords),
                    properties=properties
                )
                features.append(feature)
        
        # Create FeatureCollection
        feature_collection = FeatureCollection(features)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(feature_collection, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(features)} railway segments to {output_file}")
        return str(output_file)
    
    def simulation_to_geojson(self, simulation_df: pd.DataFrame, 
                            segments_file: Path,
                            output_file: Path = None) -> str:
        """
        Convert simulation results to animated GeoJSON for train movement visualization
        """
        if output_file is None:
            output_file = self.output_dir / "train_movements.geojson"
        
        # Load segments for position-to-coordinate mapping
        segments_df = pd.read_csv(segments_file)
        
        # Create position-to-coordinate mapping
        position_map = self._create_position_mapping(segments_df)
        
        features = []
        
        # Group by train and time to create movement points
        for train_id, train_data in simulation_df.groupby('id'):
            train_data = train_data.sort_values('t')
            
            for _, row in train_data.iterrows():
                position_m = row['pos_m']
                coords = self._position_to_coordinates(position_m, position_map)
                
                if coords:
                    properties = {
                        "train_id": str(train_id),  # Convert to string for consistency
                        "time": float(row['t']),
                        "position_m": float(position_m),
                        "speed_mps": float(row['v']),
                        "speed_kmh": float(row['v'] * 3.6),
                        "timestamp": f"{int(row['t']//60):02d}:{int(row['t']%60):02d}",
                        "controller_type": "ETCS" if "ETCS" in str(train_id) else "DISTA",
                        "finished": row.get('finished', False)
                    }
                    
                    feature = Feature(
                        geometry=Point(coords),
                        properties=properties
                    )
                    features.append(feature)
        
        # Create FeatureCollection
        feature_collection = FeatureCollection(features)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(feature_collection, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(features)} train positions to {output_file}")
        return str(output_file)
    
    def _create_position_mapping(self, segments_df: pd.DataFrame) -> List[Tuple[float, List[float]]]:
        """
        Create mapping from distance along line to geographic coordinates
        """
        position_map = []
        cumulative_distance = 0.0
        
        for _, row in segments_df.iterrows():
            from_station = row.get('from_name', row.get('from_station', ''))
            to_station = row.get('to_name', row.get('to_station', ''))
            segment_length = row.get('length_km', 0) * 1000  # Convert to meters
            
            start_coord = self.station_coords.get(from_station)
            end_coord = self.station_coords.get(to_station)
            
            if start_coord and end_coord:
                # Add interpolated points along segment
                for i in range(11):  # 10 segments + start point
                    ratio = i / 10
                    distance = cumulative_distance + segment_length * ratio
                    
                    lon = start_coord[0] + (end_coord[0] - start_coord[0]) * ratio
                    lat = start_coord[1] + (end_coord[1] - start_coord[1]) * ratio
                    
                    position_map.append((distance, [lon, lat]))
                
                cumulative_distance += segment_length
        
        return position_map
    
    def _position_to_coordinates(self, position_m: float, 
                               position_map: List[Tuple[float, List[float]]]) -> Optional[List[float]]:
        """
        Convert distance along line to geographic coordinates using interpolation
        """
        if not position_map:
            return None
        
        # Find surrounding points in position map
        for i in range(len(position_map) - 1):
            pos1, coord1 = position_map[i]
            pos2, coord2 = position_map[i + 1]
            
            if pos1 <= position_m <= pos2:
                # Interpolate between the two points
                if pos2 == pos1:
                    return coord1
                
                ratio = (position_m - pos1) / (pos2 - pos1)
                lon = coord1[0] + (coord2[0] - coord1[0]) * ratio
                lat = coord1[1] + (coord2[1] - coord1[1]) * ratio
                return [lon, lat]
        
        # If position is beyond the line, return last coordinate
        if position_m >= position_map[-1][0]:
            return position_map[-1][1]
        
        # If position is before the line, return first coordinate
        return position_map[0][1]
    
    def create_kepler_config(self, segments_file: str, movements_file: str, 
                           output_file: Path = None) -> str:
        """
        Create Kepler.gl configuration JSON for railway visualization
        """
        if output_file is None:
            output_file = self.output_dir / "kepler_config.json"
        
        config = {
            "version": "v1",
            "config": {
                "visState": {
                    "filters": [],
                    "layers": [
                        {
                            "id": "railway_segments",
                            "type": "line",
                            "config": {
                                "dataId": "segments",
                                "label": "Railway Segments",
                                "color": [23, 184, 190],
                                "columns": {"geojson": "_geojson"},
                                "isVisible": True,
                                "visConfig": {
                                    "opacity": 0.8,
                                    "thickness": 3,
                                    "colorRange": {
                                        "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
                                    }
                                }
                            }
                        },
                        {
                            "id": "train_movements",
                            "type": "point",
                            "config": {
                                "dataId": "movements",
                                "label": "Train Positions",
                                "color": [255, 178, 102],
                                "columns": {"geojson": "_geojson"},
                                "isVisible": True,
                                "visConfig": {
                                    "radius": 8,
                                    "opacity": 0.9,
                                    "radiusRange": [4, 20]
                                }
                            }
                        }
                    ],
                    "interactionConfig": {
                        "tooltip": {
                            "fieldsToShow": {
                                "segments": ["line_number", "from_station", "to_station", "max_speed_kmh", "signalling"],
                                "movements": ["train_id", "timestamp", "speed_kmh", "controller_type"]
                            }
                        }
                    }
                },
                "mapState": {
                    "bearing": 0,
                    "dragRotate": False,
                    "latitude": 47.4979,
                    "longitude": 19.0402,
                    "pitch": 0,
                    "zoom": 7,
                    "isSplit": False
                }
            }
        }
        
        # Save configuration
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created Kepler.gl config: {output_file}")
        return str(output_file)

def main():
    """Demo usage of GeoJSON exporter"""
    exporter = GeoJSONExporter()
    
    # Export railway segments
    segments_file = Path("data/k2_all_lines.csv")
    if segments_file.exists():
        segments_geojson = exporter.segments_to_geojson(segments_file)
        print(f"Segments exported to: {segments_geojson}")
        
        # Create Kepler.gl config
        config_file = exporter.create_kepler_config(segments_geojson, "outputs/train_movements.geojson")
        print(f"Kepler config created: {config_file}")
    else:
        print("❌ Segments file not found. Run K2 data fetcher first.")

if __name__ == "__main__":
    main()