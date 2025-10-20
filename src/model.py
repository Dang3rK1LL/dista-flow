from dataclasses import dataclass
import pandas as pd

@dataclass
class Segment:
    frm: str; to: str; length_m: float; speed_mps: float; tracks: int; signalling: str

class Line:
    def __init__(self, segments_df: pd.DataFrame):
        self.segments = [Segment(r.from_name, r.to_name, r.length_km*1000,
                                 r.speed_kmh/3.6, r.tracks, r.signalling)
                         for r in segments_df.itertuples()]
        self.cum = [0.0]
        for s in self.segments: self.cum.append(self.cum[-1] + s.length_m)
        self.total_m = self.cum[-1]

    def speed_limit(self, pos_m: float) -> float:
        # megkeresi melyik szegmensben vagyunk
        for i in range(len(self.segments)):
            if self.cum[i] <= pos_m < self.cum[i+1]:
                return self.segments[i].speed_mps
        return self.segments[-1].speed_mps
