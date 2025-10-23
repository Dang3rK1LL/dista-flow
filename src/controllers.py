import math

def braking_distance(v, a_eff):  # v [m/s], a_eff [m/s^2]
    """Fékút számítás: v^2 / (2*a)"""
    if a_eff <= 0:
        return float('inf')
    return (v*v) / (2.0 * max(a_eff, 1e-6))

def braking_distance_with_reaction(me, leader=None, margin_m=100.0, reaction_s=0.8):
    """
    Biztonságos féktávolság reakcióidővel
    
    Args:
        me: TrainState objektum
        leader: Elöl haladó vonat (opcionális)
        margin_m: Biztonsági margó méterben
        reaction_s: Reakcióidő másodpercben
    
    Returns:
        Szükséges biztonságos távolság méterben
    """
    # Ha valós fékezési modell van, azt használjuk
    if hasattr(me, 'use_realistic_braking') and me.use_realistic_braking:
        from .braking import BrakingCalculator
        calc = BrakingCalculator()
        
        # Számítsuk ki a valós féktávolságot
        distance, _ = calc.calculate_braking_distance(
            v_initial_kmh=me.vel * 3.6,
            v_final_kmh=0.0,
            characteristics=me.braking_char,
            rail_condition=me.rail_condition,
            include_reaction_time=True
        )
        
        return distance + margin_m
    else:
        # Egyszerű modell
        reaction_distance = me.vel * reaction_s
        brake_distance = braking_distance(me.vel, me.a_brake)
        return reaction_distance + brake_distance + margin_m

class EtcsBaseline:
    def __init__(self, reaction_s=2.0, margin_m=150.0):
        self.tr = max(0.0, reaction_s)  # protect against negative reaction time
        self.margin = max(0.0, margin_m)  # protect against negative margin
        
    def desired_speed(self, me, leader, line):
        # alap cél: menni a pályasebességgel
        vlim = line.speed_limit(me.pos_m)
        
        # Check for upcoming speed limit changes
        dist_to_change, next_vlim = line.next_speed_change(me.pos_m)
        
        # If speed limit will decrease ahead, start slowing down in advance
        if next_vlim < vlim:
            # Calculate braking distance needed to slow down from current speed to next limit
            braking_dist = braking_distance(me.vel, me.a_brake)
            target_braking_dist = braking_distance(next_vlim, me.a_brake)
            needed_dist = braking_dist - target_braking_dist
            
            # If we need to start braking soon, reduce target speed
            if dist_to_change <= needed_dist + self.margin:
                # Calculate appropriate target speed to reach next_vlim at the boundary
                safe_distance = max(0.0, dist_to_change - self.margin)
                v_target_squared = next_vlim**2 + 2.0 * me.a_brake * safe_distance
                v_target = (v_target_squared ** 0.5) if v_target_squared > 0 else 0.0
                vlim = min(vlim, v_target)
        
        if leader:
            # gap = távolság az elülső vonat hátulja és az én orrom között
            gap = (leader.pos_m - leader.length_m) - me.pos_m
            # d_safe = saját fékút + reakcióidő * saját sebesség + margin
            # (NEM adjuk hozzá a leader length_m-et újra!)
            dsafe = braking_distance(me.vel, me.a_brake) + me.vel * self.tr + self.margin
            if gap < dsafe:
                # Számítsuk ki a szükséges célsebességet a biztonságos követéshez
                # v_target^2 = 2 * a * (gap - margin - v*tr)
                safe_distance = max(0.0, gap - self.margin - me.vel * self.tr)
                v_target_squared = 2.0 * me.a_brake * safe_distance
                v_target = (v_target_squared ** 0.5) if v_target_squared > 0 else 0.0
                return min(vlim, v_target)
        return vlim

class DistaAI_Simple:
    def __init__(self, reaction_s=0.8, margin_m=100.0):
        self.tr = max(0.0, reaction_s)
        self.margin = max(0.0, margin_m)
        
    def desired_speed(self, me, leader, line):
        vlim = line.speed_limit(me.pos_m)
        
        # Check for upcoming speed limit changes (AI looks ahead!)
        dist_to_change, next_vlim = line.next_speed_change(me.pos_m)
        
        # If speed limit will decrease ahead, start slowing down in advance
        if next_vlim < vlim:
            # Calculate braking distance needed
            braking_dist = braking_distance(me.vel, me.a_brake)
            target_braking_dist = braking_distance(next_vlim, me.a_brake)
            needed_dist = braking_dist - target_braking_dist
            
            # AI is more aggressive - starts braking earlier
            if dist_to_change <= needed_dist + self.margin:
                safe_distance = max(0.0, dist_to_change - self.margin)
                v_target_squared = next_vlim**2 + 2.0 * me.a_brake * safe_distance
                v_target = (v_target_squared ** 0.5) if v_target_squared > 0 else 0.0
                vlim = min(vlim, v_target)
        
        if leader:
            gap = (leader.pos_m - leader.length_m) - me.pos_m
            dsafe = braking_distance(me.vel, me.a_brake) + me.vel * self.tr + self.margin
            if gap < dsafe:
                # Számítsuk ki a szükséges célsebességet a biztonságos követéshez
                safe_distance = max(0.0, gap - self.margin - me.vel * self.tr)
                v_target_squared = 2.0 * me.a_brake * safe_distance
                v_target = (v_target_squared ** 0.5) if v_target_squared > 0 else 0.0
                return min(vlim, v_target)
        # AI: ha nagy a mozgástér, proaktívan közelít vlim-hez (simább profil)
        return min(vlim, me.vel + 0.5*me.a_max)
