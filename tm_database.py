"""
Complete Official Pokémon TM Database (TM01 - TM100)
Contains move names, elemental types, power, accuracy, and official sprite URLs.
"""
from typing import Dict, Any

TM_DATABASE: Dict[str, Dict[str, Any]] = {
    "TM01": {"name": "TM01 Work Up", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Raises Attack and Sp. Atk by 1 stage."},
    "TM02": {"name": "TM02 Dragon Claw", "type": "Dragon", "power": 80, "accuracy": 100, "desc": "Slashes the target with huge sharp claws."},
    "TM03": {"name": "TM03 Psyshock", "type": "Psychic", "power": 80, "accuracy": 100, "desc": "Materializes odd psychic waves to deal damage."},
    "TM04": {"name": "TM04 Calm Mind", "type": "Psychic", "power": 0, "accuracy": 100, "desc": "Raises Sp. Atk and Sp. Def by 1 stage."},
    "TM05": {"name": "TM05 Roar", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Scares away wild Pokémon or switches foe."},
    "TM06": {"name": "TM06 Toxic", "type": "Poison", "power": 0, "accuracy": 90, "desc": "Badly poisons the target with worsening damage."},
    "TM07": {"name": "TM07 Hail", "type": "Ice", "power": 0, "accuracy": 100, "desc": "Summons a hailstorm for 5 turns."},
    "TM08": {"name": "TM08 Bulk Up", "type": "Fighting", "power": 0, "accuracy": 100, "desc": "Raises Attack and Defense by 1 stage."},
    "TM09": {"name": "TM09 Venoshock", "type": "Poison", "power": 65, "accuracy": 100, "desc": "Double damage if target is poisoned."},
    "TM10": {"name": "TM10 Hidden Power", "type": "Normal", "power": 60, "accuracy": 100, "desc": "A unique attack that varies in type."},
    "TM11": {"name": "TM11 Sunny Day", "type": "Fire", "power": 0, "accuracy": 100, "desc": "Intensifies the sun for 5 turns."},
    "TM12": {"name": "TM12 Taunt", "type": "Dark", "power": 0, "accuracy": 100, "desc": "Forces foe to only use attack moves."},
    "TM13": {"name": "TM13 Ice Beam", "type": "Ice", "power": 90, "accuracy": 100, "desc": "Freezing beam of ice. May freeze target."},
    "TM14": {"name": "TM14 Blizzard", "type": "Ice", "power": 110, "accuracy": 70, "desc": "Summons a howling blizzard. May freeze target."},
    "TM15": {"name": "TM15 Hyper Beam", "type": "Normal", "power": 150, "accuracy": 90, "desc": "Destructive beam requiring a turn to recharge."},
    "TM16": {"name": "TM16 Light Screen", "type": "Psychic", "power": 0, "accuracy": 100, "desc": "Reduces special damage for 5 turns."},
    "TM17": {"name": "TM17 Protect", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Evades all attacks for the turn."},
    "TM18": {"name": "TM18 Rain Dance", "type": "Water", "power": 0, "accuracy": 100, "desc": "Summons heavy rain for 5 turns."},
    "TM19": {"name": "TM19 Roost", "type": "Flying", "power": 0, "accuracy": 100, "desc": "Restores up to 50% max HP."},
    "TM20": {"name": "TM20 Safeguard", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Prevents status conditions for 5 turns."},
    "TM21": {"name": "TM21 Frustration", "type": "Normal", "power": 70, "accuracy": 100, "desc": "More powerful if user dislikes trainer."},
    "TM22": {"name": "TM22 Solar Beam", "type": "Grass", "power": 120, "accuracy": 100, "desc": "Absorbs light then fires a concentrated beam."},
    "TM23": {"name": "TM23 Smack Down", "type": "Rock", "power": 50, "accuracy": 100, "desc": "Knocks flying targets down to ground."},
    "TM24": {"name": "TM24 Thunderbolt", "type": "Electric", "power": 90, "accuracy": 100, "desc": "A strong electric blast. May paralyze target."},
    "TM25": {"name": "TM25 Thunder", "type": "Electric", "power": 110, "accuracy": 70, "desc": "A wicked lightning bolt. May paralyze target."},
    "TM26": {"name": "TM26 Earthquake", "type": "Ground", "power": 100, "accuracy": 100, "desc": "A powerful ground-shaking earthquake."},
    "TM27": {"name": "TM27 Return", "type": "Normal", "power": 70, "accuracy": 100, "desc": "More powerful if user likes trainer."},
    "TM28": {"name": "TM28 Leech Life", "type": "Bug", "power": 80, "accuracy": 100, "desc": "Drains HP to heal user by half damage dealt."},
    "TM29": {"name": "TM29 Psychic", "type": "Psychic", "power": 90, "accuracy": 100, "desc": "Strong telekinetic attack. May lower Sp. Def."},
    "TM30": {"name": "TM30 Shadow Ball", "type": "Ghost", "power": 80, "accuracy": 100, "desc": "Hurls a shadowy blob. May lower Sp. Def."},
    "TM31": {"name": "TM31 Brick Break", "type": "Fighting", "power": 75, "accuracy": 100, "desc": "Breaks light screen & reflect barriers."},
    "TM32": {"name": "TM32 Double Team", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Creates illusion copies to boost evasiveness."},
    "TM33": {"name": "TM33 Reflect", "type": "Psychic", "power": 0, "accuracy": 100, "desc": "Reduces physical damage for 5 turns."},
    "TM34": {"name": "TM34 Sludge Wave", "type": "Poison", "power": 95, "accuracy": 100, "desc": "Swamps the area with sludge. May poison foe."},
    "TM35": {"name": "TM35 Flamethrower", "type": "Fire", "power": 90, "accuracy": 100, "desc": "Scorching blast of fire. May burn target."},
    "TM36": {"name": "TM36 Sludge Bomb", "type": "Poison", "power": 90, "accuracy": 100, "desc": "Unsanitary sludge attack. May poison target."},
    "TM37": {"name": "TM37 Sandstorm", "type": "Rock", "power": 0, "accuracy": 100, "desc": "Summons a sandstorm for 5 turns."},
    "TM38": {"name": "TM38 Fire Blast", "type": "Fire", "power": 110, "accuracy": 85, "desc": "Intense blast of fire. May burn target."},
    "TM39": {"name": "TM39 Rock Tomb", "type": "Rock", "power": 60, "accuracy": 95, "desc": "Boulders hurl down to lower Speed."},
    "TM40": {"name": "TM40 Aerial Ace", "type": "Flying", "power": 60, "accuracy": 100, "desc": "Extremely fast speed attack that never misses."},
    "TM41": {"name": "TM41 Torment", "type": "Dark", "power": 0, "accuracy": 100, "desc": "Prevents target from using same move twice."},
    "TM42": {"name": "TM42 Facade", "type": "Normal", "power": 70, "accuracy": 100, "desc": "Double damage if user is burned/poisoned/paralyzed."},
    "TM43": {"name": "TM43 Flame Charge", "type": "Fire", "power": 50, "accuracy": 100, "desc": "Cloaked in flame to attack and boost Speed."},
    "TM44": {"name": "TM44 Rest", "type": "Psychic", "power": 0, "accuracy": 100, "desc": "User sleeps 2 turns to fully heal HP & status."},
    "TM45": {"name": "TM45 Attract", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Makes opposite gender target infatuated."},
    "TM46": {"name": "TM46 Thief", "type": "Dark", "power": 60, "accuracy": 100, "desc": "Attacks and steals held item."},
    "TM47": {"name": "TM47 Low Sweep", "type": "Fighting", "power": 65, "accuracy": 100, "desc": "Quick kick to lower target's Speed."},
    "TM48": {"name": "TM48 Round", "type": "Normal", "power": 60, "accuracy": 100, "desc": "Chorused song that increases damage with allies."},
    "TM49": {"name": "TM49 Echoed Voice", "type": "Normal", "power": 40, "accuracy": 100, "desc": "Increases power every consecutive turn used."},
    "TM50": {"name": "TM50 Overheat", "type": "Fire", "power": 130, "accuracy": 90, "desc": "Tremendous fire power that lowers user Sp. Atk."},
    "TM51": {"name": "TM51 Steel Wing", "type": "Steel", "power": 70, "accuracy": 90, "desc": "Hard wing strike. May boost user Defense."},
    "TM52": {"name": "TM52 Focus Blast", "type": "Fighting", "power": 120, "accuracy": 70, "desc": "Heightened power mental aura sphere."},
    "TM53": {"name": "TM53 Energy Ball", "type": "Grass", "power": 90, "accuracy": 100, "desc": "Draws power from nature. May lower Sp. Def."},
    "TM54": {"name": "TM54 False Swipe", "type": "Normal", "power": 40, "accuracy": 100, "desc": "Restrained attack that leaves target at 1 HP."},
    "TM55": {"name": "TM55 Scald", "type": "Water", "power": 80, "accuracy": 100, "desc": "Boiling hot water strike. May burn target."},
    "TM56": {"name": "TM56 Fling", "type": "Dark", "power": 50, "accuracy": 100, "desc": "Flings held item at foe."},
    "TM57": {"name": "TM57 Charge Beam", "type": "Electric", "power": 50, "accuracy": 90, "desc": "Fires electric beam. High chance to raise Sp. Atk."},
    "TM58": {"name": "TM58 Sky Drop", "type": "Flying", "power": 60, "accuracy": 100, "desc": "Takes target into sky and drops them next turn."},
    "TM59": {"name": "TM59 Brutal Swing", "type": "Dark", "power": 60, "accuracy": 100, "desc": "Swings body around to strike all nearby."},
    "TM60": {"name": "TM60 Quash", "type": "Dark", "power": 0, "accuracy": 100, "desc": "Forces target to act last in turn order."},
    "TM61": {"name": "TM61 Will-O-Wisp", "type": "Fire", "power": 0, "accuracy": 85, "desc": "Shoots sinister blue flame to burn target."},
    "TM62": {"name": "TM62 Acrobatics", "type": "Flying", "power": 55, "accuracy": 100, "desc": "Double damage if user holds no item."},
    "TM63": {"name": "TM63 Embargo", "type": "Dark", "power": 0, "accuracy": 100, "desc": "Prevents target from using items for 5 turns."},
    "TM64": {"name": "TM64 Explosion", "type": "Normal", "power": 250, "accuracy": 100, "desc": "Cataclysmic explosion causing user to faint."},
    "TM65": {"name": "TM65 Shadow Claw", "type": "Ghost", "power": 70, "accuracy": 100, "desc": "Claws woven from shadow. High critical ratio."},
    "TM66": {"name": "TM66 Payback", "type": "Dark", "power": 50, "accuracy": 100, "desc": "Double damage if user moves after target."},
    "TM67": {"name": "TM67 Smart Strike", "type": "Steel", "power": 70, "accuracy": 100, "desc": "Stabs with sharp horn or blade. Never misses."},
    "TM68": {"name": "TM68 Giga Impact", "type": "Normal", "power": 150, "accuracy": 90, "desc": "Brutal charge requiring a turn to recharge."},
    "TM69": {"name": "TM69 Rock Polish", "type": "Rock", "power": 0, "accuracy": 100, "desc": "Polishes body to sharply boost Speed."},
    "TM70": {"name": "TM70 Aurora Veil", "type": "Ice", "power": 0, "accuracy": 100, "desc": "Reduces incoming damage in Hail for 5 turns."},
    "TM71": {"name": "TM71 Stone Edge", "type": "Rock", "power": 100, "accuracy": 80, "desc": "Stabs from below with stone. High critical ratio."},
    "TM72": {"name": "TM72 Volt Switch", "type": "Electric", "power": 70, "accuracy": 100, "desc": "Attacks and switches out immediately."},
    "TM73": {"name": "TM73 Thunder Wave", "type": "Electric", "power": 0, "accuracy": 90, "desc": "Weak jolt of electricity that paralyzes foe."},
    "TM74": {"name": "TM74 Gyro Ball", "type": "Steel", "power": 65, "accuracy": 100, "desc": "Faster foe increases move power."},
    "TM75": {"name": "TM75 Swords Dance", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Frenzied dance that sharply boosts Attack."},
    "TM76": {"name": "TM76 Fly", "type": "Flying", "power": 90, "accuracy": 95, "desc": "Soars into sky on turn 1, strikes on turn 2."},
    "TM77": {"name": "TM77 Psych Up", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Copies target's stat changes."},
    "TM78": {"name": "TM78 Bulldoze", "type": "Ground", "power": 60, "accuracy": 100, "desc": "Stomps ground to lower all targets' Speed."},
    "TM79": {"name": "TM79 Frost Breath", "type": "Ice", "power": 60, "accuracy": 90, "desc": "Cold breath blast that always lands critical hit."},
    "TM80": {"name": "TM80 Rock Slide", "type": "Rock", "power": 75, "accuracy": 90, "desc": "Hurls boulders at foe. May cause flinch."},
    "TM81": {"name": "TM81 X-Scissor", "type": "Bug", "power": 80, "accuracy": 100, "desc": "Slashes target with scythes or claws."},
    "TM82": {"name": "TM82 Dragon Tail", "type": "Dragon", "power": 60, "accuracy": 90, "desc": "Knocks target away and forces a switch out."},
    "TM83": {"name": "TM83 Infestation", "type": "Bug", "power": 20, "accuracy": 100, "desc": "Traps target in bug swarm for 4-5 turns."},
    "TM84": {"name": "TM84 Poison Jab", "type": "Poison", "power": 80, "accuracy": 100, "desc": "Jabs with a poisoned arm or tentacle."},
    "TM85": {"name": "TM85 Dream Eater", "type": "Psychic", "power": 100, "accuracy": 100, "desc": "Eats sleeping target's dream to heal user."},
    "TM86": {"name": "TM86 Grass Knot", "type": "Grass", "power": 60, "accuracy": 100, "desc": "Trips target with grass. Heavier foes take more damage."},
    "TM87": {"name": "TM87 Swagger", "type": "Normal", "power": 0, "accuracy": 85, "desc": "Enrages target into confusion & boosts Attack."},
    "TM88": {"name": "TM88 Sleep Talk", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Uses a random known move while sleeping."},
    "TM89": {"name": "TM89 U-turn", "type": "Bug", "power": 70, "accuracy": 100, "desc": "Attacks and switches out immediately."},
    "TM90": {"name": "TM90 Substitute", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Creates decoy using 25% max HP."},
    "TM91": {"name": "TM91 Flash Cannon", "type": "Steel", "power": 90, "accuracy": 100, "desc": "Fires light energy beam. May lower Sp. Def."},
    "TM92": {"name": "TM92 Trick Room", "type": "Psychic", "power": 0, "accuracy": 100, "desc": "Reverses turn order for 5 turns so slower acts first."},
    "TM93": {"name": "TM93 Wild Charge", "type": "Electric", "power": 90, "accuracy": 100, "desc": "Electrified tackle that deals recoil damage."},
    "TM94": {"name": "TM94 Surf", "type": "Water", "power": 90, "accuracy": 100, "desc": "Swamps entire battlefield in a huge wave."},
    "TM95": {"name": "TM95 Snarl", "type": "Dark", "power": 55, "accuracy": 95, "desc": "Yells continuously to lower target's Sp. Atk."},
    "TM96": {"name": "TM96 Nature Power", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Adapts into a move based on current terrain."},
    "TM97": {"name": "TM97 Dark Pulse", "type": "Dark", "power": 80, "accuracy": 100, "desc": "Horrible aura of dark thoughts. May cause flinch."},
    "TM98": {"name": "TM98 Waterfall", "type": "Water", "power": 80, "accuracy": 100, "desc": "Charges with waterfall force. May cause flinch."},
    "TM99": {"name": "TM99 Dazzling Gleam", "type": "Fairy", "power": 80, "accuracy": 100, "desc": "Dazzles all foes with powerful flash of light."},
    "TM100": {"name": "TM100 Confide", "type": "Normal", "power": 0, "accuracy": 100, "desc": "Tells secret to target to lower Sp. Atk."}
}


def get_tm_info(tm_id: str) -> Dict[str, Any]:
    """Retrieve full metadata for any TM from TM01 to TM100."""
    tm_key = tm_id.upper()
    if tm_key in TM_DATABASE:
        return TM_DATABASE[tm_key]
    
    # Dynamic fallback for any unlisted TM
    return {
        "name": f"{tm_key} Machine",
        "type": "Normal",
        "power": 80,
        "accuracy": 100,
        "desc": "A technical machine for learning a move."
    }


def get_tm_sprite_url(tm_id: str) -> str:
    """Returns official PokeAPI item sprite URL based on TM move type."""
    info = get_tm_info(tm_id)
    t_type = info["type"].lower()
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/tm-{t_type}.png"
