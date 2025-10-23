import math
from typing import Optional
from .braking import (
    TrainBrakingCharacteristics,
    BrakingCalculator,
    RailCondition,
    StandardTrainTypes
)

class TrainState:
    def __init__(
        self, 
        train_id, 
        pos_m=0.0, 
        vel=0.0, 
        length_m=120.0, 
        a_max=0.7, 
        a_brake=0.7,
        braking_characteristics: Optional[TrainBrakingCharacteristics] = None,
        rail_condition: RailCondition = RailCondition.DRY
    ):
        self.id = train_id
        self.pos_m = max(0.0, pos_m)  # Position cannot be negative
        self.vel = max(0.0, vel)      # Velocity cannot be negative
        self.length_m = max(1.0, length_m)  # Train must have some length
        
        # Ha van valós fékezési karakter, azt használjuk
        if braking_characteristics:
            self.braking_char = braking_characteristics
            self.rail_condition = rail_condition
            self.use_realistic_braking = True
            
            # Számítsuk ki a valós lassulást
            calc = BrakingCalculator()
            self.a_brake = calc.calculate_service_brake_curve(
                self.vel * 3.6,  # km/h-ra
                self.braking_char,
                self.rail_condition
            )
            
            # Gyorsulás marad egyszerű (motorteljesítmény alapú lenne)
            self.a_max = max(0.01, a_max)
        else:
            # Egyszerű modell (kompatibilitás)
            self.use_realistic_braking = False
            self.a_max = max(0.01, a_max)
            self.a_brake = max(0.01, a_brake)
            self.braking_char = None
            self.rail_condition = RailCondition.DRY

    def step(self, dt, v_target, line):
        """Integrate one time step with physics constraints"""
        # Ensure non-negative target speed
        v_target = max(0.0, v_target)
        
        # Apply track speed limit to target
        vmax = line.speed_limit(self.pos_m)
        v_target = min(v_target, vmax)
        
        # Ha valós fékezési modell van, frissítsük a lassulást sebességfüggően
        if self.use_realistic_braking:
            calc = BrakingCalculator()
            # Üzemi fékezés sebességfüggő
            self.a_brake = calc.calculate_service_brake_curve(
                self.vel * 3.6,  # km/h
                self.braking_char,
                self.rail_condition
            )
        
        # Simple acceleration/deceleration towards target (with physical limits)
        if v_target > self.vel:   # accelerate
            self.vel = min(v_target, self.vel + self.a_max * dt)
        else:                     # decelerate/brake
            self.vel = max(v_target, self.vel - self.a_brake * dt)
        
        # Ensure velocity stays non-negative
        self.vel = max(0.0, self.vel)
        
        # Update position
        self.pos_m += self.vel * dt
        
        # Clamp position to stay within line bounds (don't go beyond end)
        self.pos_m = min(self.pos_m, line.total_m)
    
    def emergency_brake(self) -> float:
        """
        Vészfékezés - teljes fékhatás
        Returns: vészfék lassulás m/s²
        """
        if self.use_realistic_braking:
            calc = BrakingCalculator()
            return calc.calculate_emergency_brake(
                self.braking_char,
                self.rail_condition
            )
        else:
            # Vészfék: 1.5× normál fék
            return self.a_brake * 1.5
