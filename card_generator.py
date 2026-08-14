import io
import os
import httpx
import asyncio
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Optional
from tm_database import get_tm_info, get_tm_sprite_url

TYPE_COLORS = {
    "Fire": (239, 68, 68),
    "Grass": (34, 197, 94),
    "Poison": (168, 85, 247),
    "Water": (59, 130, 246),
    "Electric": (234, 179, 8),
    "Psychic": (236, 72, 153),
    "Ice": (6, 182, 212),
    "Dragon": (99, 102, 241),
    "Dark": (71, 85, 105),
    "Fairy": (244, 114, 182),
    "Default": (100, 116, 139)
}

BALL_SPRITE_URLS = {
    "pokeball": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png",
    "greatball": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/great-ball.png",
    "ultraball": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/ultra-ball.png",
    "masterball": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/master-ball.png",
}

POKEDOLLAR_SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/relic-gold.png"

CANDY_SPRITE_URLS = {
    "Rare Candy": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/rare-candy.png",
    "EXP Candy S": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/rare-candy.png",
    "EXP Candy M": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/rare-candy.png",
    "EXP Candy L": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/rare-candy.png"
}

TM_SPRITE_URLS = {
    "TM01": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/tm-fire.png",
    "TM02": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/tm-water.png",
    "TM03": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/tm-electric.png",
    "TM04": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/tm-ice.png",
    "TM05": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/tm-dragon.png"
}

ITEM_SPRITE_URLS = {
    "Fire Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/fire-stone.png",
    "Water Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/water-stone.png",
    "Thunder Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/thunder-stone.png",
    "Leaf Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/leaf-stone.png",
    "Moon Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/moon-stone.png",
    "Sun Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/sun-stone.png",
    "Shiny Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/shiny-stone.png",
    "Dusk Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dusk-stone.png",
    "Dawn Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dawn-stone.png",
    "Ice Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/ice-stone.png",
    "Mega Stone": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/mega-ring.png",
    "Mystery Egg": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/mystery-egg.png",
    "Lucky Egg": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/lucky-egg.png",
    "Shiny Egg": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/mystery-egg.png",
    "Manaphy Egg": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/manaphy-egg.png",
    "Egg Incubator": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/incubator.png",
    "Red Orb": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/red-orb.png",
    "Blue Orb": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/blue-orb.png",
    "Griseous Orb": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/griseous-orb.png",
    "Adamant Orb": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/adamant-orb.png",
    "Lustrous Orb": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/lustrous-orb.png",
    "Life Orb": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/life-orb.png",
    "Flame Orb": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/flame-orb.png",
    "Toxic Orb": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/toxic-orb.png",
    "Fire Z-Crystal": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/firium-z.png",
    "Water Z-Crystal": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/waterium-z.png",
    "Thunder Z-Crystal": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/electrium-z.png",
    "Grass Z-Crystal": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/grassium-z.png",
    "Tera Crystal": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/tera-shard.png",
    "Stellar Tera Crystal": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/tera-shard.png",
    "Heart Scale": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/heart-scale.png",
    "Draco Meteor Scroll": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/scroll-of-waters.png",
    "Secret Sword Scroll": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/scroll-of-darkness.png",
    "Relic Song Scroll": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/relic-copper.png",
    "Move Tutor Voucher": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/pass.png",
}

ITEM_DESCRIPTIONS = {
    "Fire Stone": "Evolves Fire-type Pokémon like Eevee & Vulpix.",
    "Water Stone": "Evolves Water-type Pokémon like Eevee & Shellder.",
    "Thunder Stone": "Evolves Electric-type Pokémon like Pikachu & Eevee.",
    "Leaf Stone": "Evolves Grass-type Pokémon like Gloom & Exeggcute.",
    "Moon Stone": "Evolves mystic Pokémon like Clefairy & Nidorino.",
    "Sun Stone": "Evolves solar Pokémon like Sunkern & Cottonee.",
    "Shiny Stone": "Evolves light Pokémon like Togetic & Roselia.",
    "Dusk Stone": "Evolves dark Pokémon like Murkrow & Misdreavus.",
    "Dawn Stone": "Evolves specific gender Pokémon like Kirlia.",
    "Ice Stone": "Evolves icy Pokémon like Alolan Vulpix.",
    "Mega Stone": "Unlocks Mega Evolution in battle.",
    "Mystery Egg": "An unhatched egg containing a mystery Pokémon.",
    "Lucky Egg": "Boosts battle EXP gained by +50%.",
    "Shiny Egg": "Guaranteed to hatch a rare Shiny Pokémon!",
    "Manaphy Egg": "A rare ocean egg containing Mythical Manaphy.",
    "Egg Incubator": "Device to hatch Pokémon Eggs faster.",
    "Red Orb": "Holds Primal Groudon's ancient magma energy.",
    "Blue Orb": "Holds Primal Kyogre's ancient ocean energy.",
    "Griseous Orb": "Powers up Giratina's Ghost & Dragon moves.",
    "Adamant Orb": "Powers up Dialga's Steel & Dragon moves.",
    "Lustrous Orb": "Powers up Palkia's Water & Dragon moves.",
    "Life Orb": "Boosts attack power by 30% at cost of HP.",
    "Flame Orb": "Inflicts Burn status on holder in battle.",
    "Toxic Orb": "Inflicts Bad Poison status on holder in battle.",
    "Fire Z-Crystal": "Unleashes Z-Move: Inferno Overdrive.",
    "Water Z-Crystal": "Unleashes Z-Move: Hydro Vortex.",
    "Thunder Z-Crystal": "Unleashes Z-Move: Gigavolt Havoc.",
    "Grass Z-Crystal": "Unleashes Z-Move: Bloom Doom.",
    "Tera Crystal": "Enables Terastallization in battle.",
    "Stellar Tera Crystal": "Unlocks the 19th Stellar Tera Type!",
    "Heart Scale": "Loved by Move Tutors to teach forgotten moves.",
    "Draco Meteor Scroll": "Teaches the ultimate Dragon move Draco Meteor.",
    "Secret Sword Scroll": "Teaches Keldeo the move Secret Sword.",
    "Relic Song Scroll": "Teaches Meloetta the move Relic Song.",
    "Move Tutor Voucher": "Pass granting free tutoring at any center.",
}

# In-Memory RAM Cache for sprites (URL -> PIL.Image) for 0ms instant loading
_ARTWORK_CACHE: Dict[str, Image.Image] = {}
_SHARED_CLIENT: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    global _SHARED_CLIENT
    if _SHARED_CLIENT is None or _SHARED_CLIENT.is_closed:
        _SHARED_CLIENT = httpx.AsyncClient(timeout=4.0, limits=httpx.Limits(max_keepalive_connections=20, max_connections=30))
    return _SHARED_CLIENT


async def _fetch_and_cache_artwork(url: str, max_size: tuple = (170, 170), force_resize: bool = False) -> Optional[Image.Image]:
    """Fetches artwork over HTTP once and caches in RAM for instant 0ms access on subsequent turns."""
    if not url:
        return None

    cache_key = f"{url}_{max_size[0]}x{max_size[1]}_{force_resize}"
    if cache_key in _ARTWORK_CACHE:
        return _ARTWORK_CACHE[cache_key].copy()

    try:
        client = _get_client()
        resp = await client.get(url)
        if resp.status_code == 200:
            p_img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
            if force_resize:
                p_img = p_img.resize(max_size, Image.Resampling.NEAREST)
            else:
                p_img.thumbnail(max_size)
            _ARTWORK_CACHE[cache_key] = p_img
            return p_img.copy()
    except Exception:
        pass

    return None


async def preload_artwork_cache() -> None:
    """Pre-warm RAM cache for all Pokéballs, Pokédollars, Candies, TMs, and starter assets on bot startup."""
    tasks = []
    for url in BALL_SPRITE_URLS.values():
        tasks.append(_fetch_and_cache_artwork(url, (44, 44), force_resize=True))

    tasks.append(_fetch_and_cache_artwork(POKEDOLLAR_SPRITE_URL, (110, 110), force_resize=True))

    for url in CANDY_SPRITE_URLS.values():
        tasks.append(_fetch_and_cache_artwork(url, (44, 44), force_resize=True))

    for url in TM_SPRITE_URLS.values():
        tasks.append(_fetch_and_cache_artwork(url, (44, 44), force_resize=True))

    for pid in [1, 4, 7]:
        url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png"
        tasks.append(_fetch_and_cache_artwork(url, (170, 170)))
        tasks.append(_fetch_and_cache_artwork(url, (200, 200)))
        tasks.append(_fetch_and_cache_artwork(url, (300, 300)))
        
    await asyncio.gather(*tasks, return_exceptions=True)


async def generate_starter_card(trainer_name: str, pokemon_data: Dict[str, Any]) -> io.BytesIO:
    """Generates a dynamic 800x480 custom Pokémon Starter Card image."""
    return await _build_pokemon_card(
        header_title=f"TRAINER: {trainer_name.upper()}",
        pokemon_data=pokemon_data,
        footer_text="★ HEXAMONBOT OFFICIAL STARTER CARD ★"
    )


async def generate_wild_card(trainer_name: str, pokemon_data: Dict[str, Any]) -> io.BytesIO:
    """Generates a dynamic 800x480 custom Wild Encounter Card image."""
    region_name = pokemon_data.get("region", "Wild").upper()
    return await _build_pokemon_card(
        header_title=f"WILD ENCOUNTER  •  {region_name}",
        pokemon_data=pokemon_data,
        footer_text="⚔️ WILD POKÉMON ENCOUNTER ⚔️",
        is_wild=True
    )


async def generate_battle_card(
    player_name: str,
    player_level: int,
    player_hp: int,
    player_max_hp: int,
    player_nature: str,
    player_image_url: str,
    wild_name: str,
    wild_level: int,
    wild_hp: int,
    wild_max_hp: int,
    wild_nature: str,
    wild_image_url: str,
    turn_number: int,
    turn_owner: str,
    status_text: str = ""
) -> io.BytesIO:
    """Generates an ultra-fast dynamic 800x480 visual Battle Arena Card image with live HP bars and RAM-cached artwork."""
    width, height = 800, 480
    image = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(image)

    # Outer Arena Frame
    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=20, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255), width=3)

    # Header Bar
    header_color = (59, 130, 246) if turn_owner == "player" else (239, 68, 68)
    draw.rounded_rectangle([25, 25, width - 25, 75], radius=12, fill=(15, 23, 42, 255), outline=header_color, width=2)

    # Fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_bold = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((40, 38), f"BATTLE ARENA  •  TURN {turn_number}", fill=(255, 255, 255, 255), font=font_title)
    owner_str = "YOUR TURN" if turn_owner == "player" else "WILD TURN"
    draw.text((width - 170, 39), owner_str, fill=header_color, font=font_title)

    # Draw Player Side (Left Container: x=35..385, y=90..410)
    draw.rounded_rectangle([35, 90, 385, 410], radius=15, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=2)
    draw.text((50, 105), f"{player_name.upper()} (LVL {player_level})", fill=(255, 255, 255, 255), font=font_sub)
    draw.text((50, 130), f"Nature: {player_nature}", fill=(148, 163, 184, 255), font=font_small)

    # Player Artwork (Instant 0ms from RAM Cache)
    p_img = await _fetch_and_cache_artwork(player_image_url, (170, 170))
    if p_img:
        image.paste(p_img, (50, 155), p_img)

    # Player HP Bar
    hp_pct = max(0.0, min(1.0, player_hp / max(1, player_max_hp)))
    hp_color = (34, 197, 94) if hp_pct > 0.5 else ((234, 179, 8) if hp_pct > 0.2 else (239, 68, 68))
    draw.text((50, 340), f"HP: {player_hp}/{player_max_hp}", fill=(255, 255, 255, 255), font=font_bold)
    draw.rounded_rectangle([50, 365, 370, 385], radius=6, fill=(51, 65, 85, 255))
    if int(320 * hp_pct) > 0:
        draw.rounded_rectangle([50, 365, 50 + int(320 * hp_pct), 385], radius=6, fill=hp_color)

    # Draw Wild Side (Right Container: x=415..765, y=90..410)
    draw.rounded_rectangle([415, 90, 765, 410], radius=15, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=2)
    draw.text((430, 105), f"WILD {wild_name.upper()} (LVL {wild_level})", fill=(249, 115, 22, 255), font=font_sub)
    draw.text((430, 130), f"Nature: {wild_nature}", fill=(148, 163, 184, 255), font=font_small)

    # Wild Artwork (Instant 0ms from RAM Cache)
    w_img = await _fetch_and_cache_artwork(wild_image_url, (170, 170))
    if w_img:
        image.paste(w_img, (430, 155), w_img)

    # Wild HP Bar
    w_hp_pct = max(0.0, min(1.0, wild_hp / max(1, wild_max_hp)))
    w_hp_color = (34, 197, 94) if w_hp_pct > 0.5 else ((234, 179, 8) if w_hp_pct > 0.2 else (239, 68, 68))
    draw.text((430, 340), f"HP: {wild_hp}/{wild_max_hp}", fill=(255, 255, 255, 255), font=font_bold)
    draw.rounded_rectangle([430, 365, 750, 385], radius=6, fill=(51, 65, 85, 255))
    if int(320 * w_hp_pct) > 0:
        draw.rounded_rectangle([430, 365, 430 + int(320 * w_hp_pct), 385], radius=6, fill=w_hp_color)

    # Status Banner (Bottom: y=420..460)
    draw.rounded_rectangle([35, 420, 765, 460], radius=10, fill=(15, 23, 42, 255), outline=(71, 85, 105, 255), width=1)
    status_disp = status_text if status_text else "Select an attack move or action below!"
    draw.text((50, 432), status_disp[:85], fill=(226, 232, 240, 255), font=font_small)

    buf = io.BytesIO()
    rgb_image = image.convert("RGB")
    rgb_image.save(buf, format="JPEG", quality=75, optimize=False)
    buf.seek(0)
    return buf


async def generate_catch_menu_card(inventory: Dict[str, int]) -> io.BytesIO:
    """Generates a visual graphic card displaying real Pokéball sprites and inventory counts across the entire layout."""
    width, height = 800, 480
    image = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(image)

    accent = (59, 130, 246)  # Blue accent

    # Outer Frame
    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=20, fill=(30, 41, 59, 255), outline=accent, width=3)

    # Header Bar
    draw.rounded_rectangle([25, 25, width - 25, 80], radius=12, fill=(15, 23, 42, 255), outline=accent, width=2)

    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_bold = ImageFont.truetype("arial.ttf", 16)
        font_sub = ImageFont.truetype("arial.ttf", 13)
        font_count = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font_title = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_count = ImageFont.load_default()

    draw.text((40, 40), "POKÉBALL INVENTORY & CATCH RATES", fill=(255, 255, 255, 255), font=font_title)

    balls_info = [
        ("pokeball", "Poké Ball", "Standard Catch Rate (1.0x)", (239, 68, 68)),
        ("greatball", "Great Ball", "Higher Catch Rate (1.5x)", (59, 130, 246)),
        ("ultraball", "Ultra Ball", "Superior Catch Rate (2.0x)", (234, 179, 8)),
        ("masterball", "Master Ball", "Guaranteed Catch Rate (255.0x)", (168, 85, 247))
    ]

    card_y = 95
    for b_key, b_name, b_desc, b_color in balls_info:
        count = inventory.get(b_key, 0)

        box_bg = (15, 23, 42, 255) if count > 0 else (20, 27, 44, 255)
        border_col = b_color if count > 0 else (51, 65, 85, 255)
        text_col = (255, 255, 255, 255) if count > 0 else (100, 116, 139, 255)

        # Row Card Container (x=35..765)
        draw.rounded_rectangle([35, card_y, 765, card_y + 75], radius=14, fill=box_bg, outline=border_col, width=2)

        # Real Pokéball Sprite Artwork (Instant 0ms RAM Cache)
        sprite_url = BALL_SPRITE_URLS.get(b_key, "")
        b_img = await _fetch_and_cache_artwork(sprite_url, (50, 50))
        if b_img:
            image.paste(b_img, (50, card_y + 12), b_img)
        else:
            # Color pill fallback if network fails
            draw.rounded_rectangle([50, card_y + 17, 90, card_y + 57], radius=8, fill=b_color)

        # Ball Name & Catch Rate Description
        draw.text((120, card_y + 16), b_name.upper(), fill=text_col, font=font_bold)
        draw.text((120, card_y + 44), b_desc, fill=(148, 163, 184, 255), font=font_sub)

        # Quantity Pill Badge (x=665..745)
        count_bg = b_color if count > 0 else (51, 65, 85, 255)
        draw.rounded_rectangle([665, card_y + 17, 745, card_y + 57], radius=10, fill=count_bg)
        draw.text((682, card_y + 24), f"x{count}", fill=(255, 255, 255, 255), font=font_count)

        card_y += 88

    buf = io.BytesIO()
    rgb_image = image.convert("RGB")
    rgb_image.save(buf, format="JPEG", quality=75, optimize=False)
    buf.seek(0)
    return buf


async def generate_battle_outcome_card(
    outcome_type: str,  # "victory", "fainted", "fled"
    player_name: str,
    player_image_url: str,
    wild_name: str,
    wild_image_url: str,
    status_text: str = ""
) -> io.BytesIO:
    """Generates visual graphic cards for Battle End states: Victory, Fainted, or Fled."""
    width, height = 800, 480
    image = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(image)

    # Frame color by outcome
    if outcome_type == "victory":
        accent = (34, 197, 94)  # Green
        title_str = "VICTORY IN BATTLE!"
    elif outcome_type == "fainted":
        accent = (239, 68, 68)  # Red
        title_str = "POKÉMON FAINTED!"
    else:
        accent = (148, 163, 184)  # Gray
        title_str = "SAFELY ESCAPED!"

    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=20, fill=(30, 41, 59, 255), outline=accent, width=3)
    draw.rounded_rectangle([25, 25, width - 25, 80], radius=12, fill=(15, 23, 42, 255), outline=accent, width=2)

    try:
        font_title = ImageFont.truetype("arial.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    draw.text((40, 40), title_str, fill=accent, font=font_title)

    # Player Artwork
    p_img = await _fetch_and_cache_artwork(player_image_url, (200, 200))
    if p_img:
        image.paste(p_img, (100, 120), p_img)

    # Wild Artwork
    w_img = await _fetch_and_cache_artwork(wild_image_url, (200, 200))
    if w_img:
        image.paste(w_img, (500, 120), w_img)

    # Status Banner at Bottom
    draw.rounded_rectangle([40, 360, 760, 440], radius=15, fill=(15, 23, 42, 255), outline=accent, width=2)
    draw.text((60, 390), status_text[:90], fill=(255, 255, 255, 255), font=font_sub)

    buf = io.BytesIO()
    rgb_image = image.convert("RGB")
    rgb_image.save(buf, format="JPEG", quality=75, optimize=False)
    buf.seek(0)
    return buf


async def generate_catch_card(
    stage: str,  # "shake_1", "shake_2", "shake_3", "caught", "broke_free"
    wild_name: str,
    wild_image_url: str,
    ball_name: str = "Poké Ball",
    iv_pct: float = 0.0,
    grade: str = "",
    nature: str = ""
) -> io.BytesIO:
    """Generates visual graphic cards for Catching animations and Catch success/break-free results."""
    width, height = 800, 480
    image = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(image)

    if stage == "caught":
        accent = (234, 179, 8)  # Gold
        title_str = f"GOTCHA! CAUGHT {wild_name.upper()}!"
    elif stage == "broke_free":
        accent = (239, 68, 68)  # Red
        title_str = f"{wild_name.upper()} BROKE FREE!"
    else:
        accent = (59, 130, 246)  # Blue
        title_str = f"THROWING {ball_name.upper()}..."

    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=20, fill=(30, 41, 59, 255), outline=accent, width=3)
    draw.rounded_rectangle([25, 25, width - 25, 80], radius=12, fill=(15, 23, 42, 255), outline=accent, width=2)

    try:
        font_title = ImageFont.truetype("arial.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_bold = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    draw.text((40, 40), title_str, fill=accent, font=font_title)

    # Wild Artwork
    w_img = await _fetch_and_cache_artwork(wild_image_url, (220, 220))
    if w_img:
        image.paste(w_img, (290, 100), w_img)

    if stage.startswith("shake_"):
        shake_num = int(stage.split("_")[1])
        star_str = " ".join(["✰"] * shake_num)
        draw.text((360, 350), star_str, fill=(234, 179, 8, 255), font=font_title)
    elif stage == "caught":
        # Draw IV & Nature Summary
        draw.rounded_rectangle([100, 340, 700, 440], radius=15, fill=(15, 23, 42, 255), outline=accent, width=2)
        draw.text((120, 360), f"Nature: {nature}  │  IV Quality: {iv_pct}% ({grade})", fill=(255, 255, 255, 255), font=font_sub)
        draw.text((120, 395), f"Saved to your Pokémon Box!", fill=(148, 163, 184, 255), font=font_bold)
    elif stage == "broke_free":
        draw.rounded_rectangle([100, 350, 700, 430], radius=15, fill=(15, 23, 42, 255), outline=accent, width=2)
        draw.text((120, 375), f"Wild {wild_name} broke free and is counter-attacking!", fill=(255, 255, 255, 255), font=font_bold)

    buf = io.BytesIO()
    rgb_image = image.convert("RGB")
    rgb_image.save(buf, format="JPEG", quality=75, optimize=False)
    buf.seek(0)
    return buf


async def _build_pokemon_card(
    header_title: str,
    pokemon_data: Dict[str, Any],
    footer_text: str,
    is_wild: bool = False
) -> io.BytesIO:
    width, height = 800, 480
    image = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(image)

    # Outer Card Container
    card_margin = 20
    card_rect = [card_margin, card_margin, width - card_margin, height - card_margin]
    draw.rounded_rectangle(card_rect, radius=20, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255), width=3)

    # Type Accent Border Line
    primary_type = pokemon_data["types"][0] if pokemon_data.get("types") else "Default"
    accent_color = TYPE_COLORS.get(primary_type, TYPE_COLORS["Default"])
    if is_wild:
        accent_color = (249, 115, 22)  # Wild Amber/Orange accent

    draw.rounded_rectangle(
        [card_margin + 5, card_margin + 5, width - card_margin - 5, height - card_margin - 5],
        radius=18, outline=accent_color, width=2
    )

    # Fetch official artwork (cached)
    poke_img = await _fetch_and_cache_artwork(pokemon_data.get("image_url", ""), (300, 300))
    if poke_img:
        image.paste(poke_img, (40, 90), poke_img)

    # Fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 32)
        font_subtitle = ImageFont.truetype("arial.ttf", 20)
        font_stats = ImageFont.truetype("arial.ttf", 16)
        font_badge = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_stats = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # Header
    x_start = 350
    level_val = pokemon_data.get("wild_level", pokemon_data.get("level", 5))
    draw.text((x_start, 35), header_title, fill=(148, 163, 184, 255), font=font_subtitle)
    draw.text((x_start, 62), f"{pokemon_data['name'].upper()}", fill=(255, 255, 255, 255), font=font_title)
    draw.text((x_start + 260, 72), f"LVL {level_val}", fill=accent_color, font=font_subtitle)

    # Type Badges
    badge_x = x_start
    badge_y = 108
    for ptype in pokemon_data.get("types", []):
        bg_color = TYPE_COLORS.get(ptype, TYPE_COLORS["Default"])
        draw.rounded_rectangle([badge_x, badge_y, badge_x + 85, badge_y + 24], radius=12, fill=bg_color)
        draw.text((badge_x + 12, badge_y + 4), ptype.upper(), fill=(255, 255, 255, 255), font=font_badge)
        badge_x += 95

    # Nature & IV Quality Info Box
    nature = pokemon_data.get("nature", "Hardy")
    from iv_ev_system import get_nature_info, get_iv_grade
    nature_info = get_nature_info(nature)
    nature_desc = nature_info.get("desc", "Neutral")

    ivs = pokemon_data.get("ivs", {})
    iv_pct = ivs.get("total_pct", 50.0)
    grade_str = ivs.get("grade") or get_iv_grade(iv_pct)

    draw.text((x_start, 142), f"Nature: {nature} ({nature_desc})", fill=(148, 163, 184, 255), font=font_badge)
    draw.text((x_start, 164), f"IV Quality: {iv_pct}% ({grade_str})", fill=(234, 179, 8, 255), font=font_badge)

    # Base Stats Section
    stats = pokemon_data["stats"]
    stat_list = [
        ("HP", stats.get("hp", 40), 120, (239, 68, 68)),
        ("ATTACK", stats.get("attack", 50), 120, (249, 115, 22)),
        ("DEFENSE", stats.get("defense", 50), 120, (234, 179, 8)),
        ("SP. ATK", stats.get("special-attack", stats.get("sp_attack", 50)), 120, (59, 130, 246)),
        ("SP. DEF", stats.get("special-defense", stats.get("sp_defense", 50)), 120, (168, 85, 247)),
        ("SPEED", stats.get("speed", 50), 120, (34, 197, 94))
    ]

    y_pos = 195
    bar_width_max = 240

    for name, val, max_val, color in stat_list:
        draw.text((x_start, y_pos), f"{name:<8}", fill=(203, 213, 225, 255), font=font_stats)
        draw.text((x_start + 80, y_pos), f"{val:>3}", fill=(255, 255, 255, 255), font=font_stats)

        bar_x = x_start + 125
        draw.rounded_rectangle([bar_x, y_pos + 4, bar_x + bar_width_max, y_pos + 14], radius=5, fill=(51, 65, 85, 255))

        filled_width = int((val / max_val) * bar_width_max)
        if filled_width > 0:
            draw.rounded_rectangle([bar_x, y_pos + 4, bar_x + filled_width, y_pos + 14], radius=5, fill=color)

        y_pos += 35

    # Footer note
    draw.text((x_start, 435), footer_text, fill=(100, 116, 139, 255), font=font_badge)

    buf = io.BytesIO()
    rgb_image = image.convert("RGB")
    rgb_image.save(buf, format="JPEG", quality=75, optimize=False)
    buf.seek(0)
    return buf


async def generate_switch_pokemon_card(team_list: List[Dict[str, Any]], active_db_id: int) -> io.BytesIO:
    """Generates an 800x480 custom card graphic displaying user's team Pokémon (up to 6 members) with HP bars and status badges."""
    width, height = 800, 480
    image = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(image)

    accent = (59, 130, 246)  # Blue accent

    # Outer Frame
    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=20, fill=(30, 41, 59, 255), outline=accent, width=3)

    # Header Bar
    draw.rounded_rectangle([25, 25, width - 25, 80], radius=12, fill=(15, 23, 42, 255), outline=accent, width=2)

    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_bold = ImageFont.truetype("arial.ttf", 15)
        font_sub = ImageFont.truetype("arial.ttf", 13)
        font_badge = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font_title = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    draw.text((40, 40), "SELECT POKÉMON TO SWITCH", fill=(255, 255, 255, 255), font=font_title)
    draw.text((width - 220, 43), f"TEAM SIZE: {len(team_list)}/6", fill=(148, 163, 184, 255), font=font_bold)

    # Grid Layout: 2 columns x 3 rows
    row_coords = [
        (35, 95, 385, 205), (415, 95, 765, 205),
        (35, 215, 385, 325), (415, 215, 765, 325),
        (35, 335, 385, 445), (415, 335, 765, 445),
    ]

    for idx, slot in enumerate(row_coords):
        if idx >= len(team_list):
            # Empty Team Slot Card Box
            draw.rounded_rectangle(slot, radius=12, fill=(20, 27, 44, 255), outline=(51, 65, 85, 255), width=1)
            draw.text((slot[0] + 110, slot[1] + 42), f"Slot #{idx+1} (Empty)", fill=(100, 116, 139, 255), font=font_sub)
            continue

        poke = team_list[idx]
        p_db_id = poke.get("id", 0)
        curr_hp = poke.get("hp", 0)
        max_hp = max(1, poke.get("max_hp", 1))
        is_active = (p_db_id == active_db_id)
        is_fainted = (curr_hp <= 0)

        # Background & border color
        if is_fainted:
            bg_col = (30, 25, 35, 255)
            border_col = (239, 68, 68, 255)  # Red
            badge_text = "FAINTED"
            badge_col = (239, 68, 68, 255)
        elif is_active:
            bg_col = (20, 40, 70, 255)
            border_col = (59, 130, 246, 255)  # Blue
            badge_text = "ACTIVE"
            badge_col = (59, 130, 246, 255)
        else:
            bg_col = (15, 23, 42, 255)
            border_col = (34, 197, 94, 255)  # Green
            badge_text = "READY"
            badge_col = (34, 197, 94, 255)

        draw.rounded_rectangle(slot, radius=12, fill=bg_col, outline=border_col, width=2)

        # Pokémon Artwork Sprite
        img_url = poke.get("image_url", f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{poke['pokemon_id']}.png")
        p_img = await _fetch_and_cache_artwork(img_url, (75, 75))
        if p_img:
            image.paste(p_img, (slot[0] + 10, slot[1] + 15), p_img)

        # Text Info
        draw.text((slot[0] + 95, slot[1] + 12), f"{poke['name'].upper()}", fill=(255, 255, 255, 255), font=font_bold)
        draw.text((slot[0] + 95, slot[1] + 34), f"Lvl {poke['level']} • {poke.get('nature', 'Hardy')}", fill=(148, 163, 184, 255), font=font_sub)

        # Status Pill Badge
        draw.rounded_rectangle([slot[2] - 80, slot[1] + 10, slot[2] - 10, slot[1] + 30], radius=8, fill=badge_col)
        draw.text((slot[2] - 72, slot[1] + 14), badge_text, fill=(255, 255, 255, 255), font=font_badge)

        # HP Bar
        hp_pct = max(0.0, min(1.0, curr_hp / max_hp))
        hp_color = (34, 197, 94) if hp_pct > 0.5 else ((234, 179, 8) if hp_pct > 0.2 else (239, 68, 68))
        draw.text((slot[0] + 95, slot[1] + 56), f"HP: {curr_hp}/{max_hp}", fill=(226, 232, 240, 255), font=font_sub)
        draw.rounded_rectangle([slot[0] + 95, slot[1] + 78, slot[2] - 15, slot[1] + 92], radius=4, fill=(51, 65, 85, 255))
        bar_len = int((slot[2] - 110 - slot[0]) * hp_pct)
        if bar_len > 0:
            draw.rounded_rectangle([slot[0] + 95, slot[1] + 78, slot[0] + 95 + bar_len, slot[1] + 92], radius=4, fill=hp_color)

    buf = io.BytesIO()
    rgb_image = image.convert("RGB")
    rgb_image.save(buf, format="JPEG", quality=75, optimize=False)
    buf.seek(0)
    return buf


async def generate_inventory_card(trainer_name: str, inventory: Dict[str, Any], category: str = "pokedollars") -> io.BytesIO:
    """
    Generates 800x480 category-specific custom inventory graphic cards:
    - 'pokedollars': Dedicated Trainer Wallet card (ONLY shows Pokédollars!)
    - 'balls': Dedicated Pokéballs card (ONLY shows balls user HAS!)
    - 'candies': Dedicated Candies card (ONLY shows candies user HAS!)
    - 'tms': Dedicated TMs card (ONLY shows TMs user HAS!)
    """
    width, height = 800, 480
    image = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(image)

    cat_colors = {
        "pokedollars": (234, 179, 8),  # Gold
        "balls": (239, 68, 68),        # Red
        "candies": (168, 85, 247),     # Purple
        "tms": (34, 197, 94),          # Green
        "stones": (6, 182, 212),       # Cyan / Diamond
        "eggs": (245, 158, 11),        # Amber / Egg
        "orbs": (236, 72, 153),        # Pink / Orb
        "crystals": (99, 102, 241),    # Indigo / Crystal
        "tutors": (249, 115, 22),      # Orange / Scroll
    }
    accent = cat_colors.get(category, cat_colors["pokedollars"])

    # Outer Frame & Header Bar
    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=20, fill=(30, 41, 59, 255), outline=accent, width=3)
    draw.rounded_rectangle([25, 25, width - 25, 80], radius=12, fill=(15, 23, 42, 255), outline=accent, width=2)

    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_bold = ImageFont.truetype("arial.ttf", 16)
        font_sub = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        font_title = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    cat_titles = {
        "pokedollars": f"{trainer_name.upper()}'S POKÉDOLLAR WALLET",
        "balls": f"{trainer_name.upper()}'S POKÉBALL POUCH",
        "candies": f"{trainer_name.upper()}'S CANDY POUCH",
        "tms": f"{trainer_name.upper()}'S TM CASE",
        "stones": f"{trainer_name.upper()}'S EVOLUTION STONE POUCH",
        "eggs": f"{trainer_name.upper()}'S EGG & INCUBATOR POUCH",
        "orbs": f"{trainer_name.upper()}'S LEGENDARY ORB CASE",
        "crystals": f"{trainer_name.upper()}'S CRYSTAL & TERA VAULT",
        "tutors": f"{trainer_name.upper()}'S TUTOR & SCROLL BAG",
    }

    draw.text((40, 40), cat_titles.get(category, cat_titles["pokedollars"]), fill=(255, 255, 255, 255), font=font_title)

    if category == "balls":
        draw.rounded_rectangle([35, 95, 765, 440], radius=15, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=2)
        draw.text((50, 110), "🔴 POKÉBALLS IN INVENTORY", fill=(239, 68, 68, 255), font=font_bold)

        balls_data = [
            ("pokeball", "Poké Ball", inventory.get("pokeball", 10), "1.0x", "Standard ball for catching wild Pokémon."),
            ("greatball", "Great Ball", inventory.get("greatball", 5), "1.5x", "High performance ball with higher success rate."),
            ("ultraball", "Ultra Ball", inventory.get("ultraball", 0), "2.0x", "Ultra-high performance ball for tough Pokémon."),
            ("masterball", "Master Ball", inventory.get("masterball", 0), "255x", "The ultimate ball. Catches any wild Pokémon without fail!")
        ]
        owned_balls = [b for b in balls_data if b[2] > 0]

        if owned_balls:
            b_y = 145
            for key, name, count, mult, desc in owned_balls:
                draw.rounded_rectangle([50, b_y, 750, b_y + 62], radius=10, fill=(20, 27, 44, 255), outline=(51, 65, 85, 255), width=1)
                b_img = await _fetch_and_cache_artwork(BALL_SPRITE_URLS[key], (44, 44))
                if b_img:
                    image.paste(b_img, (65, b_y + 9), b_img)
                draw.text((125, b_y + 12), name, fill=(255, 255, 255, 255), font=font_bold)
                draw.text((125, b_y + 35), f"{desc} • Catch Rate: {mult}", fill=(148, 163, 184, 255), font=font_sub)
                draw.rounded_rectangle([650, b_y + 16, 735, b_y + 46], radius=8, fill=(30, 41, 59, 255), outline=(239, 68, 68, 255), width=1)
                draw.text((672, b_y + 21), f"x{count}", fill=(239, 68, 68, 255), font=font_bold)
                b_y += 72
        else:
            draw.rounded_rectangle([100, 200, 700, 320], radius=15, fill=(20, 27, 44, 255), outline=(239, 68, 68, 255), width=2)
            draw.text((220, 250), "⚠️ No Pokéballs in inventory!", fill=(255, 255, 255, 255), font=font_title)

    elif category == "candies":
        draw.rounded_rectangle([35, 95, 765, 440], radius=15, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=2)
        draw.text((50, 110), "CANDIES IN INVENTORY", fill=(168, 85, 247, 255), font=font_bold)

        candies_data = [
            ("Rare Candy", inventory.get("rare_candy", 0), "Level Up", "Raises a Pokémon's level by 1."),
            ("EXP Candy S", inventory.get("exp_candy_s", 0), "+100 EXP", "Grants 100 EXP."),
            ("EXP Candy M", inventory.get("exp_candy_m", 0), "+500 EXP", "Grants 500 EXP."),
            ("EXP Candy L", inventory.get("exp_candy_l", 0), "+2000 EXP", "Grants 2000 EXP.")
        ]
        owned_candies = [c for c in candies_data if c[1] > 0]

        if owned_candies:
            c_y = 145
            for c_name, c_count, c_tag, c_desc in owned_candies:
                draw.rounded_rectangle([50, c_y, 750, c_y + 62], radius=10, fill=(20, 27, 44, 255), outline=(51, 65, 85, 255), width=1)
                
                c_url = CANDY_SPRITE_URLS.get(c_name, "")
                c_img = await _fetch_and_cache_artwork(c_url, (44, 44))
                if c_img:
                    image.paste(c_img, (65, c_y + 9), c_img)

                draw.text((125, c_y + 12), c_name, fill=(255, 255, 255, 255), font=font_bold)
                draw.text((125, c_y + 35), f"{c_desc} ({c_tag})", fill=(148, 163, 184, 255), font=font_sub)
                draw.rounded_rectangle([650, c_y + 16, 735, c_y + 46], radius=8, fill=(30, 41, 59, 255), outline=(168, 85, 247, 255), width=1)
                draw.text((672, c_y + 21), f"x{c_count}", fill=(168, 85, 247, 255), font=font_bold)
                c_y += 72
        else:
            draw.rounded_rectangle([150, 210, 650, 310], radius=15, fill=(20, 27, 44, 255), outline=(168, 85, 247, 255), width=2)
            draw.text((280, 248), "No Candies in inventory", fill=(255, 255, 255, 255), font=font_title)

    elif category == "tms":
        draw.rounded_rectangle([35, 95, 765, 440], radius=15, fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=2)
        draw.text((50, 110), "TECHNICAL MACHINES (TMs) IN CASE", fill=(34, 197, 94, 255), font=font_bold)

        user_tms = inventory.get("tms", {})
        owned_tms = [(tm_id, count) for tm_id, count in user_tms.items() if count > 0]

        if owned_tms:
            tm_y = 145
            for tm_id, count in owned_tms:
                tm_info = get_tm_info(tm_id)
                tm_url = get_tm_sprite_url(tm_id)
                draw.rounded_rectangle([50, tm_y, 750, tm_y + 62], radius=10, fill=(20, 27, 44, 255), outline=(51, 65, 85, 255), width=1)
                
                tm_img = await _fetch_and_cache_artwork(tm_url, (44, 44), force_resize=True)
                if tm_img:
                    image.paste(tm_img, (65, tm_y + 9), tm_img)

                draw.text((125, tm_y + 12), tm_info["name"], fill=(255, 255, 255, 255), font=font_bold)
                draw.text((125, tm_y + 35), f"Type: {tm_info['type']}  │  Power: {tm_info['power']} • Acc: {tm_info['accuracy']}%", fill=(148, 163, 184, 255), font=font_sub)
                draw.rounded_rectangle([650, tm_y + 16, 735, tm_y + 46], radius=8, fill=(30, 41, 59, 255), outline=(34, 197, 94, 255), width=1)
                draw.text((672, tm_y + 21), f"x{count}", fill=(34, 197, 94, 255), font=font_bold)
                tm_y += 72
        else:
            draw.rounded_rectangle([150, 210, 650, 310], radius=15, fill=(20, 27, 44, 255), outline=(34, 197, 94, 255), width=2)
            draw.text((290, 248), "No TMs in TM Case", fill=(255, 255, 255, 255), font=font_title)

    elif category in ["stones", "eggs", "orbs", "crystals", "tutors"]:
        draw.rounded_rectangle([35, 95, 765, 440], radius=15, fill=(15, 23, 42, 255), outline=accent, width=2)
        
        cat_hdr_titles = {
            "stones": "💎 EVOLUTION & MEGA STONES",
            "eggs": "🥚 POKÉMON EGGS & INCUBATORS",
            "orbs": "🔮 LEGENDARY & BATTLE ORBS",
            "crystals": "✨ Z-CRYSTALS & TERA CRYSTALS",
            "tutors": "📜 MOVE TUTOR ITEMS & SCROLLS",
        }
        draw.text((50, 110), cat_hdr_titles.get(category, "ITEMS IN POUCH"), fill=accent + (255,), font=font_bold)

        cat_items = inventory.get(category, {})
        owned_items = [(name, cnt) for name, cnt in cat_items.items() if cnt > 0]

        if owned_items:
            i_y = 145
            for name, count in owned_items[:4]:
                desc = ITEM_DESCRIPTIONS.get(name, "Special Pokémon adventure item.")
                url = ITEM_SPRITE_URLS.get(name, "")
                
                draw.rounded_rectangle([50, i_y, 750, i_y + 62], radius=10, fill=(20, 27, 44, 255), outline=(51, 65, 85, 255), width=1)
                
                if url:
                    item_img = await _fetch_and_cache_artwork(url, (44, 44), force_resize=True)
                    if item_img:
                        image.paste(item_img, (65, i_y + 9), item_img)

                draw.text((125, i_y + 12), name, fill=(255, 255, 255, 255), font=font_bold)
                draw.text((125, i_y + 35), desc, fill=(148, 163, 184, 255), font=font_sub)
                
                draw.rounded_rectangle([650, i_y + 16, 735, i_y + 46], radius=8, fill=(30, 41, 59, 255), outline=accent + (255,), width=1)
                draw.text((672, i_y + 21), f"x{count}", fill=accent + (255,), font=font_bold)
                i_y += 72
        else:
            draw.rounded_rectangle([150, 210, 650, 310], radius=15, fill=(20, 27, 44, 255), outline=accent + (255,), width=2)
            draw.text((250, 248), f"No items in {category.title()} pouch", fill=(255, 255, 255, 255), font=font_title)

    else:
        # Default Pokédollar Wallet Category Card
        draw.rounded_rectangle([35, 95, 765, 440], radius=15, fill=(15, 23, 42, 255), outline=(234, 179, 8, 255), width=2)
        draw.text((50, 110), "POKÉDOLLAR WALLET", fill=(234, 179, 8, 255), font=font_bold)

        pd_val = inventory.get("pokedollars", 0)

        # Centered Gold Balance Box with Real Gold Coin Photo Sprite (Scaled Up Big!)
        draw.rounded_rectangle([120, 160, 680, 360], radius=20, fill=(20, 27, 44, 255), outline=(234, 179, 8, 255), width=3)
        
        pd_img = await _fetch_and_cache_artwork(POKEDOLLAR_SPRITE_URL, (120, 120), force_resize=True)
        if pd_img:
            image.paste(pd_img, (160, 200), pd_img)

        draw.text((300, 210), "TOTAL BALANCE", fill=(148, 163, 184, 255), font=font_bold)
        draw.text((300, 250), f"{pd_val} PD", fill=(234, 179, 8, 255), font=font_large)

    buf = io.BytesIO()
    rgb_image = image.convert("RGB")
    rgb_image.save(buf, format="JPEG", quality=75, optimize=False)
    buf.seek(0)
    return buf


async def generate_region_card(
    region_name: str,
    trainer_level: int = 1
) -> io.BytesIO:
    """Returns the regional map image file itself as the full graphic card without any extra text overlays or containers."""
    map_file_path = f"assets/maps/{region_name.lower()}.png"
    if not os.path.exists(map_file_path):
        map_file_path = "assets/maps/kanto.png"

    with Image.open(map_file_path) as img:
        img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=92, optimize=True)
        buf.seek(0)
        return buf


CARD_THEMES: Dict[str, Dict[str, Any]] = {
    "Classic Red": {
        "bg_outer": (180, 40, 40),
        "bg_inner": (248, 190, 185),
        "border_dark": (130, 20, 20),
        "border_light": (255, 230, 225),
        "avatar_bg": (255, 235, 230),
        "header_text": (130, 20, 20),
        "badge_bar": (245, 170, 165)
    },
    "Navy Blue": {
        "bg_outer": (30, 64, 120),
        "bg_inner": (195, 218, 245),
        "border_dark": (20, 40, 80),
        "border_light": (230, 240, 255),
        "avatar_bg": (225, 240, 255),
        "header_text": (20, 40, 100),
        "badge_bar": (175, 200, 235)
    },
    "Emerald Green": {
        "bg_outer": (25, 110, 60),
        "bg_inner": (195, 238, 208),
        "border_dark": (15, 70, 35),
        "border_light": (230, 255, 238),
        "avatar_bg": (225, 252, 235),
        "header_text": (15, 80, 40),
        "badge_bar": (175, 225, 190)
    },
    "Golden Sunset": {
        "bg_outer": (205, 105, 20),
        "bg_inner": (255, 225, 175),
        "border_dark": (140, 60, 10),
        "border_light": (255, 248, 220),
        "avatar_bg": (255, 242, 210),
        "header_text": (140, 60, 10),
        "badge_bar": (245, 205, 150)
    },
    "Purple Nebula": {
        "bg_outer": (110, 45, 145),
        "bg_inner": (228, 200, 245),
        "border_dark": (65, 20, 90),
        "border_light": (250, 235, 255),
        "avatar_bg": (242, 225, 255),
        "header_text": (70, 20, 100),
        "badge_bar": (210, 175, 235)
    },
    "Dark Onyx": {
        "bg_outer": (35, 39, 47),
        "bg_inner": (75, 85, 99),
        "border_dark": (20, 22, 28),
        "border_light": (156, 163, 175),
        "avatar_bg": (107, 114, 128),
        "header_text": (243, 244, 246),
        "badge_bar": (55, 65, 80)
    }
}

CARD_TEXT_COLORS: Dict[str, Tuple[int, int, int]] = {
    "Classic Dark": (40, 20, 20),
    "Crisp White": (255, 255, 255),
    "Golden Yellow": (180, 110, 0),
    "Crimson Red": (160, 20, 20),
    "Navy Blue": (20, 50, 120),
    "Emerald Green": (15, 100, 45)
}

CARD_AVATARS: Dict[str, str] = {
    "Captain Trainer": "assets/avatars/captain.png",
    "Male Trainer": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/trainers/1.png",
    "Female Trainer": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/trainers/2.png",
    "Ace Trainer": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/trainers/10.png",
    "Champion Red": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/trainers/100.png",
    "Champion Cynthia": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/trainers/247.png",
    "Ash Ketchum": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/trainers/245.png"
}


async def generate_trainer_card(
    user_id: int,
    username: str,
    first_name: str,
    trainer_level: int = 1,
    trainer_exp: int = 0,
    wins: int = 0,
    losses: int = 0,
    joined_at: str = "2025-11-06 12:00:00",
    theme_name: str = "Classic Red",
    text_color_name: str = "Classic Dark",
    avatar_name: str = "Captain Trainer"
) -> io.BytesIO:
    """Generates a high-definition, crystal-clear customizable Trainer Card for /mystats."""
    import datetime
    import logging
    logger = logging.getLogger(__name__)

    theme = CARD_THEMES.get(theme_name, CARD_THEMES["Classic Red"])
    text_color = CARD_TEXT_COLORS.get(text_color_name, CARD_TEXT_COLORS["Classic Dark"])

    # High-resolution 800x520 canvas for crystal-clear text and graphic elements
    width, height = 800, 520
    base_img = Image.new("RGBA", (width, height), theme["bg_outer"] + (255,))
    draw = ImageDraw.Draw(base_img)

    # Outer Double Border Container
    margin = 12
    draw.rounded_rectangle([margin, margin, width - margin, height - margin], radius=24, fill=theme["bg_inner"] + (255,), outline=theme["border_dark"], width=4)
    draw.rounded_rectangle([margin + 6, margin + 6, width - margin - 6, height - margin - 6], radius=20, fill=None, outline=theme["border_light"], width=3)

    # Subtle Accent Pattern / Background Swirl in center
    bg_flame = theme.get("bg_flame", (235, 140, 130))
    draw.ellipse([80, 60, 620, 440], fill=bg_flame + (100,))
    draw.ellipse([140, 100, 560, 400], fill=theme["bg_inner"] + (255,))

    # Load high-resolution fonts with fallbacks
    try:
        font_header_title = ImageFont.truetype("arialbd.ttf", 26)
        font_header_rank = ImageFont.truetype("arialbd.ttf", 22)
        font_id = ImageFont.truetype("arial.ttf", 18)
        font_label = ImageFont.truetype("arial.ttf", 19)
        font_val = ImageFont.truetype("arialbd.ttf", 20)
        font_badge_hdr = ImageFont.truetype("arialbd.ttf", 22)
    except IOError:
        font_header_title = font_header_rank = font_id = font_label = font_val = font_badge_hdr = ImageFont.load_default()

    # Header Bar (Y: 24 to 76)
    header_box = [28, 24, width - 28, 76]
    draw.rounded_rectangle(header_box, radius=12, fill=theme["bg_outer"] + (255,), outline=theme["border_dark"], width=2)

    # Header Text
    draw.text((44, 34), "TRAINER CARD", fill=(255, 255, 255, 255), font=font_header_title)
    
    trainer_display_name = first_name if first_name else username
    rank_str = f"{trainer_display_name.upper()}  •  RANK {trainer_level}"
    
    try:
        bbox = font_header_rank.getbbox(rank_str)
        rank_w = bbox[2] - bbox[0]
    except Exception:
        rank_w = 220
    draw.text((width - 44 - rank_w, 38), rank_str, fill=(255, 245, 200, 255), font=font_header_rank)

    # Header Divider Line below header
    draw.line([(28, 86), (width - 28, 86)], fill=theme["border_dark"], width=2)

    # IDNo & Join Date Header line
    id_str = f"IDNo. {user_id}"
    draw.text((36, 96), id_str, fill=text_color, font=font_id)

    # Calculate Exp Next
    exp_per_level = 1000
    exp_next = (trainer_level * exp_per_level) - (trainer_exp % exp_per_level)
    if exp_next <= 0:
        exp_next = 1000

    # Format Join Date
    try:
        if isinstance(joined_at, str):
            dt = datetime.datetime.strptime(joined_at.split(".")[0], "%Y-%m-%d %H:%M:%S")
            date_str = dt.strftime("%b %d, %Y")
        else:
            date_str = joined_at.strftime("%b %d, %Y")
    except Exception:
        date_str = "Nov 06, 2025"

    total_battles = wins + losses
    win_rate = round((wins / total_battles * 100), 1) if total_battles > 0 else 0.0

    labels = [
        ("Exp. Points", f"{trainer_exp:,}"),
        ("To Next Rank", f"{exp_next:,} EXP"),
        ("Battle Record", f"{wins} W  /  {losses} L  ({win_rate}%)"),
        ("Adventure Started", date_str)
    ]

    start_y = 140
    row_h = 52
    for idx, (lbl, val) in enumerate(labels):
        cy = start_y + (idx * row_h)
        # Background pill for readability
        pill_rect = [36, cy - 4, 520, cy + 38]
        draw.rounded_rectangle(pill_rect, radius=8, fill=(255, 255, 255, 140), outline=theme["border_light"], width=1)
        
        draw.text((50, cy + 5), lbl, fill=text_color, font=font_label)
        draw.text((250, cy + 4), val, fill=text_color, font=font_val)

    # Avatar Container Box (Right side: X=540 to 765, Y=96 to 364)
    avatar_rect = [540, 96, 765, 364]
    draw.rounded_rectangle(avatar_rect, radius=16, fill=theme["avatar_bg"] + (255,), outline=theme["border_dark"], width=3)
    draw.rounded_rectangle([avatar_rect[0] + 4, avatar_rect[1] + 4, avatar_rect[2] - 4, avatar_rect[3] - 4], radius=12, fill=None, outline=theme["border_light"], width=2)

    avatar_target = CARD_AVATARS.get(avatar_name, "assets/avatars/captain.png")
    av_box_w = avatar_rect[2] - avatar_rect[0] - 16
    av_box_h = avatar_rect[3] - avatar_rect[1] - 16
    
    if os.path.exists(avatar_target):
        try:
            with Image.open(avatar_target) as av_raw:
                av_img = av_raw.convert("RGBA").resize((av_box_w, av_box_h), Image.Resampling.LANCZOS)
                base_img.paste(av_img, (avatar_rect[0] + 8, avatar_rect[1] + 8), av_img)
        except Exception as e:
            logger.error(f"Error loading local avatar {avatar_target}: {e}")
    else:
        av_img = await _fetch_and_cache_artwork(avatar_target, (av_box_w, av_box_h))
        if av_img:
            av_x = avatar_rect[0] + 8 + (av_box_w - av_img.width) // 2
            av_y = avatar_rect[1] + 8 + (av_box_h - av_img.height) // 2
            base_img.paste(av_img, (av_x, av_y), av_img)

    # Badges Container Bar at Bottom (Y=384 to 492)
    badge_rect = [28, 384, width - 28, 492]
    draw.rounded_rectangle(badge_rect, radius=16, fill=theme["badge_bar"] + (255,), outline=theme["border_dark"], width=3)
    
    draw.text((44, 422), "BADGES", fill=theme["header_text"], font=font_badge_hdr)

    badge_colors = [
        (239, 68, 68), (59, 130, 246), (34, 197, 94), (234, 179, 8),
        (168, 85, 247), (236, 72, 153), (20, 184, 166), (249, 115, 22)
    ]
    bx_start = 180
    b_spacing = 72
    by_center = 438

    for bi in range(8):
        bx = bx_start + (bi * b_spacing)
        is_unlocked = bi < trainer_level
        
        bfill = badge_colors[bi] if is_unlocked else (140, 140, 140)
        outline_c = (255, 215, 0) if is_unlocked else (90, 90, 90)
        
        draw.ellipse([bx - 22, by_center - 22, bx + 22, by_center + 22], fill=bfill, outline=outline_c, width=3)
        if is_unlocked:
            draw.ellipse([bx - 14, by_center - 14, bx + 4, by_center + 4], fill=(255, 255, 255, 90))
            draw.ellipse([bx - 7, by_center - 7, bx + 7, by_center + 7], fill=(255, 255, 255, 220))
        else:
            draw.ellipse([bx - 5, by_center - 5, bx + 5, by_center + 5], fill=(80, 80, 80))

    buf = io.BytesIO()
    rgb = base_img.convert("RGB")
    rgb.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf
