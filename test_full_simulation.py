"""
Teljes körű élő teszt - Realisztikus vonat szimuláció
"""
import pandas as pd
from src.model import Line
from src.train import TrainState
from src.sim import run_sim
from src.controllers import DistaAI_Simple
from src.braking import StandardTrainTypes, RailCondition
from datetime import datetime

print("=" * 70)
print("  DISTA-FLOW ÉLÉS SZIMULÁCIÓS TESZT")
print("  Magyar Vasúti Infrastruktúra Szimuláció")
print("=" * 70)
print(f"\nIndítás: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load railway segments
segments = pd.read_csv('data/segments.csv')
line = Line(segments)

print(f"📍 Pálya adatok:")
print(f"   Teljes hossz: {line.total_m/1000:.1f} km")
print(f"   Szegmensek: {len(line.segments)} db")
for i, seg in enumerate(line.segments):
    print(f"   {i+1}. {seg.frm} → {seg.to}: {seg.length_m/1000:.1f} km, {seg.speed_mps*3.6:.0f} km/h, {seg.signalling}")

# Test scenarios
scenarios = [
    {
        "name": "Modern EMU Flotta (Száraz sín)",
        "num_trains": 3,
        "train_type": StandardTrainTypes.modern_emu(),
        "rail_condition": RailCondition.DRY,
        "simulation_time": 1200
    },
    {
        "name": "InterCity Vonatok (Nedves sín)",
        "num_trains": 2,
        "train_type": StandardTrainTypes.ic_train(),
        "rail_condition": RailCondition.WET,
        "simulation_time": 1200
    },
    {
        "name": "Vegyes Forgalom (Regionális + Teher)",
        "num_trains": 4,
        "train_type": StandardTrainTypes.regional_dmu(),
        "rail_condition": RailCondition.DRY,
        "simulation_time": 1500
    }
]

all_results = []

for scenario in scenarios:
    print("\n" + "=" * 70)
    print(f"🚂 SZCENÁRIÓ: {scenario['name']}")
    print("=" * 70)
    
    # Create trains
    trains = []
    for i in range(scenario['num_trains']):
        train = TrainState(
            train_id=i,
            pos_m=i * 1500.0,  # 1.5 km spacing
            braking_characteristics=scenario['train_type'],
            rail_condition=scenario['rail_condition']
        )
        trains.append(train)
    
    print(f"\n📋 Paraméterek:")
    print(f"   Vonatok száma: {scenario['num_trains']}")
    print(f"   Vonat típus: {scenario['train_type'].train_type}")
    print(f"   Fékszázalék: {scenario['train_type'].brake_percentage}%")
    print(f"   Fék típus: {scenario['train_type'].brake_type.value}")
    print(f"   Tömeg: {scenario['train_type'].mass_tons}t")
    print(f"   Sínállapot: {scenario['rail_condition'].value}")
    print(f"   Szimulációs idő: {scenario['simulation_time']}s ({scenario['simulation_time']/60:.1f} perc)")
    
    # Setup controller
    controller = DistaAI_Simple()
    controller_map = {train.id: controller for train in trains}
    
    # Run simulation
    print(f"\n⏳ Szimuláció futtatása...")
    results = run_sim(
        line, 
        trains, 
        controller_map, 
        dt=0.5, 
        T=scenario['simulation_time']
    )
    
    # Analyze results
    print(f"\n📊 Eredmények:")
    print(f"   Pozíciók naplózva: {len(results)} db")
    
    finished_trains = results[results['finished'] == True]['id'].unique()
    print(f"   Befejezett vonatok: {len(finished_trains)}/{scenario['num_trains']}")
    
    for train_id in range(scenario['num_trains']):
        train_data = results[results['id'] == train_id]
        max_speed = train_data['v'].max() * 3.6
        avg_speed = train_data['v'].mean() * 3.6
        final_pos = train_data['pos_m'].iloc[-1]
        
        finished_rows = train_data[train_data['finished'] == True]
        if not finished_rows.empty:
            finish_time = finished_rows['t'].min()
            status = f"✅ Befejezve {finish_time:.0f}s ({finish_time/60:.1f} perc)"
        else:
            status = f"🔄 Fut... ({final_pos/1000:.1f} km)"
        
        print(f"\n   Vonat #{train_id}:")
        print(f"      Státusz: {status}")
        print(f"      Max sebesség: {max_speed:.1f} km/h")
        print(f"      Átlag sebesség: {avg_speed:.1f} km/h")
        print(f"      Végleges pozíció: {final_pos/1000:.1f} km")
    
    # Safety check
    print(f"\n🔒 Biztonsági ellenőrzés:")
    min_gap = float('inf')
    for t in sorted(results['t'].unique()):
        rows = results[results['t'] == t].sort_values('pos_m')
        positions = rows['pos_m'].values
        if len(positions) > 1:
            for i in range(len(positions) - 1):
                gap = positions[i+1] - positions[i]
                min_gap = min(min_gap, gap)
    
    if min_gap < 200:
        print(f"   ⚠️  FIGYELMEZTETÉS: Minimum távolság {min_gap:.1f}m")
    else:
        print(f"   ✅ BIZTONSÁGOS: Minimum távolság {min_gap:.1f}m")
    
    # Store for summary
    all_results.append({
        'scenario': scenario['name'],
        'trains': scenario['num_trains'],
        'finished': len(finished_trains),
        'min_gap': min_gap
    })

# Final summary
print("\n" + "=" * 70)
print("📈 ÖSSZEFOGLALÁS")
print("=" * 70)

for result in all_results:
    completion = (result['finished'] / result['trains']) * 100
    safety = "✅" if result['min_gap'] >= 200 else "⚠️"
    
    print(f"\n{result['scenario']}:")
    print(f"   Befejezés: {result['finished']}/{result['trains']} ({completion:.0f}%)")
    print(f"   Biztonság: {safety} ({result['min_gap']:.1f}m minimum távolság)")

print("\n" + "=" * 70)
print("✅ TESZT BEFEJEZVE")
print("=" * 70)
print(f"\nBefejezés: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n💡 A szimuláció teljesen realisztikus fékezési modellt használ!")
print("   - UIC 544-1 szabvány szerint")
print("   - Magyar vasúti szabályozás (D.54)")
print("   - Fékszázalék alapú számítás")
print("   - Tapadási viszonyok figyelembevételével\n")
