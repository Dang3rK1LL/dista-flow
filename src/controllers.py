import math

def braking_distance(v, a_eff):  # v [m/s], a_eff [m/s^2]
    """Fékút számítás: v^2 / (2*a)"""
    return (v*v) / (2.0 * max(a_eff, 1e-6))

class EtcsBaseline:
    def __init__(self, reaction_s=2.0, margin_m=150.0):
        self.tr = max(0.0, reaction_s)  # protect against negative reaction time
        self.margin = max(0.0, margin_m)  # protect against negative margin
        
    def desired_speed(self, me, leader, line):
        # alap cél: menni a pályasebességgel
        vlim = line.speed_limit(me.pos_m)
        if leader:
            # gap = távolság az elülső vonat hátulja és az én orrom között
            gap = (leader.pos_m - leader.length_m) - me.pos_m
            # d_safe = saját fékút + reakcióidő * saját sebesség + margin
            # (NEM adjuk hozzá a leader length_m-et újra!)
            dsafe = braking_distance(me.vel, me.a_brake) + me.vel * self.tr + self.margin
            if gap < dsafe:
                # fékezés szükséges - fokozatos lassítás
                return max(0.0, me.vel - me.a_brake)  # 1s alatt fékezne ennyit
        return vlim

class DistaAI_Simple:
    def __init__(self, reaction_s=0.8, margin_m=100.0):
        self.tr = max(0.0, reaction_s)
        self.margin = max(0.0, margin_m)
        
    def desired_speed(self, me, leader, line):
        vlim = line.speed_limit(me.pos_m)
        if leader:
            gap = (leader.pos_m - leader.length_m) - me.pos_m
            dsafe = braking_distance(me.vel, me.a_brake) + me.vel * self.tr + self.margin
            if gap < dsafe: 
                return max(0.0, me.vel - me.a_brake)
        # AI: ha nagy a mozgástér, proaktívan közelít vlim-hez (simább profil)
        return min(vlim, me.vel + 0.5*me.a_max)
