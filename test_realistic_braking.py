"""
Test realisztikus fékezési mechanika szimulációval
"""
import pandas as pd
from src.model import Line
from src.train import TrainState
from src.sim import run_sim
from src.controllers import DistaAI_Simple
from src.braking import StandardTrainTypes, RailCondition

# Load test data
segments = pd.read_csv('data/segments.csv')
line = Line(segments)

print("=== REALISZTIKUS FÉKEZÉSI TESZT ===\n")
print(f"Pálya: {line.total_m/1000:.1f} km\n")

# Test 1: Modern EMU vs Simple modell
print("=== ÖSSZEHASONLÍTÁS: Valós vs Egyszerű modell ===\n")

# Egyszerű modell
simple_train = TrainState(0, pos_m=0.0, a_max=0.7, a_brake=0.7)
simple_trains = [simple_train]
controller = DistaAI_Simple()
controller_map = {0: controller}

results_simple = run_sim(line, simple_trains, controller_map, dt=0.5, T=1200)

print(f"EGYSZERŰ MODELL (a_brake = 0.7 m/s^2):")
print(f"  Befejezési idő: {results_simple[results_simple['finished']==True]['t'].min():.1f}s")
print(f"  Átlag sebesség: {results_simple['v'].mean() * 3.6:.1f} km/h")
print(f"  Max sebesség: {results_simple['v'].max() * 3.6:.1f} km/h")

# Valós EMU modell - száraz sín
emu_char = StandardTrainTypes.modern_emu()
realistic_train = TrainState(
    1, 
    pos_m=0.0, 
    a_max=0.7,
    braking_characteristics=emu_char,
    rail_condition=RailCondition.DRY
)
realistic_trains = [realistic_train]
controller_map2 = {1: controller}

results_realistic = run_sim(line, realistic_trains, controller_map2, dt=0.5, T=1200)

print(f"\nVALÓS EMU MODELL (száraz sín, P-fék 135%):")
print(f"  Befejezési idő: {results_realistic[results_realistic['finished']==True]['t'].min():.1f}s")
print(f"  Átlag sebesség: {results_realistic['v'].mean() * 3.6:.1f} km/h")
print(f"  Max sebesség: {results_realistic['v'].max() * 3.6:.1f} km/h")

# Test 2: Nedves sín hatása
print(f"\n=== SÍNÁLLAPOT HATÁSA ===\n")

for condition, name in [
    (RailCondition.DRY, "Száraz sín"),
    (RailCondition.WET, "Nedves sín"),
    (RailCondition.SLIPPERY, "Síkos sín")
]:
    train = TrainState(
        2, 
        pos_m=0.0,
        a_max=0.7,
        braking_characteristics=emu_char,
        rail_condition=condition
    )
    trains = [train]
    ctrl_map = {2: controller}
    
    results = run_sim(line, trains, ctrl_map, dt=0.5, T=1500)
    
    finished_rows = results[results['finished']==True]
    if not finished_rows.empty:
        finish_time = finished_rows['t'].min()
        avg_speed = results['v'].mean() * 3.6
        
        print(f"{name}:")
        print(f"  Befejezési idő: {finish_time:.1f}s ({finish_time/60:.1f} perc)")
        print(f"  Átlag sebesség: {avg_speed:.1f} km/h")
    else:
        print(f"{name}: NEM FEJEZTE BE {1500}s alatt!")

# Test 3: Különböző vonat típusok
print(f"\n=== VONAT TÍPUSOK ÖSSZEHASONLÍTÁSA ===\n")

train_types = [
    (StandardTrainTypes.modern_emu(), "Modern EMU (FLIRT)"),
    (StandardTrainTypes.ic_train(), "InterCity"),
    (StandardTrainTypes.regional_dmu(), "Regionális (Bzmot)"),
    (StandardTrainTypes.freight_train(), "Tehervonat")
]

for char, name in train_types:
    train = TrainState(
        3,
        pos_m=0.0,
        a_max=0.7,
        braking_characteristics=char,
        rail_condition=RailCondition.DRY
    )
    trains = [train]
    ctrl_map = {3: controller}
    
    results = run_sim(line, trains, ctrl_map, dt=0.5, T=2000)
    
    finished_rows = results[results['finished']==True]
    if not finished_rows.empty:
        finish_time = finished_rows['t'].min()
        avg_speed = results['v'].mean() * 3.6
        max_speed = results['v'].max() * 3.6
        
        print(f"{name}:")
        print(f"  Fékszázalék: {char.brake_percentage}%")
        print(f"  Fék típus: {char.brake_type.value}")
        print(f"  Tömeg: {char.mass_tons}t")
        print(f"  Befejezési idő: {finish_time:.1f}s ({finish_time/60:.1f} perc)")
        print(f"  Átlag sebesség: {avg_speed:.1f} km/h")
        print(f"  Max sebesség: {max_speed:.1f} km/h")
        print()
    else:
        print(f"{name}: NEM FEJEZTE BE 2000s alatt!")
        print(f"  (Valószínűleg túl lassú a tehervonat)")
        print()

print("\n=== FÉKEZÉSI TELJESÍTMÉNY ELEMZÉS ===\n")

# Részletes fékezési analízis 80→40 km/h átmenetnél
from src.braking import BrakingCalculator

calc = BrakingCalculator()

print("Féktávolság 80 km/h → 40 km/h átmenetnél:\n")

for char, name in train_types:
    distance, time = calc.calculate_braking_distance(
        v_initial_kmh=80.0,
        v_final_kmh=40.0,
        characteristics=char,
        rail_condition=RailCondition.DRY,
        include_reaction_time=True
    )
    
    a_max = calc.calculate_max_deceleration(char, RailCondition.DRY)
    
    print(f"{name}:")
    print(f"  Max lassulás: {a_max:.3f} m/s^2")
    print(f"  Féktávolság: {distance:.1f}m")
    print(f"  Fékezési idő: {time:.1f}s")
    print()
