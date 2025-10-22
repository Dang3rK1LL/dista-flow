#!/usr/bin/env python3
"""
Advanced AI Controllers for DISTA-Flow
Implements Level 2 (Predictive) and Level 3 (Reinforcement Learning) controllers
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
import warnings

# Try to import ML libraries, fall back gracefully if not available
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    warnings.warn("XGBoost not available. Predictive AI controller will use fallback logic.")

try:
    import gym
    from stable_baselines3 import PPO
    HAS_RL = True
except ImportError:
    HAS_RL = False
    warnings.warn("Reinforcement Learning libraries not available. RL controller will use fallback logic.")

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.controllers import EtcsBaseline, DistaAI_Simple, braking_distance

class DistaAI_Predictive:
    """
    Level 2 AI Controller: Uses XGBoost/LightGBM for predictive train following
    """
    
    def __init__(self, reaction_s=0.8, margin_m=80.0, model_path: Optional[Path] = None):
        self.tr = max(0.0, reaction_s)
        self.margin = max(0.0, margin_m)
        self.model_path = model_path
        self.model = None
        self.feature_buffer = []  # Store recent states for temporal features
        self.buffer_size = 10
        
        # Load pre-trained model if available
        if self.model_path and self.model_path.exists() and HAS_XGBOOST:
            try:
                self.model = xgb.Booster()
                self.model.load_model(str(self.model_path))
                print(f"✅ Loaded pre-trained AI model from {self.model_path}")
            except Exception as e:
                print(f"⚠️ Failed to load AI model: {e}. Using fallback logic.")
                self.model = None
    
    def desired_speed(self, me, leader, line):
        """
        AI-enhanced speed decision using predictive model
        """
        # Get track speed limit
        vlim = line.speed_limit(me.pos_m)
        
        # If no leader, go full speed
        if not leader:
            return vlim
        
        # Calculate basic safety features
        gap = (leader.pos_m - leader.length_m) - me.pos_m
        rel_speed = me.vel - leader.vel
        
        # Create feature vector for ML model
        features = self._extract_features(me, leader, line, gap, rel_speed)
        
        # Use AI model if available, otherwise fall back to enhanced heuristics
        if self.model and HAS_XGBOOST:
            target_speed = self._predict_with_model(features, vlim)
        else:
            target_speed = self._fallback_logic(me, leader, line, gap, rel_speed, vlim)
        
        return max(0.0, min(target_speed, vlim))
    
    def _extract_features(self, me, leader, line, gap, rel_speed) -> np.ndarray:
        """
        Extract features for ML prediction
        """
        # Current state features
        current_features = [
            me.vel,                    # Own speed
            leader.vel,                # Leader speed
            gap,                       # Current gap
            rel_speed,                 # Relative speed
            me.a_max,                  # Own max acceleration
            me.a_brake,                # Own braking capability
            line.speed_limit(me.pos_m), # Track speed limit
            me.pos_m / 1000.0,         # Position along line (km)
        ]
        
        # Add this state to buffer
        self.feature_buffer.append(current_features)
        if len(self.feature_buffer) > self.buffer_size:
            self.feature_buffer.pop(0)
        
        # Temporal features (moving averages, derivatives)
        if len(self.feature_buffer) >= 2:
            recent_speeds = [f[0] for f in self.feature_buffer[-5:]]
            recent_gaps = [f[2] for f in self.feature_buffer[-5:]]
            
            speed_trend = np.mean(np.diff(recent_speeds)) if len(recent_speeds) > 1 else 0
            gap_trend = np.mean(np.diff(recent_gaps)) if len(recent_gaps) > 1 else 0
            speed_variance = np.var(recent_speeds)
        else:
            speed_trend = gap_trend = speed_variance = 0
        
        # Combine all features
        extended_features = current_features + [
            speed_trend,               # Speed change trend
            gap_trend,                 # Gap change trend  
            speed_variance,            # Speed stability
            braking_distance(me.vel, me.a_brake),  # Current braking distance
        ]
        
        return np.array(extended_features, dtype=np.float32)
    
    def _predict_with_model(self, features: np.ndarray, vlim: float) -> float:
        """
        Use trained XGBoost model to predict optimal speed
        """
        try:
            # Reshape for XGBoost prediction
            dmatrix = xgb.DMatrix(features.reshape(1, -1))
            prediction = self.model.predict(dmatrix)[0]
            
            # Clamp prediction to reasonable bounds
            return max(0.0, min(prediction, vlim))
            
        except Exception as e:
            print(f"⚠️ AI prediction failed: {e}. Using fallback.")
            return self._fallback_logic_simple(features, vlim)
    
    def _fallback_logic(self, me, leader, line, gap, rel_speed, vlim) -> float:
        """
        Enhanced heuristic logic when AI model is not available
        """
        # Calculate enhanced safety distance with predictive elements
        base_braking_dist = braking_distance(me.vel, me.a_brake)
        reaction_dist = me.vel * self.tr
        
        # Adaptive margin based on relative speed and gap trend
        adaptive_margin = self.margin
        
        # If closing in too fast, increase margin
        if rel_speed > 2.0:  # Approaching 2 m/s faster than leader
            adaptive_margin *= 1.5
        elif rel_speed < -1.0:  # Leader pulling away
            adaptive_margin *= 0.8
        
        # Predictive gap requirement
        d_safe = base_braking_dist + reaction_dist + adaptive_margin
        
        if gap < d_safe:
            # Graduated response instead of hard braking
            urgency = max(0.0, (d_safe - gap) / d_safe)
            brake_factor = 0.3 + 0.7 * urgency  # Scale from gentle to full braking
            
            return max(0.0, me.vel - me.a_brake * brake_factor)
        else:
            # Smart acceleration: approach speed limit smoothly
            speed_diff = vlim - me.vel
            if speed_diff > 0:
                # Proportional acceleration based on available gap
                gap_factor = min(1.0, gap / (d_safe * 1.5))
                accel_factor = 0.3 + 0.7 * gap_factor
                return min(vlim, me.vel + me.a_max * accel_factor)
            else:
                return vlim
    
    def _fallback_logic_simple(self, features: np.ndarray, vlim: float) -> float:
        """
        Simple fallback when everything else fails
        """
        current_speed = features[0]
        return min(vlim, current_speed + 0.5)
    
    def save_training_data(self, simulation_df: pd.DataFrame, output_file: Path):
        """
        Save simulation data in format suitable for ML training
        """
        training_data = []
        
        # Process simulation data to create training examples
        for train_id, train_data in simulation_df.groupby('id'):
            train_data = train_data.sort_values('t')
            
            for i in range(1, len(train_data)):
                current = train_data.iloc[i]
                previous = train_data.iloc[i-1]
                
                # Features from previous state, target from current state
                features = {
                    'prev_speed': previous['v'],
                    'current_speed': current['v'],
                    'position': current['pos_m'],
                    'speed_change': current['v'] - previous['v'],
                    'time_delta': current['t'] - previous['t'],
                    'train_id': train_id
                }
                
                training_data.append(features)
        
        # Save to CSV
        pd.DataFrame(training_data).to_csv(output_file, index=False)
        print(f"✅ Saved {len(training_data)} training samples to {output_file}")

class DistaAI_RL:
    """
    Level 3 AI Controller: Reinforcement Learning based train following
    """
    
    def __init__(self, reaction_s=0.5, margin_m=60.0, model_path: Optional[Path] = None):
        self.tr = max(0.0, reaction_s)
        self.margin = max(0.0, margin_m)
        self.model_path = model_path
        self.model = None
        self.state_buffer = []
        
        # Load pre-trained RL model if available
        if self.model_path and self.model_path.exists() and HAS_RL:
            try:
                self.model = PPO.load(str(self.model_path))
                print(f"✅ Loaded pre-trained RL model from {self.model_path}")
            except Exception as e:
                print(f"⚠️ Failed to load RL model: {e}. Using fallback logic.")
                self.model = None
    
    def desired_speed(self, me, leader, line):
        """
        RL-based speed decision
        """
        vlim = line.speed_limit(me.pos_m)
        
        if not leader:
            return vlim
        
        # Create state vector for RL agent
        state = self._create_state(me, leader, line)
        
        if self.model and HAS_RL:
            try:
                # Get action from RL model
                action, _ = self.model.predict(state, deterministic=True)
                target_speed = self._action_to_speed(action, me, vlim)
                return max(0.0, min(target_speed, vlim))
            except Exception as e:
                print(f"⚠️ RL prediction failed: {e}. Using fallback.")
        
        # Fallback to aggressive but safe heuristic
        return self._rl_fallback(me, leader, line, vlim)
    
    def _create_state(self, me, leader, line) -> np.ndarray:
        """
        Create state vector for RL agent
        """
        gap = (leader.pos_m - leader.length_m) - me.pos_m
        rel_speed = me.vel - leader.vel
        
        state = np.array([
            me.vel / 50.0,                    # Normalized own speed
            leader.vel / 50.0,                # Normalized leader speed  
            gap / 1000.0,                     # Normalized gap
            rel_speed / 20.0,                 # Normalized relative speed
            line.speed_limit(me.pos_m) / 50.0, # Normalized speed limit
            me.pos_m / 200000.0,              # Normalized position
        ], dtype=np.float32)
        
        return state
    
    def _action_to_speed(self, action: np.ndarray, me, vlim: float) -> float:
        """
        Convert RL action to target speed
        """
        # Assume action is acceleration command in range [-1, 1]
        accel_command = np.clip(action[0], -1.0, 1.0)
        
        if accel_command > 0:
            target_speed = me.vel + accel_command * me.a_max
        else:
            target_speed = me.vel + accel_command * me.a_brake
        
        return max(0.0, min(target_speed, vlim))
    
    def _rl_fallback(self, me, leader, line, vlim) -> float:
        """
        Aggressive but safe fallback logic for RL controller
        """
        gap = (leader.pos_m - leader.length_m) - me.pos_m
        d_safe = braking_distance(me.vel, me.a_brake) + me.vel * self.tr + self.margin
        
        if gap < d_safe * 0.8:  # More aggressive threshold
            return max(0.0, me.vel - me.a_brake * 0.8)
        elif gap > d_safe * 2.0:  # Plenty of room
            return min(vlim, me.vel + me.a_max * 0.8)
        else:
            return min(vlim, me.vel + me.a_max * 0.3)

# Factory function for easy controller creation
def create_controller(controller_type: str, **kwargs):
    """
    Factory function to create controllers
    """
    controllers = {
        'etcs': EtcsBaseline,
        'dista_simple': DistaAI_Simple,  # From original controllers.py
        'dista_predictive': DistaAI_Predictive,
        'dista_rl': DistaAI_RL,
    }
    
    if controller_type.lower() not in controllers:
        raise ValueError(f"Unknown controller type: {controller_type}")
    
    return controllers[controller_type.lower()](**kwargs)

def main():
    """Demo usage of AI controllers"""
    print("🤖 DISTA-Flow AI Controllers Demo")
    
    # Test predictive controller
    print("\n1. Testing Predictive AI Controller...")
    pred_controller = DistaAI_Predictive(reaction_s=0.6, margin_m=70.0)
    print(f"   Created: {pred_controller.__class__.__name__}")
    print(f"   XGBoost available: {HAS_XGBOOST}")
    
    # Test RL controller  
    print("\n2. Testing RL Controller...")
    rl_controller = DistaAI_RL(reaction_s=0.4, margin_m=50.0)
    print(f"   Created: {rl_controller.__class__.__name__}")
    print(f"   RL libraries available: {HAS_RL}")
    
    # Test factory function
    print("\n3. Testing Factory Function...")
    try:
        etcs_ctrl = create_controller('etcs', reaction_s=2.0, margin_m=180.0)
        print(f"   Created ETCS controller: {etcs_ctrl.__class__.__name__}")
    except Exception as e:
        print(f"   Factory error: {e}")

if __name__ == "__main__":
    main()