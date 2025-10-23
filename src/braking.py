"""
Realisztikus vasúti fékezési mechanika
Magyar vasúti szabályozás (D.54) és UIC szabványok alapján

Fékszázalék = (Fékezett tömeg / Teljes tömeg) × 100

Alapfogalmak:
- P-fékszázalék: személyvonatoknál (min. 75%)
- G-fékszázalék: tehervonatok (min. 30-60%)
- Féktávolság: v²/(2×a_eff) ahol a_eff = fékerő / tömeg
- Tapadási viszonyok: száraz/nedves/síkos sín (μ = 0.33/0.25/0.15)
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class BrakeType(Enum):
    """Fék típusok UIC szabvány szerint"""
    P = "P"  # Passenger - személyvonat (gyors fékezés)
    G = "G"  # Goods - tehervonat (lassú fékezés)
    
class RailCondition(Enum):
    """Sín állapot - tapadási viszonyok"""
    DRY = "dry"           # Száraz sín: μ = 0.33
    WET = "wet"           # Nedves sín: μ = 0.25
    SLIPPERY = "slippery" # Síkos sín (ősz, levelek): μ = 0.15
    ICY = "icy"           # Jeges sín: μ = 0.08

@dataclass
class TrainBrakingCharacteristics:
    """
    Vonat fékezési karakterisztikái valós vasúti adatok alapján
    """
    # Alapadatok
    train_type: str  # "szemely", "IC", "teher", "villamos", "dízel"
    mass_tons: float  # Vonat teljes tömege tonnában
    length_m: float   # Vonat hossza méterben
    
    # Fékrendszer
    brake_type: BrakeType  # P vagy G fék
    brake_percentage: float  # Fékszázalék (0-200)
    
    # Elektropneumatikus (EP) fék?
    has_ep_brake: bool = False
    
    # Vonat maximális sebessége
    max_speed_kmh: float = 160.0
    
    # Tapadási tényező korrekció
    adhesion_factor: float = 1.0
    
    def __post_init__(self):
        """Validáció és alapértelmezett értékek"""
        if self.brake_percentage < 0 or self.brake_percentage > 200:
            raise ValueError(f"Invalid brake percentage: {self.brake_percentage}")
        
        if self.mass_tons <= 0:
            raise ValueError(f"Invalid train mass: {self.mass_tons}")

class BrakingCalculator:
    """
    Valós vasúti fékezési számítások UIC és magyar szabályozás szerint
    """
    
    # Gravitációs gyorsulás
    G = 9.81  # m/s²
    
    # Tapadási együtthatók különböző sínállapotokhoz
    ADHESION_COEFFICIENTS = {
        RailCondition.DRY: 0.33,
        RailCondition.WET: 0.25,
        RailCondition.SLIPPERY: 0.15,
        RailCondition.ICY: 0.08
    }
    
    # EP fék reakcióidő csökkentés (másodperc)
    EP_BRAKE_TIME_REDUCTION = 1.5  # EP fék 1.5s-al gyorsabb
    
    # Alapértelmezett fékezési reakcióidők (UIC 544-1)
    BRAKE_RESPONSE_TIMES = {
        BrakeType.P: 3.5,   # P-fék: 3.5s (személyvonat)
        BrakeType.G: 8.0    # G-fék: 8.0s (tehervonat)
    }
    
    @classmethod
    def calculate_max_deceleration(
        cls,
        characteristics: TrainBrakingCharacteristics,
        rail_condition: RailCondition = RailCondition.DRY,
        gradient_promille: float = 0.0
    ) -> float:
        """
        Számítsa ki a maximális lassulást (m/s²)
        
        Képlet: a_max = (brake_percentage / 100) × μ × g × adhesion_factor + gradient_effect
        
        Args:
            characteristics: Vonat fékezési adatai
            rail_condition: Sín állapot
            gradient_promille: Pályalejtés ezrelékben (+: lejtő segít, -: emelkedő hátráltat)
            
        Returns:
            Maximális lassulás m/s²-ban
        """
        # Tapadási együttható a sín állapota alapján
        mu = cls.ADHESION_COEFFICIENTS[rail_condition]
        
        # Alapfékezés fékszázalék szerint
        # Fékszázalék 100% = teljes tapadási fékezés
        brake_ratio = characteristics.brake_percentage / 100.0
        
        # Maximális lassulás tapadási határ nélkül
        a_brake_theoretical = brake_ratio * mu * cls.G * characteristics.adhesion_factor
        
        # Tapadási határ (kerék nem csúszhat)
        # Személyvonatok: max ~1.2 m/s² (P-fék, száraz sín)
        # Tehervonatok: max ~0.6 m/s² (G-fék, száraz sín)
        a_adhesion_limit = mu * cls.G
        
        # A kisebb számít
        a_brake = min(a_brake_theoretical, a_adhesion_limit)
        
        # Pályalejtés hatása (pozitív lejtő segíti a fékezést)
        gradient_effect = (gradient_promille / 1000.0) * cls.G
        
        # Teljes lassulás
        a_total = a_brake + gradient_effect
        
        # Minimum 0.1 m/s² (valami fékezés mindig van)
        return max(0.1, a_total)
    
    @classmethod
    def calculate_braking_distance(
        cls,
        v_initial_kmh: float,
        v_final_kmh: float,
        characteristics: TrainBrakingCharacteristics,
        rail_condition: RailCondition = RailCondition.DRY,
        gradient_promille: float = 0.0,
        include_reaction_time: bool = True
    ) -> tuple[float, float]:
        """
        Számítsa ki a féktávolságot valós vasúti modell szerint
        
        Returns:
            (braking_distance_m, braking_time_s)
        """
        # Sebességek m/s-ban
        v0 = v_initial_kmh / 3.6
        vf = v_final_kmh / 3.6
        
        if v0 <= vf:
            return (0.0, 0.0)
        
        # Maximális lassulás
        a_max = cls.calculate_max_deceleration(
            characteristics, rail_condition, gradient_promille
        )
        
        # Reakcióidő (fékhatás felépülése)
        if include_reaction_time:
            t_response = cls.BRAKE_RESPONSE_TIMES[characteristics.brake_type]
            
            # EP fék gyorsabb
            if characteristics.has_ep_brake:
                t_response -= cls.EP_BRAKE_TIME_REDUCTION
            
            # Reakcióidő alatt a vonat tovább megy
            s_reaction = v0 * t_response
        else:
            t_response = 0.0
            s_reaction = 0.0
        
        # Tényleges fékezési távolság (v² = u² + 2as)
        # s = (vf² - v0²) / (2 × a)
        s_brake = (vf**2 - v0**2) / (2.0 * (-a_max))
        
        # Fékezési idő (v = u + at)
        t_brake = (vf - v0) / (-a_max)
        
        # Teljes távolság és idő
        s_total = s_reaction + s_brake
        t_total = t_response + t_brake
        
        return (s_total, t_total)
    
    @classmethod
    def calculate_service_brake_curve(
        cls,
        v_kmh: float,
        characteristics: TrainBrakingCharacteristics,
        rail_condition: RailCondition = RailCondition.DRY
    ) -> float:
        """
        Üzemi fékezés (nem vészfékezés) - finomabb szabályozás
        
        Returns:
            Ajánlott lassulás m/s² üzemi fékezéshez (60-70% max)
        """
        a_max = cls.calculate_max_deceleration(characteristics, rail_condition)
        
        # Üzemi fékezés: 60-70% a maximumból (kényelem és kopás miatt)
        service_brake_factor = 0.65
        
        # Sebességfüggő korrekció (nagy sebesség → óvatosabb)
        if v_kmh > 120:
            service_brake_factor *= 0.9
        
        return a_max * service_brake_factor
    
    @classmethod
    def calculate_emergency_brake(
        cls,
        characteristics: TrainBrakingCharacteristics,
        rail_condition: RailCondition = RailCondition.DRY
    ) -> float:
        """
        Vészfékezés - teljes fékhatás azonnal
        
        Returns:
            Vészfék lassulás m/s²
        """
        # Vészféknél a teljes fékhatás
        return cls.calculate_max_deceleration(characteristics, rail_condition)

# === ELŐRE DEFINIÁLT VONAT TÍPUSOK ===

class StandardTrainTypes:
    """Standard magyar vasúti járművek fékezési adatai"""
    
    @staticmethod
    def modern_emu() -> TrainBrakingCharacteristics:
        """Modern villamosított motorvonat (pl. FLIRT, Stadler)"""
        return TrainBrakingCharacteristics(
            train_type="EMU_modern",
            mass_tons=180.0,
            length_m=120.0,
            brake_type=BrakeType.P,
            brake_percentage=135,  # Kiváló fékezés
            has_ep_brake=True,
            max_speed_kmh=160
        )
    
    @staticmethod
    def ic_train() -> TrainBrakingCharacteristics:
        """InterCity szerelvény (IC+)"""
        return TrainBrakingCharacteristics(
            train_type="IC",
            mass_tons=450.0,
            length_m=180.0,
            brake_type=BrakeType.P,
            brake_percentage=110,
            has_ep_brake=True,
            max_speed_kmh=160
        )
    
    @staticmethod
    def regional_dmu() -> TrainBrakingCharacteristics:
        """Regionális dízel motorvonat (Bzmot)"""
        return TrainBrakingCharacteristics(
            train_type="DMU_regional",
            mass_tons=70.0,
            length_m=50.0,
            brake_type=BrakeType.P,
            brake_percentage=95,
            has_ep_brake=False,
            max_speed_kmh=100
        )
    
    @staticmethod
    def freight_train() -> TrainBrakingCharacteristics:
        """Tehervonat (átlagos)"""
        return TrainBrakingCharacteristics(
            train_type="freight",
            mass_tons=1200.0,
            length_m=450.0,
            brake_type=BrakeType.G,
            brake_percentage=65,
            has_ep_brake=False,
            max_speed_kmh=100
        )
    
    @staticmethod
    def suburban_train() -> TrainBrakingCharacteristics:
        """Elővárosi vonat"""
        return TrainBrakingCharacteristics(
            train_type="suburban",
            mass_tons=120.0,
            length_m=120.0,
            brake_type=BrakeType.P,
            brake_percentage=120,
            has_ep_brake=True,
            max_speed_kmh=120
        )

# === PÉLDA HASZNÁLAT ===

def example_braking_calculations():
    """Példa a fékezési számításokra"""
    
    print("=== MAGYAR VASÚTI FÉKEZÉSI SZÁMÍTÁSOK ===\n")
    
    # Modern EMU
    emu = StandardTrainTypes.modern_emu()
    calc = BrakingCalculator()
    
    # Különböző sínállapotok
    for condition in [RailCondition.DRY, RailCondition.WET, RailCondition.SLIPPERY]:
        a_max = calc.calculate_max_deceleration(emu, condition)
        print(f"{condition.value.upper()} sín:")
        print(f"  Max lassulás: {a_max:.3f} m/s²")
        
        # Féktávolság 160 km/h-ról állásra
        distance, time = calc.calculate_braking_distance(
            160, 0, emu, condition, include_reaction_time=True
        )
        print(f"  Féktávolság 160→0 km/h: {distance:.1f}m ({time:.1f}s)")
        
        # Féktávolság 160→40 km/h (sebességváltás)
        distance2, time2 = calc.calculate_braking_distance(
            160, 40, emu, condition, include_reaction_time=True
        )
        print(f"  Féktávolság 160→40 km/h: {distance2:.1f}m ({time2:.1f}s)")
        print()
    
    # Tehervonat összehasonlítás
    print("\n=== TEHERVONAT vs SZEMÉLYVONAT ===\n")
    
    freight = StandardTrainTypes.freight_train()
    passenger = StandardTrainTypes.ic_train()
    
    for train, name in [(freight, "Tehervonat"), (passenger, "IC vonat")]:
        a_max = calc.calculate_max_deceleration(train, RailCondition.DRY)
        distance, time = calc.calculate_braking_distance(
            100, 0, train, RailCondition.DRY
        )
        print(f"{name}:")
        print(f"  Fékszázalék: {train.brake_percentage}%")
        print(f"  Fék típus: {train.brake_type.value}")
        print(f"  Max lassulás: {a_max:.3f} m/s²")
        print(f"  Féktávolság 100→0 km/h: {distance:.1f}m ({time:.1f}s)")
        print()

if __name__ == "__main__":
    example_braking_calculations()
