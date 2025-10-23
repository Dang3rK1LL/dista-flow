"""
Gyors eredmény elemzés a szimulációról
"""
import sys
sys.path.append('src')

from src.model import Line
from src.sim import run_sim
from src.controllers import DistaAI_Simple, EtcsBaseline
from src.braking import StandardTrainTypes, RailCondition
from src.train import TrainState
import pandas as pd
import numpy as np

def analyze_simulation():
    print("\n" + "="*70)
    print("🚂 DISTA-FLOW SZIMULÁCIÓ EREDMÉNY ELEMZÉS")
    print("="*70)
    
    # Load line data
    df = pd.read_csv('data/segments.csv')
    line = Line(df)
    
    print(f"\n📍 Vonal információk:")
    print(f"   Hossz: {line.total_m/1000:.1f} km")
    print(f"   Szegmensek: {len(line.segments)}")
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Modern EMU (FLIRT) - Száraz sín',
            'train_type': StandardTrainTypes.modern_emu(),
            'rail_condition': RailCondition.DRY,
            'controller': DistaAI_Simple,
            'num_trains': 5
        },
        {
            'name': 'InterCity - Nedves sín',
            'train_type': StandardTrainTypes.ic_train(),
            'rail_condition': RailCondition.WET,
            'controller': DistaAI_Simple,
            'num_trains': 5
        },
        {
            'name': 'Tehervonat - Száraz sín',
            'train_type': StandardTrainTypes.freight_train(),
            'rail_condition': RailCondition.DRY,
            'controller': DistaAI_Simple,
            'num_trains': 3
        }
    ]
    
    results_summary = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─'*70}")
        print(f"📊 SZCENÁRIÓ {i}: {scenario['name']}")
        print(f"{'─'*70}")
        
        # Run simulation
        trains = []
        for i in range(scenario['num_trains']):
            train = TrainState(
                i,
                pos_m=i * 1000.0,
                braking_characteristics=scenario['train_type'],
                rail_condition=scenario['rail_condition']
            )
            trains.append(train)
        
        controller = scenario['controller']()
        controller_map = {train.id: controller for train in trains}
        
        # Run simulation
        results_df = run_sim(
            line,
            trains,
            controller_map,
            dt=0.5,
            T=8000.0
        )
        
        # Calculate statistics from results
        finished_count = len([t for t in trains if t.pos_m >= line.total_m - 1.0])
        total = len(trains)
        sim_time = results_df['t'].max()
        
        # Calculate statistics
        velocities = [t.vel * 3.6 for t in trains]  # km/h
        positions = [t.pos_m / 1000 for t in trains]  # km
        
        avg_vel = np.mean(velocities)
        max_vel = np.max(velocities)
        min_vel = np.min(velocities)
        
        # Calculate distances between trains
        sorted_positions = sorted([t.pos_m for t in trains])
        distances = [sorted_positions[i+1] - sorted_positions[i] 
                    for i in range(len(sorted_positions)-1)]
        min_distance = min(distances) if distances else 0
        avg_distance = np.mean(distances) if distances else 0
        
        # Calculate completion percentage
        completion_pct = [(t.pos_m / line.total_m * 100) for t in trains]
        avg_completion = np.mean(completion_pct)
        
        print(f"\n✅ Befejezés:")
        print(f"   Befejezett vonatok: {finished_count}/{total} ({finished_count/total*100:.0f}%)")
        print(f"   Szimuláció idő: {sim_time:.1f}s ({sim_time/60:.1f} perc)")
        
        print(f"\n🚄 Sebességek:")
        print(f"   Átlag: {avg_vel:.1f} km/h")
        print(f"   Maximum: {max_vel:.1f} km/h")
        print(f"   Minimum: {min_vel:.1f} km/h")
        
        print(f"\n📍 Pozíciók:")
        print(f"   Átlagos előrehaladás: {avg_completion:.1f}%")
        for j, train in enumerate(trains):
            pct = (train.pos_m / line.total_m * 100)
            print(f"   Vonat {j}: {train.pos_m/1000:.1f} km ({pct:.1f}%)")
        
        print(f"\n🛡️ Biztonság (távolságok vonatok között):")
        print(f"   Minimum távolság: {min_distance:.0f}m")
        print(f"   Átlag távolság: {avg_distance:.0f}m")
        print(f"   Biztonságos? {'✅ IGEN' if min_distance >= 500 else '⚠️ NEM'}")
        
        # Store summary
        results_summary.append({
            'scenario': scenario['name'],
            'finished_rate': f"{finished_count}/{total}",
            'time_min': f"{sim_time/60:.1f}",
            'avg_speed_kmh': f"{avg_vel:.1f}",
            'min_distance_m': f"{min_distance:.0f}",
            'safe': '✅' if min_distance >= 500 else '⚠️'
        })
    
    # Summary table
    print(f"\n{'='*70}")
    print("📋 ÖSSZEFOGLALÓ TÁBLÁZAT")
    print(f"{'='*70}")
    print(f"{'Szcenárió':<35} {'Befejezett':<12} {'Idő(p)':<10} {'Átl.seb':<10} {'Min.táv':<10} {'Biztonság'}")
    print(f"{'-'*70}")
    for r in results_summary:
        print(f"{r['scenario']:<35} {r['finished_rate']:<12} {r['time_min']:<10} {r['avg_speed_kmh']:<10} {r['min_distance_m']:<10} {r['safe']}")
    
    print(f"\n{'='*70}")
    print("✅ ELEMZÉS KÉSZ")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    analyze_simulation()
