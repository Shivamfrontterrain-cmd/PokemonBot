from typing import Dict, Any, Tuple

REGIONS: Dict[str, Dict[str, Any]] = {
    "Kanto": {
        "gen": 1,
        "dex_range": (1, 151),
        "req_level": 1,
        "emoji": "🏔️",
        "mascot_id": 151,
        "description": "The classic region where it all began. Famous for Pallet Town and Indigo Plateau."
    },
    "Johto": {
        "gen": 2,
        "dex_range": (152, 251),
        "req_level": 2,
        "emoji": "🌸",
        "mascot_id": 250,
        "description": "A historic region rich with tradition, bell towers, and ancient ruins."
    },
    "Hoenn": {
        "gen": 3,
        "dex_range": (252, 386),
        "req_level": 3,
        "emoji": "🌋",
        "mascot_id": 384,
        "description": "A tropical region known for its vast ocean routes, volcanoes, and weather."
    },
    "Sinnoh": {
        "gen": 4,
        "dex_range": (387, 493),
        "req_level": 4,
        "emoji": "❄️",
        "mascot_id": 493,
        "description": "A mountainous region with snowy peaks and legendary myths of time and space."
    },
    "Unova": {
        "gen": 5,
        "dex_range": (494, 649),
        "req_level": 5,
        "emoji": "🏙️",
        "mascot_id": 643,
        "description": "A modern metropolitan region far from Kanto, full of diverse ecosystems."
    },
    "Kalos": {
        "gen": 6,
        "dex_range": (650, 721),
        "req_level": 6,
        "emoji": "🏰",
        "mascot_id": 716,
        "description": "A star-shaped region renowned for fashion, mega evolution, and beauty."
    },
    "Alola": {
        "gen": 7,
        "dex_range": (722, 809),
        "req_level": 7,
        "emoji": "🏝️",
        "mascot_id": 791,
        "description": "A tropical island paradise featuring Island Trials and Z-Moves."
    },
    "Galar": {
        "gen": 8,
        "dex_range": (810, 905),
        "req_level": 8,
        "emoji": "⚔️",
        "mascot_id": 888,
        "description": "An industrial region with vast Wild Areas and giant Dynamax Stadiums."
    },
    "Paldea": {
        "gen": 9,
        "dex_range": (906, 1025),
        "req_level": 9,
        "emoji": "💎",
        "mascot_id": 1007,
        "description": "An open-world region famous for Naranja/Uva Academy and Terastallization."
    }
}


def get_region_info(region_name: str) -> Dict[str, Any]:
    """Retrieve details for a given region name."""
    return REGIONS.get(region_name, REGIONS["Kanto"])


def get_all_regions() -> Dict[str, Dict[str, Any]]:
    """Return all region configurations."""
    return REGIONS
