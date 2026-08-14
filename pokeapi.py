import io
import httpx
import random
import asyncio
import copy
from typing import Dict, Any, Optional, List
from regions import get_region_info
from iv_ev_system import generate_ivs, get_random_nature

# Common moves dictionary
MOVES_DATABASE: Dict[str, Dict[str, Any]] = {
    "Tackle": {"name": "Tackle", "type": "Normal", "power": 40, "emoji": "💥"},
    "Scratch": {"name": "Scratch", "type": "Normal", "power": 40, "emoji": "🐾"},
    "Quick Attack": {"name": "Quick Attack", "type": "Normal", "power": 40, "emoji": "⚡"},
    "Bite": {"name": "Bite", "type": "Dark", "power": 60, "emoji": "🦷"},
    "Ember": {"name": "Ember", "type": "Fire", "power": 40, "emoji": "🔥"},
    "Flamethrower": {"name": "Flamethrower", "type": "Fire", "power": 90, "emoji": "🔥"},
    "Water Gun": {"name": "Water Gun", "type": "Water", "power": 40, "emoji": "💧"},
    "Hydro Pump": {"name": "Hydro Pump", "type": "Water", "power": 110, "emoji": "🌊"},
    "Vine Whip": {"name": "Vine Whip", "type": "Grass", "power": 45, "emoji": "🍃"},
    "Razor Leaf": {"name": "Razor Leaf", "type": "Grass", "power": 55, "emoji": "🍃"},
    "Thunder Shock": {"name": "Thunder Shock", "type": "Electric", "power": 40, "emoji": "⚡"},
    "Thunderbolt": {"name": "Thunderbolt", "type": "Electric", "power": 90, "emoji": "⚡"},
    "Confusion": {"name": "Confusion", "type": "Psychic", "power": 50, "emoji": "🔮"},
    "Ice Beam": {"name": "Ice Beam", "type": "Ice", "power": 90, "emoji": "❄️"},
    "Dragon Claw": {"name": "Dragon Claw", "type": "Dragon", "power": 80, "emoji": "🐲"},
}

STARTERS_DATA: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1,
        "name": "Bulbasaur",
        "types": ["Grass", "Poison"],
        "emoji": "🍃",
        "description": "For some time after its birth, it uses the nutrients that are packed into the seed on its back to grow.",
        "stats": {"hp": 45, "attack": 49, "defense": 49, "special-attack": 65, "special-defense": 65, "speed": 45},
        "ev_yields": {"Special Attack": 1},
        "capture_rate": 45,
        "rarity": "Starter",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png"
    },
    4: {
        "id": 4,
        "name": "Charmander",
        "types": ["Fire"],
        "emoji": "🔥",
        "description": "The flame on its tail shows the strength of its life force. If Charmander is weak, the flame also burns weakly.",
        "stats": {"hp": 39, "attack": 52, "defense": 43, "special-attack": 60, "special-defense": 50, "speed": 65},
        "ev_yields": {"Speed": 1},
        "capture_rate": 45,
        "rarity": "Starter",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png"
    },
    7: {
        "id": 7,
        "name": "Squirtle",
        "types": ["Water"],
        "emoji": "💧",
        "description": "After birth, its back swells and hardens into a shell. Powerfully sprays foam from its mouth.",
        "stats": {"hp": 44, "attack": 48, "defense": 65, "special-attack": 50, "special-defense": 64, "speed": 43},
        "ev_yields": {"Defense": 1},
        "capture_rate": 45,
        "rarity": "Starter",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png"
    }
}

# Global RAM cache for fetched Pokémon data (id -> dict)
_POKEMON_CACHE: Dict[int, Dict[str, Any]] = {}
_SHARED_CLIENT: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    global _SHARED_CLIENT
    if _SHARED_CLIENT is None or _SHARED_CLIENT.is_closed:
        _SHARED_CLIENT = httpx.AsyncClient(timeout=4.0, limits=httpx.Limits(max_keepalive_connections=20, max_connections=30))
    return _SHARED_CLIENT


def get_pokemon_moves(types: List[str]) -> List[Dict[str, Any]]:
    """Generate 4 suitable battle moves based on Pokémon types."""
    moves = [MOVES_DATABASE["Tackle"], MOVES_DATABASE["Quick Attack"]]
    
    if "Fire" in types:
        moves.append(MOVES_DATABASE["Ember"])
        moves.append(MOVES_DATABASE["Flamethrower"])
    elif "Water" in types:
        moves.append(MOVES_DATABASE["Water Gun"])
        moves.append(MOVES_DATABASE["Hydro Pump"])
    elif "Grass" in types:
        moves.append(MOVES_DATABASE["Vine Whip"])
        moves.append(MOVES_DATABASE["Razor Leaf"])
    elif "Electric" in types:
        moves.append(MOVES_DATABASE["Thunder Shock"])
        moves.append(MOVES_DATABASE["Thunderbolt"])
    elif "Psychic" in types:
        moves.append(MOVES_DATABASE["Confusion"])
        moves.append(MOVES_DATABASE["Bite"])
    else:
        moves.append(MOVES_DATABASE["Scratch"])
        moves.append(MOVES_DATABASE["Bite"])

    return moves[:4]


async def fetch_pokemon_data(pokemon_id: int) -> Dict[str, Any]:
    """Fetch Pokémon data with RAM caching and parallel HTTP request execution."""
    if pokemon_id in _POKEMON_CACHE:
        res_data = copy.deepcopy(_POKEMON_CACHE[pokemon_id])
        res_data["nature"] = get_random_nature()
        return res_data

    if pokemon_id in STARTERS_DATA:
        sdata = copy.deepcopy(STARTERS_DATA[pokemon_id])
        sdata["moves"] = get_pokemon_moves(sdata["types"])
        sdata["nature"] = get_random_nature()
        _POKEMON_CACHE[pokemon_id] = sdata
        return sdata

    client = _get_client()
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}"

    try:
        res, s_res = await asyncio.gather(
            client.get(url),
            client.get(species_url),
            return_exceptions=True
        )

        if isinstance(res, httpx.Response) and res.status_code == 200:
            data = res.json()
            stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
            types = [t["type"]["name"].capitalize() for t in data["types"]]
            
            ev_yields = {}
            for stat in data["stats"]:
                effort = stat.get("effort", 0)
                if effort > 0:
                    sname = stat["stat"]["name"].replace("-", " ").title()
                    ev_yields[sname] = effort

            image_url = (
                data["sprites"]["other"]["official-artwork"]["front_default"]
                or f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png"
            )
            
            is_legendary = False
            is_mythical = False
            capture_rate = 120

            if isinstance(s_res, httpx.Response) and s_res.status_code == 200:
                s_data = s_res.json()
                is_legendary = s_data.get("is_legendary", False)
                is_mythical = s_data.get("is_mythical", False)
                capture_rate = s_data.get("capture_rate", 120)

            if is_legendary or is_mythical:
                rarity = "Legendary"
            elif capture_rate <= 45:
                rarity = "Rare"
            elif capture_rate <= 120:
                rarity = "Uncommon"
            else:
                rarity = "Common"

            emoji = "⚡"
            if "Fire" in types: emoji = "🔥"
            elif "Water" in types: emoji = "💧"
            elif "Grass" in types: emoji = "🍃"
            elif "Electric" in types: emoji = "⚡"
            elif "Psychic" in types: emoji = "🔮"

            fetched = {
                "id": pokemon_id,
                "name": data["name"].capitalize(),
                "types": types,
                "emoji": emoji,
                "description": f"Wild {data['name'].capitalize()} encountered in the wild!",
                "stats": stats,
                "ev_yields": ev_yields or {"HP": 1},
                "capture_rate": capture_rate,
                "rarity": rarity,
                "is_legendary": is_legendary or is_mythical,
                "moves": get_pokemon_moves(types),
                "image_url": image_url
            }

            _POKEMON_CACHE[pokemon_id] = fetched

            res_data = copy.deepcopy(fetched)
            res_data["nature"] = get_random_nature()
            return res_data
    except Exception:
        pass

    fallback = {
        "id": pokemon_id,
        "name": f"Pokedex-{pokemon_id}",
        "types": ["Normal"],
        "emoji": "🐾",
        "description": f"Wild Pokedex #{pokemon_id} encountered!",
        "stats": {"hp": 45, "attack": 45, "defense": 45, "special-attack": 45, "special-defense": 45, "speed": 45},
        "ev_yields": {"Exp": 1},
        "capture_rate": 120,
        "rarity": "Common",
        "nature": get_random_nature(),
        "is_legendary": False,
        "moves": get_pokemon_moves(["Normal"]),
        "image_url": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png"
    }
    return fallback


async def fetch_random_wild_pokemon(region_name: str) -> Dict[str, Any]:
    """Fetch a random wild Pokémon native to the specified region."""
    region_info = get_region_info(region_name)
    min_dex, max_dex = region_info["dex_range"]

    wild_dex = random.randint(min_dex, max_dex)
    pokemon_data = await fetch_pokemon_data(wild_dex)

    rarity = pokemon_data.get("rarity", "Common")
    pokemon_data["ivs"] = generate_ivs(rarity)
    pokemon_data["nature"] = get_random_nature()
    pokemon_data["region"] = region_name
    pokemon_data["wild_level"] = random.randint(2, 12)

    return pokemon_data


def get_starter_info(pokemon_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve static starter info immediately."""
    sinfo = STARTERS_DATA.get(pokemon_id)
    if sinfo:
        sinfo["ivs"] = generate_ivs("Rare")
        sinfo["nature"] = get_random_nature()
    return sinfo
