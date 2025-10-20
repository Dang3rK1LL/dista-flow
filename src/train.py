import math

class TrainState:
    def __init__(self, train_id, pos_m=0.0, vel=0.0, length_m=120.0, a_max=0.7, a_brake=0.7):
        self.id = train_id; self.pos_m = pos_m; self.vel = vel
        self.length_m = length_m; self.a_max = a_max; self.a_brake = a_brake

    def step(self, dt, v_target, line):
        # egyszerű gyorsítás/fékezés
        if v_target > self.vel:   # gyorsít
            self.vel = min(v_target, self.vel + self.a_max*dt)
        else:                     # fékez
            self.vel = max(v_target, self.vel - self.a_brake*dt)

        # pályakorlát
        vmax = line.speed_limit(self.pos_m)
        self.vel = min(self.vel, vmax)
        self.pos_m += self.vel * dt
