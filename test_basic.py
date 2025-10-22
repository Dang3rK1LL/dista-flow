#!/usr/bin/env python3
"""
Simple unit tests for DISTA-Flow components
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
from src.model import Line
from src.train import TrainState
from src.controllers import EtcsBaseline, DistaAI_Simple, braking_distance
from src.metrics import compute_headways, throughput
from src.sim import run_sim

def test_braking_distance():
    """Test braking distance calculation"""
    print("Testing braking distance...")
    
    # v=30 m/s, a=1 m/s^2 => d = 30^2/(2*1) = 450m
    d = braking_distance(30, 1.0)
    assert abs(d - 450.0) < 0.1, f"Expected 450, got {d}"
    
    # v=0 => d=0
    d = braking_distance(0, 1.0)
    assert d == 0.0, f"Expected 0, got {d}"
    
    # Test edge case: a=0 should not crash
    d = braking_distance(10, 0.0)
    assert d > 0, "Should handle zero acceleration gracefully"
    
    print("✅ Braking distance tests passed")

def test_headway_calculation():
    """Test headway computation with known train positions"""
    print("Testing headway calculation...")
    
    # Create test data: 2 trains at t=0
    data = [
        {'t': 0.0, 'id': 'T1', 'pos_m': 0.0, 'v': 20.0},      # rear train
        {'t': 0.0, 'id': 'T2', 'pos_m': 500.0, 'v': 20.0},    # front train
        {'t': 1.0, 'id': 'T1', 'pos_m': 20.0, 'v': 20.0},     
        {'t': 1.0, 'id': 'T2', 'pos_m': 520.0, 'v': 20.0},    
    ]
    df = pd.DataFrame(data)
    
    hw = compute_headways(df, train_length=120.0)
    
    # Expected gap at t=0: 500 - (0 + 120) = 380m
    expected_gap = 380.0
    actual_gap = hw[hw['t'] == 0.0]['gap_m'].iloc[0]
    assert abs(actual_gap - expected_gap) < 0.1, f"Expected {expected_gap}, got {actual_gap}"
    
    print("✅ Headway calculation tests passed")

def test_finish_detection():
    """Test that trains are detected when they finish"""
    print("Testing finish detection...")
    
    # Load short test data
    test_segments = pd.DataFrame([
        {'from_name': 'A', 'to_name': 'B', 'length_km': 5.0, 'speed_kmh': 100, 'tracks': 2, 'signalling': 'ETCS'}
    ])
    line = Line(test_segments)
    
    # Single train starting near the end
    trains = [TrainState('T1', pos_m=4500.0, vel=25.0, length_m=120)]  # 500m from end
    controllers = {'T1': EtcsBaseline(1.0, 100.0)}
    
    # Short simulation
    df = run_sim(line, trains, controllers, dt=0.5, T=60)
    
    # Check that train reached the end
    max_pos = df['pos_m'].max()
    assert max_pos >= line.total_m - 1.0, f"Train should reach end {line.total_m}, max pos: {max_pos}"
    
    tput = throughput(df, line.total_m)
    assert tput >= 1, f"Should have 1 finished train, got {tput}"
    
    print("✅ Finish detection tests passed")

def test_controller_safety():
    """Test that controllers don't command negative speeds"""
    print("Testing controller safety...")
    
    # Create simple line
    segments = pd.DataFrame([
        {'from_name': 'A', 'to_name': 'B', 'length_km': 1.0, 'speed_kmh': 80, 'tracks': 2, 'signalling': 'ETCS'}
    ])
    line = Line(segments)
    
    # Two trains very close together
    train1 = TrainState('T1', pos_m=0.0, vel=22.0)    # following
    train2 = TrainState('T2', pos_m=150.0, vel=22.0)  # leading
    
    ctrl = EtcsBaseline(reaction_s=2.0, margin_m=100.0)
    
    # Test desired speed when too close
    v_des = ctrl.desired_speed(train1, train2, line)
    
    assert v_des >= 0.0, f"Desired speed must be non-negative, got {v_des}"
    assert v_des <= 25.0, f"Desired speed too high: {v_des}"  # reasonable upper bound
    
    print("✅ Controller safety tests passed")

if __name__ == "__main__":
    print("Running DISTA-Flow unit tests...\n")
    
    try:
        test_braking_distance()
        test_headway_calculation()
        test_controller_safety()
        test_finish_detection()
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)