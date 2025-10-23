import pandas as pd
from src.model import Line

# Load test data
segments = pd.read_csv('data/segments.csv')
line = Line(segments)

print(f'Total line distance: {line.total_m:.1f}m ({line.total_m/1000:.1f} km)')
print(f'\nCumulative distances: {line.cum}')

# Test speed limits at different positions
test_positions = [0, 1000, 5000, 6900, 7000, 10000, 12600, 13000, 15000, 18000, 18300]

print(f'\nSpeed limit tests:')
for pos in test_positions:
    speed_limit = line.speed_limit(pos)
    print(f'Position {pos:6.0f}m ({pos/1000:5.1f}km): Speed limit = {speed_limit*3.6:.0f} km/h')
    
print(f'\nSegment details:')
for i, seg in enumerate(line.segments):
    print(f'Segment {i}: {line.cum[i]:.0f}m - {line.cum[i+1]:.0f}m, Speed: {seg.speed_mps*3.6:.0f} km/h')
