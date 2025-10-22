import math

class TrainState:
    def __init__(self, train_id, pos_m=0.0, vel=0.0, length_m=120.0, a_max=0.7, a_brake=0.7):
        self.id = train_id
        self.pos_m = max(0.0, pos_m)  # Position cannot be negative
        self.vel = max(0.0, vel)      # Velocity cannot be negative
        self.length_m = max(1.0, length_m)  # Train must have some length
        self.a_max = max(0.01, a_max)     # Must be able to accelerate
        self.a_brake = max(0.01, a_brake) # Must be able to brake

    def step(self, dt, v_target, line):
        """Integrate one time step with physics constraints"""
        # Ensure non-negative target speed
        v_target = max(0.0, v_target)
        
        # Simple acceleration/deceleration towards target
        if v_target > self.vel:   # accelerate
            self.vel = min(v_target, self.vel + self.a_max * dt)
        else:                     # decelerate/brake
            self.vel = max(v_target, self.vel - self.a_brake * dt)

        # Apply track speed limit
        vmax = line.speed_limit(self.pos_m)
        self.vel = min(self.vel, vmax)
        
        # Ensure velocity stays non-negative
        self.vel = max(0.0, self.vel)
        
        # Update position
        self.pos_m += self.vel * dt
        
        # Clamp position to stay within line bounds (don't go beyond end)
        self.pos_m = min(self.pos_m, line.total_m)
