import math
import random
from typing import Dict, Any, Tuple, List

# Pokéball multipliers based on main series games
BALL_MULTIPLIERS = {
    "pokeball": 1.0,
    "greatball": 1.5,
    "ultraball": 2.0,
    "masterball": 255.0
}

BALL_NAMES = {
    "pokeball": "Poké Ball",
    "greatball": "Great Ball",
    "ultraball": "Ultra Ball",
    "masterball": "Master Ball"
}

# Official 18-Type Effectiveness Matrix
TYPE_CHART: Dict[str, Dict[str, float]] = {
    "Normal":   {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
    "Fire":     {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
    "Water":    {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5},
    "Grass":    {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Dragon": 0.5, "Steel": 0.5},
    "Electric": {"Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0, "Flying": 2.0, "Dragon": 0.5},
    "Ice":      {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
    "Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0, "Dark": 2.0, "Steel": 2.0, "Fairy": 0.5},
    "Poison":   {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0, "Fairy": 2.0},
    "Ground":   {"Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Poison": 2.0, "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
    "Flying":   {"Electric": 0.5, "Grass": 2.0, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5, "Steel": 0.5},
    "Psychic":  {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0.0, "Steel": 0.5},
    "Bug":      {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Dark": 2.0, "Steel": 0.5, "Fairy": 0.5},
    "Rock":     {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
    "Ghost":    {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5},
    "Dragon":   {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
    "Dark":     {"Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5, "Fairy": 0.5},
    "Steel":    {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0},
    "Fairy":    {"Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Dark": 2.0, "Steel": 0.5}
}


def get_type_effectiveness(move_type: str, defender_types: List[str]) -> Tuple[float, str]:
    """
    Calculates total type multiplier against defender's types and returns battle feedback.
    Returns: (multiplier, effectiveness_text)
    """
    multiplier = 1.0
    move_chart = TYPE_CHART.get(move_type, {})

    for dtype in defender_types:
        mult = move_chart.get(dtype, 1.0)
        multiplier *= mult

    if multiplier >= 4.0:
        eff_text = "💥 It's super effective! (4x)"
    elif multiplier >= 2.0:
        eff_text = "⚡ It's super effective!"
    elif multiplier == 0.0:
        eff_text = "🛡️ It had no effect..."
    elif multiplier <= 0.25:
        eff_text = "🛡️ It's not very effective... (0.25x)"
    elif multiplier <= 0.5:
        eff_text = "🛡️ It's not very effective..."
    else:
        eff_text = ""

    return multiplier, eff_text


def get_move_effectiveness_badge(move_type: str, defender_types: List[str]) -> str:
    """Returns a short tag to display on move selection buttons during battle."""
    mult, _ = get_type_effectiveness(move_type, defender_types)
    if mult >= 2.0:
        return "🔥 2x"
    elif mult == 0.0:
        return "🚫 0x"
    elif mult <= 0.5:
        return "🛡️ 0.5x"
    return ""


def calculate_damage(
    attacker_level: int,
    move_power: int,
    attack_stat: int,
    defense_stat: int,
    type_multiplier: float = 1.0
) -> int:
    """Calculates move damage using authentic simplified Pokémon formula including Type Effectiveness."""
    if move_power <= 0 or type_multiplier <= 0.0:
        return 0

    level_factor = (2 * attacker_level / 5) + 2
    base_damage = (level_factor * move_power * (attack_stat / max(1, defense_stat))) / 50 + 2
    variation = random.uniform(0.85, 1.0)
    damage = math.floor(base_damage * variation * type_multiplier)
    return max(1, damage)


def calculate_catch_success(
    max_hp: int,
    current_hp: int,
    base_catch_rate: int = 120,
    ball_type: str = "pokeball"
) -> Tuple[bool, float]:
    """Calculates catch probability using authentic Gen 3/4 4-shake formula."""
    multiplier = BALL_MULTIPLIERS.get(ball_type, 1.0)
    if ball_type == "masterball":
        return True, 100.0

    hp_factor = (3 * max_hp - 2 * current_hp) / max(1, 3 * max_hp)
    a = max(1.0, hp_factor * base_catch_rate * multiplier)

    if a >= 255.0:
        return True, 100.0

    b = math.floor(65535 * ((a / 255.0) ** 0.25))

    # Calculate overall probability
    p_single_shake = min(1.0, (b + 1) / 65536.0)
    catch_prob = (p_single_shake ** 4) * 100.0

    # 4 shake checks
    shakes_passed = 0
    for _ in range(4):
        rand_val = random.randint(0, 65535)
        if rand_val <= b:
            shakes_passed += 1
        else:
            break

    success = (shakes_passed == 4)
    return success, round(catch_prob, 1)
