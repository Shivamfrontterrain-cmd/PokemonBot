import os
import uuid
import random
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.request import HTTPXRequest

from database import (
    init_db,
    get_user,
    get_user_starter,
    register_user_with_starter,
    update_user_region,
    get_or_create_inventory,
    use_pokeball,
    set_active_hunt,
    get_active_hunt,
    clear_active_hunt,
    create_active_battle,
    get_active_battle,
    update_active_battle,
    end_active_battle,
    add_caught_pokemon,
    has_user_caught_pokemon,
    get_user_starter,
    get_user_team,
    update_user_pokemon_hp,
    switch_active_battle_pokemon,
    add_user_pokedollars,
    get_user_pokedollars,
    get_user_full_stats,
    update_user_card_settings,
    record_user_win,
    record_user_loss,
)
from pokeapi import (
    fetch_pokemon_data,
    fetch_random_wild_pokemon,
    get_starter_info,
    get_pokemon_moves,
)
from card_generator import (
    generate_starter_card,
    generate_wild_card,
    generate_battle_card,
    generate_battle_outcome_card,
    generate_catch_card,
    generate_catch_menu_card,
    generate_switch_pokemon_card,
    generate_inventory_card,
    generate_region_card,
    generate_trainer_card,
    CARD_THEMES,
    CARD_TEXT_COLORS,
    CARD_AVATARS,
    preload_artwork_cache,
)
from regions import get_all_regions, get_region_info
from battle_engine import (
    calculate_damage,
    calculate_catch_success,
    BALL_NAMES,
    get_type_effectiveness,
    get_move_effectiveness_badge,
)
from iv_ev_system import generate_ivs, get_iv_grade, get_nature_info
from tm_database import get_tm_info

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "hexamonbot.db")


def render_vibrant_hp_bar(current_hp: int, max_hp: int) -> str:
    """Renders a clean HP progress bar (Green > 50%, Yellow 20-50%, Red < 20%)."""
    pct = max(0.0, min(1.0, current_hp / max(1, max_hp)))
    filled = int(round(pct * 8))
    
    if pct > 0.5:
        icon = "💚"
        fill_char = "🟩"
    elif pct > 0.2:
        icon = "💛"
        fill_char = "🟨"
    else:
        icon = "🔴"
        fill_char = "🟥"

    bar = fill_char * filled + "⬜" * (8 - filled)
    return f"{icon} `[{bar}]` `{current_hp}/{max_hp} HP`"


async def post_init(application: Application) -> None:
    """Initialize database tables and pre-warm RAM artwork cache on bot startup."""
    await init_db(DB_PATH)
    logger.info("Database initialized successfully.")
    asyncio.create_task(preload_artwork_cache())
    logger.info("RAM Artwork cache pre-warming started in background.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    if not user or not update.message:
        return

    user_id = user.id
    first_name = user.first_name or "Trainer"

    existing_user = await get_user(user_id, DB_PATH)
    if existing_user and existing_user.get("starter_chosen") == 1:
        starter = await get_user_starter(user_id, DB_PATH)
        inv = await get_or_create_inventory(user_id, DB_PATH)

        if starter:
            pokemon_data = {
                "name": starter["name"],
                "types": ["Starter"],
                "stats": {
                    "hp": starter["hp"],
                    "attack": starter["attack"],
                    "defense": starter["defense"],
                    "special-attack": starter["sp_attack"],
                    "special-defense": starter["sp_defense"],
                    "speed": starter["speed"],
                },
                "image_url": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{starter['pokemon_id']}.png"
            }

            card_buf = await generate_starter_card(first_name, pokemon_data)
            current_region = existing_user.get("current_region", "Kanto")
            trainer_lvl = existing_user.get("trainer_level", 1)
            hp_bar = render_vibrant_hp_bar(starter["hp"], starter["max_hp"])
            iv_pct = starter.get("iv_total_pct", 80.6)
            iv_grade = get_iv_grade(iv_pct)

            nature_str = starter.get("nature", "Hardy")
            nature_desc = get_nature_info(nature_str)["desc"]

            caption = (
                f"╭──────────────────────────────╮\n"
                f"│  🌟 **TRAINER CARD & PROFILE** 🌟  │\n"
                f"╰──────────────────────────────╯\n\n"
                f"👤 **Trainer**: `{first_name}`\n"
                f"🎖️ **Level**: `{trainer_lvl}/10`\n"
                f"📍 **Active Region**: `{current_region}`\n\n"
                f"🔰 **Active Partner**: `{starter['name']}` (Level {starter['level']})\n"
                f"HP: {hp_bar}\n"
                f"🧬 **Nature**: `{nature_str} ({nature_desc})`\n"
                f"📊 **IV Quality**: `{iv_pct}% ({iv_grade})`\n"
                f"⚔️ **Attack**: `{starter['attack']}`  │  🛡️ **Defense**: `{starter['defense']}`\n"
                f"⚡ **Speed**: `{starter['speed']}`\n\n"
                f"🎒 **Inventory**:\n"
                f"• Poké Balls: `{inv['pokeball']}`\n"
                f"• Great Balls: `{inv['greatball']}`\n\n"
                f"💡 *Use /hunt to battle wild Pokémon or /travel to explore!*"
            )

            await update.message.reply_photo(
                photo=card_buf,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )
            return

    keyboard = [
        [InlineKeyboardButton("Bulbasaur   │  Grass • Poison", callback_data="select_starter:1")],
        [InlineKeyboardButton("Charmander  │  Fire", callback_data="select_starter:4")],
        [InlineKeyboardButton("Squirtle    │  Water", callback_data="select_starter:7")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"╭──────────────────────────────╮\n"
        f"│  🌿 **WELCOME TO HEXAMON** 🌿   │\n"
        f"╰──────────────────────────────╯\n\n"
        f"Greetings **{first_name}**! I am **Professor Oak**.\n\n"
        f"Welcome to the Pokémon world! Before embarking on your adventure, "
        f"choose your very first partner Pokémon below:\n\n"
        f"🎒 *(New trainers receive 10x Poké Balls & 5x Great Balls!)*"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


async def select_starter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle starter selection callback query."""
    query = update.callback_query
    if not query or not query.message:
        return

    user = query.from_user
    user_id = user.id
    username = user.username
    first_name = user.first_name or "Trainer"

    data = query.data
    if not data or not data.startswith("select_starter:"):
        return

    pokemon_id = int(data.split(":")[1])

    existing_user = await get_user(user_id, DB_PATH)
    if existing_user and existing_user.get("starter_chosen") == 1:
        await query.answer("⚠️ You have already chosen your starter Pokémon!", show_alert=True)
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    try:
        pokemon_data = await fetch_pokemon_data(pokemon_id)
        pokemon_data["ivs"] = generate_ivs("Rare")
        pokemon_data["rarity"] = "Starter"
    except Exception as e:
        logger.error(f"Error fetching Pokémon data: {e}")
        await query.answer("⚠️ Failed to load Pokémon data. Please try again.", show_alert=True)
        return

    success, msg = await register_user_with_starter(user_id, username, first_name, pokemon_data, DB_PATH)

    if not success:
        await query.answer(f"⚠️ {msg}", show_alert=True)
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    await query.answer("Starter chosen successfully!")

    try:
        await query.message.delete()
    except Exception:
        pass

    card_buf = await generate_starter_card(first_name, pokemon_data)
    types_str = " • ".join(pokemon_data["types"])
    stats = pokemon_data["stats"]
    ivs = pokemon_data["ivs"]

    nature_str = pokemon_data.get("nature", "Hardy")
    nature_desc = get_nature_info(nature_str)["desc"]

    caption = (
        f"╭──────────────────────────────╮\n"
        f"│  🎉 **STARTER PARTNER CHOSEN** 🎉 │\n"
        f"╰──────────────────────────────╯\n\n"
        f"Congratulations **{first_name}**! You partnered with **{pokemon_data['name']}**!\n\n"
        f"🏷️ **Type**: `{types_str}`  │  ⭐ **Level**: `5`\n"
        f"🧬 **Nature**: `{nature_str} ({nature_desc})`\n"
        f"📊 **IV Quality**: `{ivs['total_pct']}% ({ivs['grade']})`\n"
        f"📊 **Base Stats**:\n"
        f"• ❤️ HP: `{stats['hp']}`  │  ⚔️ Attack: `{stats['attack']}`\n"
        f"• 🛡️ Defense: `{stats['defense']}`  │  ⚡ Speed: `{stats['speed']}`\n\n"
        f"🎒 Received: **10x Poké Balls** & **5x Great Balls**!\n\n"
        f"🚀 **Use /hunt to search for wild Pokémon or /travel to explore!**"
    )

    await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=card_buf,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN
    )


def _build_travel_keyboard() -> InlineKeyboardMarkup:
    """Build clean 4-row grid keyboard for region travel without emojis."""
    keyboard = [
        [
            InlineKeyboardButton("Kanto", callback_data="travel:Kanto"),
            InlineKeyboardButton("Johto", callback_data="travel:Johto")
        ],
        [
            InlineKeyboardButton("Hoenn", callback_data="travel:Hoenn"),
            InlineKeyboardButton("Sinnoh", callback_data="travel:Sinnoh")
        ],
        [
            InlineKeyboardButton("Unova", callback_data="travel:Unova"),
            InlineKeyboardButton("Kalos", callback_data="travel:Kalos")
        ],
        [
            InlineKeyboardButton("Alola", callback_data="travel:Alola"),
            InlineKeyboardButton("Galar", callback_data="travel:Galar"),
            InlineKeyboardButton("Paldea", callback_data="travel:Paldea")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def travel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /travel command with custom region map graphic card and clean grid layout."""
    user = update.effective_user
    if not user or not update.message:
        return

    user_id = user.id
    existing_user = await get_user(user_id, DB_PATH)
    if not existing_user or existing_user.get("starter_chosen") != 1:
        await update.message.reply_text("⚠️ Please pick your starter Pokémon first using /start!")
        return

    current_region = existing_user.get("current_region", "Kanto")
    user_level = existing_user.get("trainer_level", 1)

    reply_markup = _build_travel_keyboard()
    card_buf = await generate_region_card(current_region, user_level)

    caption = (
        f"╭──────────────────────────────╮\n"
        f"│  ✈️ **WORLD TRAVEL HUB** ✈️      │\n"
        f"╰──────────────────────────────╯\n\n"
        f"📍 **Current Region**: `{current_region}`\n"
        f"🎖️ **Trainer Level**: `Lvl {user_level}`\n\n"
        f"Select a destination region below to travel:"
    )

    await update.message.reply_photo(
        photo=card_buf,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


def _build_inventory_keyboard(active_cat: str = "pokedollars") -> InlineKeyboardMarkup:
    """Helper to build category tab buttons for inventory navigation."""
    cat_rows = [
        [("pokedollars", "💰 Wallet"), ("balls", "🔴 Pokéballs"), ("candies", "🍬 Candies")],
        [("tms", "💿 TMs"), ("stones", "💎 Stones"), ("eggs", "🥚 Eggs")],
        [("orbs", "🔮 Orbs"), ("crystals", "✨ Crystals"), ("tutors", "📜 Tutors")]
    ]

    keyboard = []
    for row_defs in cat_rows:
        btn_row = []
        for cat_id, label in row_defs:
            if cat_id == active_cat:
                btn_row.append(InlineKeyboardButton(f"• {label} •", callback_data="noop"))
            else:
                btn_row.append(InlineKeyboardButton(label, callback_data=f"inv_cat:{cat_id}"))
        keyboard.append(btn_row)

    return InlineKeyboardMarkup(keyboard)


def _build_inventory_caption(inv: Dict[str, Any], category: str = "pokedollars") -> str:
    """Helper to generate category-specific markdown captions."""
    from card_generator import ITEM_DESCRIPTIONS

    if category == "balls":
        balls_data = [
            ("🔴 **Poké Ball** (1.0x)", inv.get("pokeball", 10)),
            ("🔵 **Great Ball** (1.5x)", inv.get("greatball", 5)),
            ("🟡 **Ultra Ball** (2.0x)", inv.get("ultraball", 0)),
            ("🟣 **Master Ball** (255x)", inv.get("masterball", 0)),
        ]
        owned = [f"• {name}: `{cnt}`" for name, cnt in balls_data if cnt > 0]
        items_str = "\n".join(owned) if owned else "_No Pokéballs in inventory._"

        return (
            f"╭──────────────────────────────╮\n"
            f"│  🔴 **POKÉBALL POUCH** 🔴        │\n"
            f"╰──────────────────────────────╯\n\n"
            f"{items_str}"
        )
    elif category == "candies":
        candies_data = [
            ("👑 **Rare Candy** (+1 Lvl)", inv.get("rare_candy", 0)),
            ("🍬 **EXP Candy (S)** (+100 EXP)", inv.get("exp_candy_s", 0)),
            ("🍬 **EXP Candy (M)** (+500 EXP)", inv.get("exp_candy_m", 0)),
            ("🍬 **EXP Candy (L)** (+2000 EXP)", inv.get("exp_candy_l", 0)),
        ]
        owned = [f"• {name}: `{cnt}`" for name, cnt in candies_data if cnt > 0]
        items_str = "\n".join(owned) if owned else "_No Candies in inventory._"

        return (
            f"╭──────────────────────────────╮\n"
            f"│  🍬 **CANDY POUCH** 🍬         │\n"
            f"╰──────────────────────────────╯\n\n"
            f"{items_str}"
        )
    elif category == "tms":
        user_tms = inv.get("tms", {})
        owned = []
        for tmid, cnt in user_tms.items():
            if cnt > 0:
                tinfo = get_tm_info(tmid)
                owned.append(f"• **{tinfo['name']}** ({tinfo['type']}): `{cnt}`")
        items_str = "\n".join(owned) if owned else "_No TMs in TM Case._"

        return (
            f"╭──────────────────────────────╮\n"
            f"│  💿 **TECHNICAL MACHINES** 💿  │\n"
            f"╰──────────────────────────────╯\n\n"
            f"{items_str}"
        )
    elif category in ["stones", "eggs", "orbs", "crystals", "tutors"]:
        headers = {
            "stones": ("💎", "EVOLUTION & MEGA STONES"),
            "eggs": ("🥚", "POKÉMON EGGS & INCUBATORS"),
            "orbs": ("🔮", "LEGENDARY & BATTLE ORBS"),
            "crystals": ("✨", "Z-CRYSTALS & TERA CRYSTALS"),
            "tutors": ("📜", "MOVE TUTORS & SCROLLS"),
        }
        icon, title = headers.get(category, ("🎒", "ITEMS"))
        cat_items = inv.get(category, {})
        owned = []
        for name, cnt in cat_items.items():
            if cnt > 0:
                desc = ITEM_DESCRIPTIONS.get(name, "")
                owned.append(f"• **{name}**: `{cnt}`\n  └ _{desc}_")
        items_str = "\n".join(owned) if owned else f"_No items in {category.title()} pouch._"

        return (
            f"╭──────────────────────────────╮\n"
            f"│  {icon} **{title}** {icon}  │\n"
            f"╰──────────────────────────────╯\n\n"
            f"{items_str}"
        )
    else:
        pd = inv.get("pokedollars", 0)
        return (
            f"╭──────────────────────────────╮\n"
            f"│  💰 **POKÉDOLLAR WALLET** 💰    │\n"
            f"╰──────────────────────────────╯\n\n"
            f"💰 **Total Balance**: `{pd} PD`"
        )


async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View trainer's inventory with category navigation tabs."""
    user = update.effective_user
    if not user or not update.message:
        return

    inv = await get_or_create_inventory(user.id, DB_PATH)
    card_buf = await generate_inventory_card(user.first_name or "Trainer", inv, category="pokedollars")
    caption = _build_inventory_caption(inv, category="pokedollars")
    reply_markup = _build_inventory_keyboard(active_cat="pokedollars")

    await update.message.reply_photo(
        photo=card_buf,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def inventory_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch inventory category graphic card and caption dynamically."""
    query = update.callback_query
    if not query or not query.message:
        return

    user = query.from_user
    user_id = user.id
    data = query.data
    if not data or not data.startswith("inv_cat:"):
        return

    cat_id = data.split(":")[1]
    inv = await get_or_create_inventory(user_id, DB_PATH)

    card_buf = await generate_inventory_card(user.first_name or "Trainer", inv, category=cat_id)
    caption = _build_inventory_caption(inv, category=cat_id)
    reply_markup = _build_inventory_keyboard(active_cat=cat_id)

    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=card_buf, caption=caption, parse_mode=ParseMode.MARKDOWN),
            reply_markup=reply_markup
        )
        await query.answer()
    except Exception as e:
        logger.error(f"Error updating inventory view: {e}")
        await query.answer()


def _build_trainer_card_main_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Main keyboard with More Stats and Edit Profile buttons."""
    keyboard = [
        [
            InlineKeyboardButton("More Stats", callback_data=f"mystats_more:{user_id}"),
            InlineKeyboardButton("Edit Profile", callback_data=f"mystats_edit:{user_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_trainer_card_edit_keyboard(user_id: int, theme: str, color: str, avatar: str) -> InlineKeyboardMarkup:
    """Edit Profile sub-menu keyboard with customization options and Back button."""
    keyboard = [
        [
            InlineKeyboardButton(f"🎨 Theme: {theme}", callback_data=f"card_theme:{user_id}"),
            InlineKeyboardButton(f"✏️ Text: {color}", callback_data=f"card_color:{user_id}")
        ],
        [
            InlineKeyboardButton(f"👤 Avatar: {avatar}", callback_data=f"card_avatar:{user_id}")
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data=f"mystats_back:{user_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mystats command to show user profile & customizable Trainer Card with NO text caption."""
    user = update.effective_user
    if not user or not update.message:
        return

    user_id = user.id
    user_stats = await get_user_full_stats(user_id, DB_PATH)
    if not user_stats or user_stats.get("starter_chosen") != 1:
        await update.message.reply_text("⚠️ Please pick your starter Pokémon first using /start!")
        return

    theme = user_stats.get("card_theme", "Classic Red")
    color = user_stats.get("card_text_color", "Classic Dark")
    avatar = user_stats.get("card_avatar", "Captain Trainer")

    card_buf = await generate_trainer_card(
        user_id=user_id,
        username=user_stats.get("username", user.username or "Trainer"),
        first_name=user_stats.get("first_name", user.first_name or "Trainer"),
        trainer_level=user_stats.get("trainer_level", 1),
        trainer_exp=user_stats.get("trainer_exp", 0),
        wins=user_stats.get("wins", 0),
        losses=user_stats.get("losses", 0),
        joined_at=str(user_stats.get("joined_at", "2025-11-06 12:00:00")),
        theme_name=theme,
        text_color_name=color,
        avatar_name=avatar
    )

    reply_markup = _build_trainer_card_main_keyboard(user_id)

    # Clean card display: NO text caption!
    await update.message.reply_photo(
        photo=card_buf,
        caption="",
        reply_markup=reply_markup
    )


async def card_customization_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle interaction for More Stats, Edit Profile, Theme/Color/Avatar changes, and Back button."""
    query = update.callback_query
    if not query or not query.message:
        return

    user = query.from_user
    if not user:
        return

    data = query.data or ""
    parts = data.split(":")
    action = parts[0]
    target_user_id = int(parts[1]) if len(parts) > 1 else 0

    if user.id != target_user_id:
        await query.answer("❌ This is not your Trainer Card!", show_alert=True)
        return

    user_stats = await get_user_full_stats(user.id, DB_PATH)
    if not user_stats:
        await query.answer("User stats not found.", show_alert=True)
        return

    current_theme = user_stats.get("card_theme", "Classic Red")
    current_color = user_stats.get("card_text_color", "Classic Dark")
    current_avatar = user_stats.get("card_avatar", "Captain Trainer")

    if action == "mystats_more":
        pd = user_stats.get("pokedollars", 0)
        wins = user_stats.get("wins", 0)
        losses = user_stats.get("losses", 0)
        total_battles = wins + losses
        win_rate = round((wins / total_battles * 100), 1) if total_battles > 0 else 0.0
        region = user_stats.get("current_region", "Kanto")
        total_pokes = user_stats.get("total_pokemon", 0)

        stats_popup = (
            f"📊 Trainer Stats Breakdown ({user.first_name}):\n"
            f"• Current Region: {region}\n"
            f"• Pokédollars: {pd:,} PD\n"
            f"• Pokémon Caught: {total_pokes}\n"
            f"• Total Battles: {total_battles}\n"
            f"• Win Rate: {win_rate}%\n"
            f"• Card Theme: {current_theme}"
        )
        await query.answer(stats_popup, show_alert=True)
        return

    elif action == "mystats_edit":
        reply_markup = _build_trainer_card_edit_keyboard(user.id, current_theme, current_color, current_avatar)
        try:
            await query.message.edit_reply_markup(reply_markup=reply_markup)
        except Exception:
            pass
        await query.answer("✏️ Edit Profile Mode: Cycle options below!")
        return

    elif action == "mystats_back":
        reply_markup = _build_trainer_card_main_keyboard(user.id)
        try:
            await query.message.edit_reply_markup(reply_markup=reply_markup)
        except Exception:
            pass
        await query.answer()
        return

    themes_list = list(CARD_THEMES.keys())
    colors_list = list(CARD_TEXT_COLORS.keys())
    avatars_list = list(CARD_AVATARS.keys())

    if action == "card_theme":
        idx = themes_list.index(current_theme) if current_theme in themes_list else 0
        new_theme = themes_list[(idx + 1) % len(themes_list)]
        await update_user_card_settings(user.id, card_theme=new_theme, db_path=DB_PATH)
        current_theme = new_theme
        await query.answer(f"🎨 Theme: {new_theme}")

    elif action == "card_color":
        idx = colors_list.index(current_color) if current_color in colors_list else 0
        new_color = colors_list[(idx + 1) % len(colors_list)]
        await update_user_card_settings(user.id, card_text_color=new_color, db_path=DB_PATH)
        current_color = new_color
        await query.answer(f"✏️ Text: {new_color}")

    elif action == "card_avatar":
        idx = avatars_list.index(current_avatar) if current_avatar in avatars_list else 0
        new_avatar = avatars_list[(idx + 1) % len(avatars_list)]
        await update_user_card_settings(user.id, card_avatar=new_avatar, db_path=DB_PATH)
        current_avatar = new_avatar
        await query.answer(f"👤 Avatar: {new_avatar}")

    # Regenerate Card Image and edit photo with NO text caption
    card_buf = await generate_trainer_card(
        user_id=user.id,
        username=user_stats.get("username", user.username or "Trainer"),
        first_name=user_stats.get("first_name", user.first_name or "Trainer"),
        trainer_level=user_stats.get("trainer_level", 1),
        trainer_exp=user_stats.get("trainer_exp", 0),
        wins=user_stats.get("wins", 0),
        losses=user_stats.get("losses", 0),
        joined_at=str(user_stats.get("joined_at", "2025-11-06 12:00:00")),
        theme_name=current_theme,
        text_color_name=current_color,
        avatar_name=current_avatar
    )

    reply_markup = _build_trainer_card_edit_keyboard(user.id, current_theme, current_color, current_avatar)

    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=card_buf, caption=""),
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error updating trainer card media: {e}")


async def travel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle travel destination selection callback."""
    query = update.callback_query
    if not query or not query.message:
        return

    user = query.from_user
    user_id = user.id
    data = query.data
    if not data or not data.startswith("travel:"):
        return

    target_region = data.split(":")[1]
    existing_user = await get_user(user_id, DB_PATH)
    if not existing_user:
        await query.answer("⚠️ User not found. Please /start first.", show_alert=True)
        return

    user_level = existing_user.get("trainer_level", 1)
    current_region = existing_user.get("current_region", "Kanto")
    rinfo = get_region_info(target_region)
    req_level = rinfo["req_level"]

    # 1. Requirement Check: Pop-up alert if unfulfilled!
    if user_level < req_level:
        await query.answer(
            f"🔒 Level Requirement Unfulfilled!\n\n"
            f"You must reach Trainer Level {req_level} to unlock {target_region}.\n"
            f"(Your Level: Lvl {user_level})",
            show_alert=True
        )
        return

    # 2. Already in region check
    if current_region == target_region:
        await query.answer(f"📍 You are already in {target_region}!", show_alert=True)
        return

    # 3. Direct Travel if requirements met
    await update_user_region(user_id, target_region, DB_PATH)
    await query.answer(f"✈️ Traveled to {target_region}!")

    card_buf = await generate_region_card(target_region, user_level)
    reply_markup = _build_travel_keyboard()

    caption = (
        f"╭──────────────────────────────╮\n"
        f"│  ✈️ **WORLD TRAVEL HUB** ✈️      │\n"
        f"╰──────────────────────────────╯\n\n"
        f"📍 **Current Region**: `{target_region}`\n"
        f"🎖️ **Trainer Level**: `Lvl {user_level}`\n\n"
        f"Select a destination region below to travel:"
    )

    try:
        media = InputMediaPhoto(media=card_buf, caption=caption, parse_mode=ParseMode.MARKDOWN)
        await query.message.edit_media(media=media, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error editing travel media: {e}")
        try:
            await query.message.edit_caption(caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass


async def hunt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /hunt command spawning a wild Pokémon encounter with rarity tier & IV generation."""
    user = update.effective_user
    if not user or not update.message:
        return

    user_id = user.id
    existing_user = await get_user(user_id, DB_PATH)
    if not existing_user or existing_user.get("starter_chosen") != 1:
        await update.message.reply_text("⚠️ Please pick your starter Pokémon first using /start!")
        return

    active_battle = await get_active_battle(user_id, DB_PATH)
    if active_battle and not active_battle.get("expired"):
        already_caught = await has_user_caught_pokemon(user_id, active_battle["wild_id"], DB_PATH)
        star_icon = "★ " if already_caught else ""
        await update.message.reply_text(
            f"⚔️ **BATTLE IN PROGRESS!**\n\n"
            f"You are currently battling wild **{star_icon}{active_battle['wild_name']}** (Lvl {active_battle['wild_level']})!\n"
            f"You must finish or run away from your current battle before hunting again.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    current_region = existing_user.get("current_region", "Kanto")
    first_name = user.first_name or "Trainer"

    try:
        pokemon_data = await fetch_random_wild_pokemon(current_region)
    except Exception as e:
        logger.error(f"Error generating wild encounter: {e}")
        await update.message.reply_text("⚠️ Failed to generate wild encounter. Please try again!")
        return

    card_buf = await generate_wild_card(first_name, pokemon_data)

    types_str = " • ".join(pokemon_data["types"])
    wild_lvl = pokemon_data["wild_level"]
    poke_id = pokemon_data["id"]
    rarity = pokemon_data.get("rarity", "Common")

    # Check if user has already caught this species before
    already_caught = await has_user_caught_pokemon(user_id, poke_id, DB_PATH)
    star_icon = "★ " if already_caught else ""

    # Select header title based on Rarity Tier
    if rarity == "Legendary":
        header_badge = "👑 **LEGENDARY ENCOUNTER** 👑"
        rarity_str = "👑 **Legendary**"
    elif rarity == "Rare":
        header_badge = "✨ **RARE ENCOUNTER** ✨"
        rarity_str = "✨ **Rare**"
    elif rarity == "Uncommon":
        header_badge = "⭐ **UNCOMMON ENCOUNTER** ⭐"
        rarity_str = "⭐ **Uncommon**"
    else:
        header_badge = "🌿 **WILD POKÉMON SPOTTED** 🌿"
        rarity_str = "🌿 **Common**"

    # Generate unique hunt token to invalidate older /hunt cards
    hunt_token = str(uuid.uuid4())[:8]
    await set_active_hunt(user_id, hunt_token, poke_id, wild_lvl, DB_PATH)

    keyboard = [
        [
            InlineKeyboardButton("Battle", callback_data=f"battle:{poke_id}:{wild_lvl}:{hunt_token}"),
            InlineKeyboardButton("EV Yields", callback_data=f"ev_yields:{poke_id}:{hunt_token}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    rinfo = get_region_info(current_region)

    nature_str = pokemon_data.get("nature", "Hardy")
    nature_desc = get_nature_info(nature_str)["desc"]

    # 1-in-250 rare TM drop chance during hunt (random TM from TM01 to TM100)
    tm_drop_text = ""
    if random.randint(1, 250) == 1:
        dropped_tm_num = random.randint(1, 100)
        tm_id = f"TM{dropped_tm_num:02d}"
        tm_info = get_tm_info(tm_id)
        await add_user_tm(user_id, tm_id, quantity=1, db_path=DB_PATH)
        tm_drop_text = f"\n\n🎉 **RARE FIND!** You found a rare **{tm_info['name']}** ({tm_info['type']}) during your hunt!"

    caption = (
        f"╭──────────────────────────────╮\n"
        f"│  {header_badge}  │\n"
        f"╰──────────────────────────────╯\n\n"
        f"A wild **{star_icon}{pokemon_data['name']}** appeared in **{rinfo['emoji']} {current_region}**!\n\n"
        f"🏷️ **Type**: `{types_str}`  │  ⭐ **Level**: `Lvl {wild_lvl}`\n"
        f"🧬 **Nature**: `{nature_str} ({nature_desc})`\n"
        f"📊 **Rarity**: {rarity_str}{tm_drop_text}\n\n"
        f"What will you do, **{first_name}**?"
    )

    await update.message.reply_photo(
        photo=card_buf,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def ev_yields_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle EV Yields button click displaying EV effort points awarded on defeat."""
    query = update.callback_query
    if not query:
        return

    user_id = query.from_user.id
    data = query.data
    if not data or not data.startswith("ev_yields:"):
        return

    parts = data.split(":")
    poke_id = int(parts[1])
    token = parts[2] if len(parts) > 2 else ""

    active_hunt = await get_active_hunt(user_id, DB_PATH)
    if not active_hunt or active_hunt["hunt_token"] != token:
        await query.answer("💨 This Pokémon has already fled!", show_alert=True)
        try:
            await query.message.edit_caption(caption="💨 This wild Pokémon ran away!", reply_markup=None)
        except Exception:
            pass
        return

    try:
        poke_data = await fetch_pokemon_data(poke_id)
        evs = poke_data.get("ev_yields", {"Exp": 1})
        ev_str = ", ".join([f"+{val} {stat}" for stat, val in evs.items()])
    except Exception:
        ev_str = "+1 Speed EV"

    await query.answer(f"📊 EV Yields on defeat:\n{ev_str}", show_alert=True)


async def start_battle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Initiate turn-based combat against wild Pokémon with stale hunt verification."""
    query = update.callback_query
    if not query or not query.message:
        return

    user = query.from_user
    user_id = user.id
    active_battle = await get_active_battle(user_id, DB_PATH)
    if active_battle:
        await query.answer("⚔️ You are already in an active battle!", show_alert=True)
        return

    data = query.data
    if not data or not data.startswith("battle:"):
        return

    parts = data.split(":")
    wild_id = int(parts[1])
    wild_lvl = int(parts[2])
    token = parts[3] if len(parts) > 3 else ""

    # Check if this hunt encounter is still valid
    active_hunt = await get_active_hunt(user_id, DB_PATH)
    if not active_hunt or active_hunt["hunt_token"] != token:
        await query.answer("💨 This Pokémon has already fled!", show_alert=True)
        try:
            await query.message.edit_caption(caption="💨 This wild Pokémon ran away!", reply_markup=None)
        except Exception:
            pass
        return

    player_starter = await get_user_starter(user_id, DB_PATH)
    if not player_starter:
        await query.answer("⚠️ You don't have an active Pokémon! Use /start.", show_alert=True)
        return

    wild_data = await fetch_pokemon_data(wild_id)
    wild_data["wild_level"] = wild_lvl
    wild_data["ivs"] = generate_ivs(wild_data.get("rarity", "Common"))

    # Clear active hunt record now that battle is engaged
    await clear_active_hunt(user_id, DB_PATH)

    await create_active_battle(user_id, wild_data, player_starter, DB_PATH)
    await get_or_create_inventory(user_id, DB_PATH)

    await query.answer("Battle Started!")
    await render_battle_screen(query, user_id)


async def _handle_expired_battle(query, battle: Dict[str, Any]) -> bool:
    """Helper to check if a battle expired due to 2min inactivity and display fled card/caption."""
    if not battle or not battle.get("expired"):
        return False

    wild_name = battle.get("wild_name", "Wild Pokémon")
    if query:
        try:
            await query.answer("⚠️ The wild Pokémon got tired of waiting and fled! Battle ended.", show_alert=True)
        except Exception:
            pass

        fled_text = (
            f"╭──────────────────────────────╮\n"
            f"│  💨 **WILD POKÉMON FLED** 💨      │\n"
            f"╰──────────────────────────────╯\n\n"
            f"The wild **{wild_name}** got tired of waiting for your move and fled into the tall grass!\n\n"
            f"⏱️ *Battle ended after 2 minutes of inactivity. You gained no items or EXP.*\n\n"
            f"🌿 Use /hunt to find another wild Pokémon!"
        )
        try:
            await query.message.edit_caption(caption=fled_text, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            try:
                await query.message.edit_text(fled_text, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                await query.message.reply_text(fled_text, parse_mode=ParseMode.MARKDOWN)

    return True


async def render_battle_screen(query, user_id: int, status_text: str = "") -> None:
    """Renders updated turn-based battle screen and updates the message photo media IN-PLACE."""
    battle = await get_active_battle(user_id, DB_PATH)
    if not battle:
        try:
            await query.message.edit_caption(caption="Battle concluded.")
        except Exception:
            pass
        return

    if await _handle_expired_battle(query, battle):
        return

    player_starter = await get_user_starter(user_id, DB_PATH)
    active_poke_id = battle.get("player_pokemon_id") or (player_starter['pokemon_id'] if player_starter else 1)
    p_img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{active_poke_id}.png"
    w_img_url = battle.get("wild_image_url", "")

    w_nature = battle.get("wild_nature", "Hardy")
    p_nature = battle.get("player_nature", "Hardy")
    turn_num = battle.get("turn_number", 1)
    turn_owner = battle.get("turn_owner", "player")

    card_buf = await generate_battle_card(
        player_name=battle["player_name"],
        player_level=battle["player_level"],
        player_hp=battle["player_hp"],
        player_max_hp=battle["player_max_hp"],
        player_nature=p_nature,
        player_image_url=p_img_url,
        wild_name=battle["wild_name"],
        wild_level=battle["wild_level"],
        wild_hp=battle["wild_hp"],
        wild_max_hp=battle["wild_max_hp"],
        wild_nature=w_nature,
        wild_image_url=w_img_url,
        turn_number=turn_num,
        turn_owner=turn_owner,
        status_text=status_text
    )

    already_caught = await has_user_caught_pokemon(user_id, battle["wild_id"], DB_PATH)
    star_icon = "★ " if already_caught else ""

    if turn_owner == "player":
        header_text = f"⚔️ **BATTLE ARENA**  •  **TURN {turn_num}**"
        sub_text = "Select your attack move or action below:"
    else:
        header_text = f"👾 **WILD TURN**  •  **TURN {turn_num}**"
        sub_text = f"Wild **{star_icon}{battle['wild_name']}** is taking its turn..."

    caption = (
        f"╭──────────────────────────────╮\n"
        f"│  {header_text}  │\n"
        f"╰──────────────────────────────╯\n\n"
        f"{sub_text}"
    )

    keyboard = []

    wild_data = await fetch_pokemon_data(battle["wild_id"])
    wild_types = wild_data.get("types", ["Normal"])

    if turn_owner == "player":
        active_poke_id = battle.get("player_pokemon_id") or 1
        active_poke_data = await fetch_pokemon_data(active_poke_id)
        player_moves = get_pokemon_moves(active_poke_data.get("types", ["Normal"]))

        m_buttons = []
        for idx, move in enumerate(player_moves):
            badge = get_move_effectiveness_badge(move["type"], wild_types)
            badge_str = f" [{badge}]" if badge else ""
            m_buttons.append(InlineKeyboardButton(f"{move['name']}{badge_str}", callback_data=f"use_move:{idx}"))

        keyboard.append([m_buttons[0], m_buttons[1]])
        if len(m_buttons) > 2:
            keyboard.append([m_buttons[2], m_buttons[3]])

        keyboard.append([
            InlineKeyboardButton("Catch", callback_data="catch_menu"),
            InlineKeyboardButton("🔄 Switch", callback_data="switch_pokemon_menu"),
            InlineKeyboardButton("Run", callback_data="run_battle")
        ])
    else:
        wild_moves = get_pokemon_moves(wild_types)

        w_buttons = []
        for move in wild_moves:
            w_buttons.append(InlineKeyboardButton(f"Wild {move['name']}", callback_data="auto_wild_turn"))

        keyboard.append([w_buttons[0], w_buttons[1]])
        if len(w_buttons) > 2:
            keyboard.append([w_buttons[2], w_buttons[3]])

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        media = InputMediaPhoto(media=card_buf, caption=caption, parse_mode=ParseMode.MARKDOWN)
        await query.message.edit_media(media=media, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error editing message media: {e}")
        try:
            await query.message.edit_caption(caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass


async def use_move_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Player's Move Execution -> Automatic Wild Turn."""
    query = update.callback_query
    if not query or not query.message:
        return

    user = query.from_user
    user_id = user.id
    data = query.data
    if not data or not data.startswith("use_move:"):
        return

    move_idx = int(data.split(":")[1])
    battle = await get_active_battle(user_id, DB_PATH)
    if await _handle_expired_battle(query, battle):
        return

    if not battle or battle.get("turn_owner") != "player":
        await query.answer("⚠️ Not your turn!", show_alert=True)
        return

    already_caught = await has_user_caught_pokemon(user_id, battle["wild_id"], DB_PATH)
    star_icon = "★ " if already_caught else ""

    active_poke_id = battle.get("player_pokemon_id") or 1
    active_poke_data = await fetch_pokemon_data(active_poke_id)
    wild_data = await fetch_pokemon_data(battle["wild_id"])
    wild_types = wild_data.get("types", ["Normal"])
    player_types = active_poke_data.get("types", ["Normal"])

    player_moves = get_pokemon_moves(player_types)
    player_move = player_moves[min(move_idx, len(player_moves) - 1)]

    # 1. Execute Player Attack with Type Effectiveness
    p_mult, p_eff_text = get_type_effectiveness(player_move["type"], wild_types)
    player_dmg = calculate_damage(battle["player_level"], player_move["power"], battle["player_attack"], battle["wild_defense"], type_multiplier=p_mult)
    new_wild_hp = max(0, battle["wild_hp"] - player_dmg)

    p_eff_str = f" {p_eff_text}" if p_eff_text else ""
    await query.answer(f"Your {battle['player_name']} used {player_move['name']} for {player_dmg} damage!{p_eff_str}")

    player_starter = await get_user_starter(user_id, DB_PATH)
    p_img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{active_poke_id}.png"
    w_img_url = battle.get("wild_image_url", "")

    # Check if Wild Fainted
    if new_wild_hp <= 0:
        await end_active_battle(user_id, DB_PATH)
        await record_user_win(user_id, exp_gained=50, db_path=DB_PATH)
        earned_pd = random.randint(1, 10)
        new_balance = await add_user_pokedollars(user_id, earned_pd, DB_PATH)

        win_card = await generate_battle_outcome_card(
            outcome_type="victory",
            player_name=battle["player_name"],
            player_image_url=p_img_url,
            wild_name=battle["wild_name"],
            wild_image_url=w_img_url,
            status_text=f"Wild {star_icon}{battle['wild_name']} fainted! Earned +{earned_pd} PD!"
        )
        win_caption = (
            f"╭──────────────────────────────╮\n"
            f"│  🎉 **VICTORY IN BATTLE!** 🎉    │\n"
            f"╰──────────────────────────────╯\n\n"
            f"Wild **{star_icon}{battle['wild_name']}** fainted!\n"
            f"Your **{battle['player_name']}** won the battle and earned EXP!\n\n"
            f"💰 **Reward**: `+{earned_pd} Pokédollars (PD)`\n"
            f"💳 **Total Balance**: `{new_balance} PD`"
        )
        try:
            await query.message.edit_media(media=InputMediaPhoto(media=win_card, caption=win_caption, parse_mode=ParseMode.MARKDOWN))
        except Exception:
            pass
        return

    # 2. Switch to Wild's Turn State & Render Screen showing Wild Moves & Status on card
    turn_num = battle.get("turn_number", 1)
    await update_active_battle(user_id, new_wild_hp, battle["player_hp"], turn_num, "wild", DB_PATH)
    status_msg = f"Your {battle['player_name']} used {player_move['name']} for {player_dmg} HP damage!{p_eff_str}"
    await render_battle_screen(query, user_id, status_text=status_msg)

    # 3. Wait 1.5 seconds so user sees Wild's turn & Wild's moves on screen
    await asyncio.sleep(1.5)

    battle_current = await get_active_battle(user_id, DB_PATH)
    if not battle_current or battle_current.get("turn_owner") != "wild":
        return
    if await _handle_expired_battle(query, battle_current):
        return

    # 4. Automatically trigger Wild Pokémon's Move with Type Effectiveness
    wild_moves = get_pokemon_moves(wild_types)
    wild_move = random.choice(wild_moves)
    w_mult, w_eff_text = get_type_effectiveness(wild_move["type"], player_types)
    wild_dmg = calculate_damage(battle_current["wild_level"], wild_move["power"], battle_current["wild_attack"], battle_current["player_defense"], type_multiplier=w_mult)
    new_player_hp = max(0, battle_current["player_hp"] - wild_dmg)

    # Check if Player Fainted
    if new_player_hp <= 0:
        active_p_db_id = battle_current.get("player_db_id", 0)
        if active_p_db_id > 0:
            await update_user_pokemon_hp(active_p_db_id, 0, DB_PATH)

        team = await get_user_team(user_id, limit=6, db_path=DB_PATH)
        ready_team = [p for p in team if p["hp"] > 0]

        if ready_team:
            await update_active_battle(user_id, battle_current["wild_hp"], 0, turn_num, "player", DB_PATH)
            await query.answer("😵 Your Pokémon fainted! Select your next Pokémon!", show_alert=True)
            await switch_pokemon_menu_callback(update, context)
            return

        await end_active_battle(user_id, DB_PATH)
        await record_user_loss(user_id, DB_PATH)
        faint_card = await generate_battle_outcome_card(
            outcome_type="fainted",
            player_name=battle_current["player_name"],
            player_image_url=p_img_url,
            wild_name=battle_current["wild_name"],
            wild_image_url=w_img_url,
            status_text=f"All your team Pokémon fainted!"
        )
        faint_caption = (
            f"╭──────────────────────────────╮\n"
            f"│  😵 **ALL POKÉMON FAINTED** 😵  │\n"
            f"╰──────────────────────────────╯\n\n"
            f"Wild **{star_icon}{battle_current['wild_name']}** used **{wild_move['name']}** for **{wild_dmg} damage**!\n"
            f"All your team Pokémon fainted. You fled safely to recover."
        )
        try:
            await query.message.edit_media(media=InputMediaPhoto(media=faint_card, caption=faint_caption, parse_mode=ParseMode.MARKDOWN))
        except Exception:
            pass
        return

    # Advance to next turn & return to Player's Turn
    next_turn = turn_num + 1
    await update_active_battle(user_id, battle_current["wild_hp"], new_player_hp, next_turn, "player", DB_PATH)
    w_eff_str = f" {w_eff_text}" if w_eff_text else ""
    status_wild_msg = f"Wild {battle_current['wild_name']} used {wild_move['name']} for {wild_dmg} HP damage!{w_eff_str}"
    await render_battle_screen(query, user_id, status_text=status_wild_msg)


async def auto_wild_turn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user that wild turn is currently processing automatically."""
    query = update.callback_query
    if query:
        await query.answer("Wild Pokémon is taking its turn automatically...", show_alert=False)


async def catch_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Display Pokéball selection menu graphic IN-PLACE.
    Shows target wild Pokémon + inventory ball breakdown graphic.
    """
    query = update.callback_query
    if not query or not query.message:
        return

    user = query.from_user
    user_id = user.id

    inv = await get_or_create_inventory(user_id, DB_PATH)
    battle = await get_active_battle(user_id, DB_PATH)

    if not battle:
        await query.answer("⚠️ No active battle.", show_alert=True)
        return
    if await _handle_expired_battle(query, battle):
        return

    already_caught = await has_user_caught_pokemon(user_id, battle["wild_id"], DB_PATH)
    star_icon = "★ " if already_caught else ""

    menu_card = await generate_catch_menu_card(inventory=inv)

    keyboard = []
    if inv.get("pokeball", 0) > 0:
        keyboard.append([InlineKeyboardButton(f"Poké Ball (x{inv['pokeball']})", callback_data="throw_ball:pokeball")])
    if inv.get("greatball", 0) > 0:
        keyboard.append([InlineKeyboardButton(f"Great Ball (x{inv['greatball']})", callback_data="throw_ball:greatball")])
    if inv.get("ultraball", 0) > 0:
        keyboard.append([InlineKeyboardButton(f"Ultra Ball (x{inv['ultraball']})", callback_data="throw_ball:ultraball")])
    if inv.get("masterball", 0) > 0:
        keyboard.append([InlineKeyboardButton(f"Master Ball (x{inv['masterball']})", callback_data="throw_ball:masterball")])

    keyboard.append([InlineKeyboardButton("Back to Battle", callback_data="back_to_battle")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if len(keyboard) > 1:
        inventory_text = "Select a ball from your inventory:"
    else:
        inventory_text = "⚠️ You don't have any Poké Balls left in your inventory!"

    caption = (
        f"╭──────────────────────────────╮\n"
        f"│  🎯 **SELECT POKÉBALL TO THROW** │\n"
        f"╰──────────────────────────────╯\n\n"
        f"Target: Wild **{star_icon}{battle['wild_name']}** ({battle['wild_hp']}/{battle['wild_max_hp']} HP)\n\n"
        f"{inventory_text}"
    )

    try:
        media = InputMediaPhoto(media=menu_card, caption=caption, parse_mode=ParseMode.MARKDOWN)
        await query.message.edit_media(media=media, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error editing catch menu media: {e}")
        try:
            await query.message.edit_caption(caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            pass


async def throw_ball_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process throwing a Pokéball with a subtle 3-shake catch animation and displaying IV details on capture."""
    query = update.callback_query
    if not query or not query.message:
        return

    user = query.from_user
    user_id = user.id
    data = query.data
    if not data or not data.startswith("throw_ball:"):
        return

    ball_type = data.split(":")[1]

    success_use = await use_pokeball(user_id, ball_type, DB_PATH)
    if not success_use:
        ball_name = BALL_NAMES.get(ball_type, "Pokéball")
        await query.answer(f"⚠️ You don't have any {ball_name} left!", show_alert=True)
        return

    battle = await get_active_battle(user_id, DB_PATH)
    if not battle:
        await query.answer("⚠️ Battle ended.", show_alert=True)
        return
    if await _handle_expired_battle(query, battle):
        return

    already_caught = await has_user_caught_pokemon(user_id, battle["wild_id"], DB_PATH)
    star_icon = "★ " if already_caught else ""

    wild_catch_rate = battle.get("wild_catch_rate", 120)
    caught, pct = calculate_catch_success(battle["wild_max_hp"], battle["wild_hp"], wild_catch_rate, ball_type)
    ball_name = BALL_NAMES.get(ball_type, "Pokéball")

    await query.answer(f"Threw {ball_name}!")

    # 🎬 Catch Animation Card Frames (✰  ✰ ✰  ✰ ✰ ✰)
    w_img_url = battle.get("wild_image_url", "")
    for idx in range(1, 4):
        card_shake = await generate_catch_card(
            stage=f"shake_{idx}",
            wild_name=battle["wild_name"],
            wild_image_url=w_img_url,
            ball_name=ball_name
        )
        frame_caption = f"╭──────────────────────────────╮\n│  🎯 **THROWING {ball_name.upper()}** │\n╰──────────────────────────────╯\n\nYou threw a **{ball_name}** at Wild **{star_icon}{battle['wild_name']}**!\n\n{' '.join(['✰']*idx)}"
        try:
            await query.message.edit_media(media=InputMediaPhoto(media=card_shake, caption=frame_caption, parse_mode=ParseMode.MARKDOWN))
        except Exception:
            pass
        await asyncio.sleep(0.7)

    if caught:
        wild_data = await fetch_pokemon_data(battle["wild_id"])
        rarity = wild_data.get("rarity", "Common")
        wild_data["ivs"] = generate_ivs(rarity)
        ivs = wild_data["ivs"]

        await add_caught_pokemon(user_id, wild_data, battle["wild_level"], DB_PATH)
        await end_active_battle(user_id, DB_PATH)

        nature_str = wild_data.get("nature", "Hardy")
        nature_desc = get_nature_info(nature_str)["desc"]

        caught_card = await generate_catch_card(
            stage="caught",
            wild_name=battle["wild_name"],
            wild_image_url=w_img_url,
            ball_name=ball_name,
            iv_pct=ivs['total_pct'],
            grade=ivs['grade'],
            nature=nature_str
        )

        catch_caption = (
            f"╭──────────────────────────────╮\n"
            f"│  🎉 **POKÉMON CAUGHT!** 🎉       │\n"
            f"╰──────────────────────────────╯\n\n"
            f"Gotcha! You caught Wild **{star_icon}{battle['wild_name']}** (Lvl {battle['wild_level']}) with a **{ball_name}**!\n\n"
            f"🧬 **Nature**: `{nature_str} ({nature_desc})`\n"
            f"📊 **IV Quality**: `{ivs['total_pct']}% ({ivs['grade']})`\n"
            f"📦 **{battle['wild_name']}** was saved to your Pokémon Box."
        )
        try:
            await query.message.edit_media(media=InputMediaPhoto(media=caught_card, caption=catch_caption, parse_mode=ParseMode.MARKDOWN))
        except Exception:
            pass
    else:
        # Wild breaks free
        broke_card = await generate_catch_card(
            stage="broke_free",
            wild_name=battle["wild_name"],
            wild_image_url=w_img_url
        )
        try:
            await query.message.edit_media(
                media=InputMediaPhoto(media=broke_card, caption=f"Aww! Wild **{star_icon}{battle['wild_name']}** broke free!", parse_mode=ParseMode.MARKDOWN)
            )
        except Exception:
            pass

        await asyncio.sleep(1.0)

        turn_num = battle.get("turn_number", 1)
        await update_active_battle(user_id, battle["wild_hp"], battle["player_hp"], turn_num, "wild", DB_PATH)
        await render_battle_screen(query, user_id)

        await asyncio.sleep(1.5)

        battle_current = await get_active_battle(user_id, DB_PATH)
        if not battle_current or battle_current.get("turn_owner") != "wild":
            return

        wild_moves = get_pokemon_moves(["Normal", "Dark"])
        wild_move = random.choice(wild_moves)
        wild_dmg = calculate_damage(battle_current["wild_level"], wild_move["power"], battle_current["wild_attack"], battle_current["player_defense"])
        new_player_hp = max(0, battle_current["player_hp"] - wild_dmg)

        player_starter = await get_user_starter(user_id, DB_PATH)
        p_img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{player_starter['pokemon_id']}.png" if player_starter else ""

        if new_player_hp <= 0:
            await end_active_battle(user_id, DB_PATH)
            faint_card = await generate_battle_outcome_card(
                outcome_type="fainted",
                player_name=battle_current["player_name"],
                player_image_url=p_img_url,
                wild_name=battle_current["wild_name"],
                wild_image_url=w_img_url,
                status_text=f"Your {battle_current['player_name']} fainted!"
            )
            faint_caption = (
                f"╭──────────────────────────────╮\n"
                f"│  😵 **YOUR POKÉMON FAINTED** 😵  │\n"
                f"╰──────────────────────────────╯\n\n"
                f"Wild **{star_icon}{battle_current['wild_name']}** used **{wild_move['name']}** for **{wild_dmg} damage**!\n"
                f"Your **{battle_current['player_name']}** fainted. You fled safely to recover."
            )
            try:
                await query.message.edit_media(media=InputMediaPhoto(media=faint_card, caption=faint_caption, parse_mode=ParseMode.MARKDOWN))
            except Exception:
                pass
            return

        next_turn = turn_num + 1
        await update_active_battle(user_id, battle_current["wild_hp"], new_player_hp, next_turn, "player", DB_PATH)
        status_wild_msg = f"Wild {battle_current['wild_name']} used {wild_move['name']} for {wild_dmg} HP damage!"
        await render_battle_screen(query, user_id, status_text=status_wild_msg)


async def back_to_battle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return from Pokéball menu back to battle screen."""
    query = update.callback_query
    if query:
        battle = await get_active_battle(query.from_user.id, DB_PATH)
        if await _handle_expired_battle(query, battle):
            return
        await query.answer()
        await render_battle_screen(query, query.from_user.id)


async def run_battle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Flee safely from wild battle."""
    query = update.callback_query
    if not query or not query.message:
        return

    user_id = query.from_user.id
    battle = await get_active_battle(user_id, DB_PATH)
    if await _handle_expired_battle(query, battle):
        return
    already_caught = await has_user_caught_pokemon(user_id, battle["wild_id"], DB_PATH) if battle else False
    star_icon = "★ " if already_caught else ""
    wild_name = f"{star_icon}{battle['wild_name']}" if battle else "wild Pokémon"
    w_img_url = battle.get("wild_image_url", "") if battle else ""
    player_starter = await get_user_starter(user_id, DB_PATH)
    p_img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{player_starter['pokemon_id']}.png" if player_starter else ""

    await end_active_battle(user_id, DB_PATH)
    await query.answer("💨 Escaped safely!")

    fled_card = await generate_battle_outcome_card(
        outcome_type="fled",
        player_name=battle.get("player_name", "Starter") if battle else "Starter",
        player_image_url=p_img_url,
        wild_name=battle.get("wild_name", "Wild") if battle else "Wild",
        wild_image_url=w_img_url,
        status_text=f"You escaped safely from wild {wild_name}."
    )

    run_caption = (
        f"╭──────────────────────────────╮\n"
        f"│  🏃 **ESCAPED FROM BATTLE** 🏃   │\n"
        f"╰──────────────────────────────╯\n\n"
        f"You escaped safely from wild **{wild_name}**."
    )
    try:
        await query.message.edit_media(media=InputMediaPhoto(media=fled_card, caption=run_caption, parse_mode=ParseMode.MARKDOWN))
    except Exception:
        pass


async def switch_pokemon_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Renders visual team switch card graphic and clickable inline buttons for available non-fainted team members."""
    query = update.callback_query
    if not query or not query.message:
        return

    user_id = query.from_user.id
    battle = await get_active_battle(user_id, DB_PATH)
    if not battle:
        await query.answer("⚠️ No active battle.", show_alert=True)
        return
    if await _handle_expired_battle(query, battle):
        return

    team = await get_user_team(user_id, limit=6, db_path=DB_PATH)
    active_db_id = battle.get("player_db_id", 0)

    switch_card = await generate_switch_pokemon_card(team, active_db_id)

    keyboard = []
    ready_count = 0
    for poke in team:
        p_db_id = poke["id"]
        is_active = (p_db_id == active_db_id)
        is_fainted = (poke["hp"] <= 0)

        if is_fainted:
            btn_text = f"😵 {poke['name']} (Fainted)"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data="noop")])
        elif is_active:
            btn_text = f"⚔️ {poke['name']} (Active)"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data="noop")])
        else:
            ready_count += 1
            btn_text = f"🔄 Switch to {poke['name']} (Lvl {poke['level']})"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"do_switch:{p_db_id}")])

    keyboard.append([InlineKeyboardButton("Back to Battle", callback_data="back_to_battle")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if ready_count > 0:
        sub_text = "Select a Pokémon from your team to send into battle:"
    else:
        sub_text = "⚠️ All other team Pokémon are fainted or active!"

    caption = (
        f"╭──────────────────────────────╮\n"
        f"│  🔄 **SWITCH POKÉMON** 🔄      │\n"
        f"╰──────────────────────────────╯\n\n"
        f"{sub_text}"
    )

    try:
        await query.message.edit_media(media=InputMediaPhoto(media=switch_card, caption=caption, parse_mode=ParseMode.MARKDOWN), reply_markup=reply_markup)
    except Exception:
        pass


async def do_switch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute switching active Pokémon in battle and proceed with battle or wild turn."""
    query = update.callback_query
    if not query or not query.message:
        return

    user_id = query.from_user.id
    data = query.data
    if not data or not data.startswith("do_switch:"):
        return

    target_db_id = int(data.split(":")[1])

    battle = await get_active_battle(user_id, DB_PATH)
    if not battle:
        await query.answer("⚠️ Battle ended.", show_alert=True)
        return
    if await _handle_expired_battle(query, battle):
        return

    switched_poke = await switch_active_battle_pokemon(user_id, target_db_id, DB_PATH)
    if not switched_poke:
        await query.answer("⚠️ Cannot switch to that Pokémon!", show_alert=True)
        return

    await query.answer(f"🔄 Go! {switched_poke['name']}!")

    switch_msg = f"You switched out! Go! {switched_poke['name']}!"
    await render_battle_screen(query, user_id, status_text=switch_msg)


async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """No-operation callback for blank spacer button."""
    query = update.callback_query
    if query:
        await query.answer()


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("ERROR: Please set a valid BOT_TOKEN in your .env file!")
        return

    request_config = HTTPXRequest(
        connect_timeout=20.0,
        read_timeout=30.0,
        write_timeout=20.0,
        pool_timeout=20.0
    )
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request_config)
        .post_init(post_init)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("travel", travel_command))
    app.add_handler(CommandHandler("hunt", hunt_command))
    app.add_handler(CommandHandler("mystats", mystats_command))
    app.add_handler(CommandHandler("stats", mystats_command))
    app.add_handler(CommandHandler("profile", mystats_command))
    app.add_handler(CommandHandler("inventory", inventory_command))
    app.add_handler(CommandHandler("inv", inventory_command))
    app.add_handler(CommandHandler("bag", inventory_command))

    app.add_handler(CallbackQueryHandler(select_starter_callback, pattern=r"^select_starter:"))
    app.add_handler(CallbackQueryHandler(inventory_category_callback, pattern=r"^inv_cat:"))
    app.add_handler(CallbackQueryHandler(card_customization_callback, pattern=r"^(card_|mystats_)"))
    app.add_handler(CallbackQueryHandler(travel_callback, pattern=r"^travel:"))
    app.add_handler(CallbackQueryHandler(ev_yields_callback, pattern=r"^ev_yields:"))
    app.add_handler(CallbackQueryHandler(start_battle_callback, pattern=r"^battle:"))
    app.add_handler(CallbackQueryHandler(use_move_callback, pattern=r"^use_move:"))
    app.add_handler(CallbackQueryHandler(auto_wild_turn_callback, pattern=r"^auto_wild_turn$"))
    app.add_handler(CallbackQueryHandler(catch_menu_callback, pattern=r"^catch_menu$"))
    app.add_handler(CallbackQueryHandler(switch_pokemon_menu_callback, pattern=r"^switch_pokemon_menu$"))
    app.add_handler(CallbackQueryHandler(do_switch_callback, pattern=r"^do_switch:"))
    app.add_handler(CallbackQueryHandler(throw_ball_callback, pattern=r"^throw_ball:"))
    app.add_handler(CallbackQueryHandler(back_to_battle_callback, pattern=r"^back_to_battle$"))
    app.add_handler(CallbackQueryHandler(run_battle_callback, pattern=r"^run_battle$"))
    app.add_handler(CallbackQueryHandler(noop_callback, pattern=r"^noop$"))

    logger.info("Bot starting polling with IV/EV system, Rarity tiers, and Legendary encounters...")
    app.run_polling(bootstrap_retries=-1)


if __name__ == "__main__":
    import time
    while True:
        try:
            main()
        except KeyboardInterrupt:
            logger.info("Bot manually stopped.")
            break
        except Exception as e:
            logger.error(f"Bot encountered connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
