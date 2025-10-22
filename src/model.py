from dataclasses import dataclass
import pandas as pd

@dataclass
class Segment:
    frm: str; to: str; length_m: float; speed_mps: float; tracks: int; signalling: str

class Line:
    def __init__(self, segments_df: pd.DataFrame):
        # Handle both old and new data formats
        self.segments = []
        for r in segments_df.itertuples():
            # Old format compatibility
            if hasattr(r, 'from_name'):
                frm, to = r.from_name, r.to_name
                length_km = r.length_km
                speed_kmh = r.speed_kmh
                tracks = getattr(r, 'tracks', 2)
                signalling = getattr(r, 'signalling', 'Unknown')
            # New K2 format
            elif hasattr(r, 'from_station'):
                frm, to = r.from_station, r.to_station
                length_km = r.length_km
                speed_kmh = getattr(r, 'max_speed_kmh', getattr(r, 'speed_kmh', 100))
                tracks = getattr(r, 'tracks', 2)
                signalling = getattr(r, 'signalling', 'Unknown')
            else:
                continue
                
            segment = Segment(
                frm=frm, 
                to=to, 
                length_m=length_km*1000,
                speed_mps=speed_kmh/3.6, 
                tracks=tracks, 
                signalling=signalling
            )
            self.segments.append(segment)
        
        # Calculate cumulative distances
        self.cum = [0.0]
        for s in self.segments: 
            self.cum.append(self.cum[-1] + s.length_m)
        self.total_m = self.cum[-1]

    def speed_limit(self, pos_m: float) -> float:
        # megkeresi melyik szegmensben vagyunk
        for i in range(len(self.segments)):
            if self.cum[i] <= pos_m < self.cum[i+1]:
                return self.segments[i].speed_mps
        return self.segments[-1].speed_mps
