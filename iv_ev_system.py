import random
import math
from typing import Dict, Any, Optional

# 25 Pokémon Natures mapping (Increased Stat (+10%), Decreased Stat (-10%))
POKEMON_NATURES: Dict[str, Dict[str, Optional[str]]] = {
    "Adamant": {"plus": "attack", "minus": "sp_attack", "desc": "+10% Atk, -10% Sp.Atk"},
    "Brave": {"plus": "attack", "minus": "speed", "desc": "+10% Atk, -10% Speed"},
    "Naughty": {"plus": "attack", "minus": "sp_defense", "desc": "+10% Atk, -10% Sp.Def"},
    "Lonely": {"plus": "attack", "minus": "defense", "desc": "+10% Atk, -10% Def"},
    "Bold": {"plus": "defense", "minus": "attack", "desc": "+10% Def, -10% Atk"},
    "Impish": {"plus": "defense", "minus": "sp_attack", "desc": "+10% Def, -10% Sp.Atk"},
    "Lax": {"plus": "defense", "minus": "sp_defense", "desc": "+10% Def, -10% Sp.Def"},
    "Relaxed": {"plus": "defense", "minus": "speed", "desc": "+10% Def, -10% Speed"},
    "Modest": {"plus": "sp_attack", "minus": "attack", "desc": "+10% Sp.Atk, -10% Atk"},
    "Mild": {"plus": "sp_attack", "minus": "defense", "desc": "+10% Sp.Atk, -10% Def"},
    "Rash": {"plus": "sp_attack", "minus": "sp_defense", "desc": "+10% Sp.Atk, -10% Sp.Def"},
    "Quiet": {"plus": "sp_attack", "minus": "speed", "desc": "+10% Sp.Atk, -10% Speed"},
    "Calm": {"plus": "sp_defense", "minus": "attack", "desc": "+10% Sp.Def, -10% Atk"},
    "Gentle": {"plus": "sp_defense", "minus": "defense", "desc": "+10% Sp.Def, -10% Def"},
    "Careful": {"plus": "sp_defense", "minus": "sp_attack", "desc": "+10% Sp.Def, -10% Sp.Atk"},
    "Sassy": {"plus": "sp_defense", "minus": "speed", "desc": "+10% Sp.Def, -10% Speed"},
    "Jolly": {"plus": "speed", "minus": "sp_attack", "desc": "+10% Speed, -10% Sp.Atk"},
    "Timid": {"plus": "speed", "minus": "attack", "desc": "+10% Speed, -10% Atk"},
    "Hasty": {"plus": "speed", "minus": "defense", "desc": "+10% Speed, -10% Def"},
    "Naive": {"plus": "speed", "minus": "sp_defense", "desc": "+10% Speed, -10% Sp.Def"},
    "Hardy": {"plus": None, "minus": None, "desc": "Neutral (No stat change)"},
    "Docile": {"plus": None, "minus": None, "desc": "Neutral (No stat change)"},
    "Serious": {"plus": None, "minus": None, "desc": "Neutral (No stat change)"},
    "Bashful": {"plus": None, "minus": None, "desc": "Neutral (No stat change)"},
    "Quirky": {"plus": None, "minus": None, "desc": "Neutral (No stat change)"},
}


def get_random_nature() -> str:
    """Roll a random Nature out of the 25 Pokémon Natures."""
    return random.choice(list(POKEMON_NATURES.keys()))


def get_nature_info(nature_name: str) -> Dict[str, Any]:
    """Retrieve Nature details and description."""
    return POKEMON_NATURES.get(nature_name, POKEMON_NATURES["Hardy"])


def generate_ivs(rarity: str = "Common") -> Dict[str, Any]:
    """
    Generates 6 IV stats (0 to 31) based on rarity tier.
    - Common / Uncommon: Completely random 0..31.
    - Rare (8% spawn rate): Guaranteed min 12+ per stat, with at least 1 stat guaranteed to be 31!
    - Legendary (2% spawn rate): Guaranteed min 20+ per stat, with at least 3 stats guaranteed to be 31!
    """
    stats_keys = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]

    if rarity == "Legendary":
        ivs = {k: random.randint(20, 31) for k in stats_keys}
        perfect_stats = random.sample(stats_keys, k=3)
        for k in perfect_stats:
            ivs[k] = 31
    elif rarity == "Rare":
        ivs = {k: random.randint(12, 31) for k in stats_keys}
        perfect_stat = random.choice(stats_keys)
        ivs[perfect_stat] = 31
    elif rarity == "Uncommon":
        ivs = {k: random.randint(5, 31) for k in stats_keys}
    else:
        ivs = {k: random.randint(0, 31) for k in stats_keys}

    iv_sum = sum(ivs[k] for k in stats_keys)
    total_pct = round((iv_sum / 186.0) * 100.0, 1)

    ivs["sum"] = iv_sum
    ivs["total_pct"] = total_pct
    ivs["grade"] = get_iv_grade(total_pct)

    return ivs


def get_iv_grade(total_pct: float) -> str:
    """Returns human-readable IV rating."""
    if total_pct >= 100.0:
        return "🌟 Perfect 100%"
    elif total_pct >= 90.0:
        return "🔥 Outstanding"
    elif total_pct >= 80.0:
        return "✨ Excellent"
    elif total_pct >= 65.0:
        return "👍 Above Average"
    elif total_pct >= 50.0:
        return "📊 Average"
    else:
        return "🌧️ Below Average"


def calculate_effective_stats(
    base_stats: Dict[str, int],
    level: int,
    ivs: Dict[str, int],
    evs: Dict[str, int],
    nature: str = "Hardy"
) -> Dict[str, int]:
    """
    Calculates final effective stats incorporating level, IVs, EVs, and Nature multiplier (+10% / -10%):
    HP = floor(((2 * Base + IV + floor(EV/4)) * Level) / 100) + Level + 10
    Stat = floor( (floor(((2 * Base + IV + floor(EV/4)) * Level) / 100) + 5) * Nature_Multiplier )
    """
    effective = {}
    nature_info = get_nature_info(nature)

    # HP is unaffected by Nature
    base_hp = base_stats.get("hp", 45)
    iv_hp = ivs.get("hp", 15)
    ev_hp = evs.get("hp", 0)
    effective["hp"] = math.floor(((2 * base_hp + iv_hp + math.floor(ev_hp / 4)) * level) / 100) + level + 10

    # Other 5 stats
    for stat in ["attack", "defense", "special-attack", "special-defense", "speed"]:
        short_key = "sp_attack" if stat == "special-attack" else ("sp_defense" if stat == "special-defense" else stat)
        base_val = base_stats.get(stat, base_stats.get(short_key, 45))
        iv_val = ivs.get(short_key, 15)
        ev_val = evs.get(short_key, 0)
        
        stat_base = math.floor(((2 * base_val + iv_val + math.floor(ev_val / 4)) * level) / 100) + 5
        
        # Apply Nature multiplier (+10% / -10%)
        multiplier = 1.0
        if nature_info["plus"] == short_key:
            multiplier = 1.1
        elif nature_info["minus"] == short_key:
            multiplier = 0.9

        effective[short_key] = math.floor(stat_base * multiplier)

    return effective
