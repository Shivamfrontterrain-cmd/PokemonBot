import aiosqlite
import json
import datetime
import time
from typing import Optional, Dict, Any, Tuple


async def init_db(db_path: str = "hexamonbot.db") -> None:
    """Initialize database tables for users, Pokémon, inventory, active battles, and active hunts."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA synchronous=NORMAL;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                starter_chosen INTEGER DEFAULT 0,
                trainer_level INTEGER DEFAULT 1,
                trainer_exp INTEGER DEFAULT 0,
                current_region TEXT DEFAULT 'Kanto',
                pokedollars INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_pokemon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pokemon_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                nickname TEXT NOT NULL,
                level INTEGER DEFAULT 5,
                hp INTEGER NOT NULL,
                max_hp INTEGER NOT NULL,
                attack INTEGER NOT NULL,
                defense INTEGER NOT NULL,
                sp_attack INTEGER NOT NULL,
                sp_defense INTEGER NOT NULL,
                speed INTEGER NOT NULL,
                is_starter INTEGER DEFAULT 1,
                iv_hp INTEGER DEFAULT 15,
                iv_attack INTEGER DEFAULT 15,
                iv_defense INTEGER DEFAULT 15,
                iv_sp_attack INTEGER DEFAULT 15,
                iv_sp_defense INTEGER DEFAULT 15,
                iv_speed INTEGER DEFAULT 15,
                iv_total_pct REAL DEFAULT 48.4,
                ev_hp INTEGER DEFAULT 0,
                ev_attack INTEGER DEFAULT 0,
                ev_defense INTEGER DEFAULT 0,
                ev_sp_attack INTEGER DEFAULT 0,
                ev_sp_defense INTEGER DEFAULT 0,
                ev_speed INTEGER DEFAULT 0,
                rarity TEXT DEFAULT 'Common',
                nature TEXT DEFAULT 'Hardy',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_inventory (
                user_id INTEGER PRIMARY KEY,
                pokeball INTEGER DEFAULT 10,
                greatball INTEGER DEFAULT 5,
                ultraball INTEGER DEFAULT 0,
                masterball INTEGER DEFAULT 0,
                rare_candy INTEGER DEFAULT 0,
                exp_candy_s INTEGER DEFAULT 0,
                exp_candy_m INTEGER DEFAULT 0,
                exp_candy_l INTEGER DEFAULT 0,
                tms_json TEXT DEFAULT '{}',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS active_battles (
                user_id INTEGER PRIMARY KEY,
                wild_id INTEGER NOT NULL,
                wild_name TEXT NOT NULL,
                wild_level INTEGER NOT NULL,
                wild_hp INTEGER NOT NULL,
                wild_max_hp INTEGER NOT NULL,
                wild_attack INTEGER NOT NULL,
                wild_defense INTEGER NOT NULL,
                wild_speed INTEGER NOT NULL,
                wild_catch_rate INTEGER DEFAULT 120,
                wild_image_url TEXT,
                wild_nature TEXT DEFAULT 'Hardy',
                player_pokemon_id INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                player_level INTEGER NOT NULL,
                player_hp INTEGER NOT NULL,
                player_max_hp INTEGER NOT NULL,
                player_attack INTEGER NOT NULL,
                player_defense INTEGER NOT NULL,
                player_speed INTEGER NOT NULL,
                player_nature TEXT DEFAULT 'Hardy',
                turn_number INTEGER DEFAULT 1,
                turn_owner TEXT DEFAULT 'player',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS active_hunts (
                user_id INTEGER PRIMARY KEY,
                hunt_token TEXT NOT NULL,
                pokemon_id INTEGER NOT NULL,
                wild_level INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        await db.commit()
        await _migrate_schema(db)


async def _migrate_schema(db: aiosqlite.Connection) -> None:
    """Ensure newly added columns exist in tables."""
    async with db.execute("PRAGMA table_info(users)") as cursor:
        columns = [row[1] for row in await cursor.fetchall()]

    if "trainer_level" not in columns:
        await db.execute("ALTER TABLE users ADD COLUMN trainer_level INTEGER DEFAULT 1")
    if "trainer_exp" not in columns:
        await db.execute("ALTER TABLE users ADD COLUMN trainer_exp INTEGER DEFAULT 0")
    if "current_region" not in columns:
        await db.execute("ALTER TABLE users ADD COLUMN current_region TEXT DEFAULT 'Kanto'")
    if "pokedollars" not in columns:
        await db.execute("ALTER TABLE users ADD COLUMN pokedollars INTEGER DEFAULT 0")
    if "wins" not in columns:
        await db.execute("ALTER TABLE users ADD COLUMN wins INTEGER DEFAULT 0")
    if "losses" not in columns:
        await db.execute("ALTER TABLE users ADD COLUMN losses INTEGER DEFAULT 0")
    if "card_theme" not in columns:
        await db.execute("ALTER TABLE users ADD COLUMN card_theme TEXT DEFAULT 'Classic Red'")
    if "card_text_color" not in columns:
        await db.execute("ALTER TABLE users ADD COLUMN card_text_color TEXT DEFAULT 'Classic Dark'")
    if "card_avatar" not in columns:
        await db.execute("ALTER TABLE users ADD COLUMN card_avatar TEXT DEFAULT 'Trainer Boy'")

    async with db.execute("PRAGMA table_info(active_battles)") as cursor:
        b_columns = [row[1] for row in await cursor.fetchall()]

    if "turn_number" not in b_columns:
        await db.execute("ALTER TABLE active_battles ADD COLUMN turn_number INTEGER DEFAULT 1")
    if "turn_owner" not in b_columns:
        await db.execute("ALTER TABLE active_battles ADD COLUMN turn_owner TEXT DEFAULT 'player'")
    if "wild_nature" not in b_columns:
        await db.execute("ALTER TABLE active_battles ADD COLUMN wild_nature TEXT DEFAULT 'Hardy'")
    if "player_nature" not in b_columns:
        await db.execute("ALTER TABLE active_battles ADD COLUMN player_nature TEXT DEFAULT 'Hardy'")
    if "player_db_id" not in b_columns:
        await db.execute("ALTER TABLE active_battles ADD COLUMN player_db_id INTEGER DEFAULT 0")
    if "last_action_timestamp" not in b_columns:
        await db.execute("ALTER TABLE active_battles ADD COLUMN last_action_timestamp REAL DEFAULT 0")

    async with db.execute("PRAGMA table_info(user_pokemon)") as cursor:
        p_columns = [row[1] for row in await cursor.fetchall()]

    iv_ev_cols = [
        ("iv_hp", "INTEGER DEFAULT 15"),
        ("iv_attack", "INTEGER DEFAULT 15"),
        ("iv_defense", "INTEGER DEFAULT 15"),
        ("iv_sp_attack", "INTEGER DEFAULT 15"),
        ("iv_sp_defense", "INTEGER DEFAULT 15"),
        ("iv_speed", "INTEGER DEFAULT 15"),
        ("iv_total_pct", "REAL DEFAULT 48.4"),
        ("ev_hp", "INTEGER DEFAULT 0"),
        ("ev_attack", "INTEGER DEFAULT 0"),
        ("ev_defense", "INTEGER DEFAULT 0"),
        ("ev_sp_attack", "INTEGER DEFAULT 0"),
        ("ev_sp_defense", "INTEGER DEFAULT 0"),
        ("ev_speed", "INTEGER DEFAULT 0"),
        ("rarity", "TEXT DEFAULT 'Common'"),
        ("nature", "TEXT DEFAULT 'Hardy'"),
    ]

    for col_name, col_type in iv_ev_cols:
        if col_name not in p_columns:
            await db.execute(f"ALTER TABLE user_pokemon ADD COLUMN {col_name} {col_type}")

    async with db.execute("PRAGMA table_info(user_inventory)") as cursor:
        inv_columns = [row[1] for row in await cursor.fetchall()]

    inv_cols = [
        ("rare_candy", "INTEGER DEFAULT 0"),
        ("exp_candy_s", "INTEGER DEFAULT 0"),
        ("exp_candy_m", "INTEGER DEFAULT 0"),
        ("exp_candy_l", "INTEGER DEFAULT 0"),
        ("tms_json", "TEXT DEFAULT '{}'"),
        ("stones_json", "TEXT DEFAULT '{\"Fire Stone\": 1, \"Water Stone\": 1, \"Thunder Stone\": 1}'"),
        ("eggs_json", "TEXT DEFAULT '{\"Mystery Egg\": 1, \"Lucky Egg\": 1}'"),
        ("orbs_json", "TEXT DEFAULT '{\"Life Orb\": 1}'"),
        ("crystals_json", "TEXT DEFAULT '{\"Tera Crystal\": 2}'"),
        ("tutors_json", "TEXT DEFAULT '{\"Heart Scale\": 3}'"),
    ]

    for col_name, col_type in inv_cols:
        if col_name not in inv_columns:
            await db.execute(f"ALTER TABLE user_inventory ADD COLUMN {col_name} {col_type}")

    await db.commit()


async def get_user(user_id: int, db_path: str = "hexamonbot.db") -> Optional[Dict[str, Any]]:
    """Retrieve user details by Telegram user_id."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def update_user_region(user_id: int, new_region: str, db_path: str = "hexamonbot.db") -> bool:
    """Update user active region."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE users SET current_region = ? WHERE user_id = ?", (new_region, user_id))
        await db.commit()
        return True


async def get_user_starter(user_id: int, db_path: str = "hexamonbot.db") -> Optional[Dict[str, Any]]:
    """Get the starter/active Pokémon owned by the user."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM user_pokemon WHERE user_id = ? ORDER BY is_starter DESC, level DESC LIMIT 1",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def register_user_with_starter(
    user_id: int,
    username: Optional[str],
    first_name: str,
    pokemon_data: Dict[str, Any],
    db_path: str = "hexamonbot.db"
) -> Tuple[bool, str]:
    """Atomically registers user, grants starter Pokémon with high IVs and Nature, and sets initial inventory."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT starter_chosen FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user_row = await cursor.fetchone()
            if user_row and user_row["starter_chosen"] == 1:
                return False, "You have already chosen a starter Pokémon!"

        if not user_row:
            await db.execute(
                "INSERT INTO users (user_id, username, first_name, starter_chosen) VALUES (?, ?, ?, 1)",
                (user_id, username, first_name)
            )
        else:
            await db.execute(
                "UPDATE users SET starter_chosen = 1, username = ?, first_name = ? WHERE user_id = ?",
                (username, first_name, user_id)
            )

        stats = pokemon_data["stats"]
        ivs = pokemon_data.get("ivs", {"hp": 25, "attack": 25, "defense": 25, "sp_attack": 25, "sp_defense": 25, "speed": 25, "total_pct": 80.6})
        rarity = pokemon_data.get("rarity", "Starter")
        nature = pokemon_data.get("nature", "Hardy")

        await db.execute("""
            INSERT INTO user_pokemon (
                user_id, pokemon_id, name, nickname, level,
                hp, max_hp, attack, defense, sp_attack, sp_defense, speed, is_starter,
                iv_hp, iv_attack, iv_defense, iv_sp_attack, iv_sp_defense, iv_speed, iv_total_pct,
                rarity, nature
            ) VALUES (?, ?, ?, ?, 5, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            pokemon_data["id"],
            pokemon_data["name"],
            pokemon_data["name"],
            stats["hp"],
            stats["hp"],
            stats["attack"],
            stats["defense"],
            stats.get("special-attack", stats.get("sp_attack", 50)),
            stats.get("special-defense", stats.get("sp_defense", 50)),
            stats["speed"],
            ivs.get("hp", 25),
            ivs.get("attack", 25),
            ivs.get("defense", 25),
            ivs.get("sp_attack", 25),
            ivs.get("sp_defense", 25),
            ivs.get("speed", 25),
            ivs.get("total_pct", 80.6),
            rarity,
            nature,
        ))

        await db.execute("""
            INSERT INTO user_inventory (user_id, pokeball, greatball, ultraball, masterball)
            VALUES (?, 10, 5, 0, 0)
            ON CONFLICT(user_id) DO UPDATE SET
            pokeball = pokeball + 10,
            greatball = greatball + 5
        """, (user_id,))

        await db.commit()
        return True, "Starter registered successfully!"


async def get_or_create_inventory(user_id: int, db_path: str = "hexamonbot.db") -> Dict[str, Any]:
    """Retrieve user inventory or initialize defaults."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM user_inventory WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()

        if not row:
            await db.execute(
                "INSERT INTO user_inventory (user_id, pokeball, greatball, ultraball, masterball) VALUES (?, 10, 5, 0, 0)",
                (user_id,)
            )
            await db.commit()
            async with db.execute("SELECT * FROM user_inventory WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()

        inv = dict(row) if row else {
            "pokeball": 10, "greatball": 5, "ultraball": 0, "masterball": 0,
            "rare_candy": 0, "exp_candy_s": 0, "exp_candy_m": 0, "exp_candy_l": 0, "tms_json": "{}"
        }

        for cat_key in ["tms", "stones", "eggs", "orbs", "crystals", "tutors"]:
            raw_val = inv.get(f"{cat_key}_json")
            if not raw_val or raw_val == "{}":
                if cat_key == "stones":
                    inv[cat_key] = {"Fire Stone": 1, "Water Stone": 1, "Thunder Stone": 1}
                elif cat_key == "eggs":
                    inv[cat_key] = {"Mystery Egg": 1, "Lucky Egg": 1}
                elif cat_key == "orbs":
                    inv[cat_key] = {"Life Orb": 1}
                elif cat_key == "crystals":
                    inv[cat_key] = {"Tera Crystal": 2}
                elif cat_key == "tutors":
                    inv[cat_key] = {"Heart Scale": 3}
                else:
                    inv[cat_key] = {}
            else:
                try:
                    inv[cat_key] = json.loads(raw_val)
                except Exception:
                    inv[cat_key] = {}

        async with db.execute("SELECT pokedollars FROM users WHERE user_id = ?", (user_id,)) as cursor:
            u_row = await cursor.fetchone()
            inv["pokedollars"] = u_row["pokedollars"] if (u_row and u_row["pokedollars"] is not None) else 0

        return inv


async def use_pokeball(user_id: int, ball_type: str, db_path: str = "hexamonbot.db") -> bool:
    """Decrements Pokéball count from inventory if available (>0)."""
    valid_balls = ["pokeball", "greatball", "ultraball", "masterball"]
    if ball_type not in valid_balls:
        return False

    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(f"SELECT {ball_type} FROM user_inventory WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()

        if not row or row[ball_type] <= 0:
            return False

        await db.execute(
            f"UPDATE user_inventory SET {ball_type} = {ball_type} - 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()
        return True


async def set_active_hunt(
    user_id: int,
    hunt_token: str,
    pokemon_id: int,
    wild_level: int,
    db_path: str = "hexamonbot.db"
) -> None:
    """Store or replace active hunt encounter for a user."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            INSERT INTO active_hunts (user_id, hunt_token, pokemon_id, wild_level)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            hunt_token = excluded.hunt_token,
            pokemon_id = excluded.pokemon_id,
            wild_level = excluded.wild_level,
            created_at = CURRENT_TIMESTAMP
        """, (user_id, hunt_token, pokemon_id, wild_level))
        await db.commit()


async def get_active_hunt(user_id: int, db_path: str = "hexamonbot.db") -> Optional[Dict[str, Any]]:
    """Retrieve user's active hunt record."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM active_hunts WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def clear_active_hunt(user_id: int, db_path: str = "hexamonbot.db") -> None:
    """Clear active hunt token when battle starts or encounter ends."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("DELETE FROM active_hunts WHERE user_id = ?", (user_id,))
        await db.commit()


async def create_active_battle(
    user_id: int,
    wild_data: Dict[str, Any],
    player_starter: Dict[str, Any],
    db_path: str = "hexamonbot.db"
) -> None:
    """Save active battle instance to database."""
    async with aiosqlite.connect(db_path) as db:
        stats = wild_data["stats"]
        wild_nature = wild_data.get("nature", "Hardy")
        player_nature = player_starter.get("nature", "Hardy")

        player_db_id = player_starter.get("id", 0)
        now_ts = time.time()

        await db.execute("""
            INSERT INTO active_battles (
                user_id, wild_id, wild_name, wild_level, wild_hp, wild_max_hp,
                wild_attack, wild_defense, wild_speed, wild_catch_rate, wild_image_url, wild_nature,
                player_pokemon_id, player_db_id, player_name, player_level, player_hp, player_max_hp,
                player_attack, player_defense, player_speed, player_nature, turn_number, turn_owner, last_action_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'player', ?)
            ON CONFLICT(user_id) DO UPDATE SET
                wild_id = excluded.wild_id,
                wild_name = excluded.wild_name,
                wild_level = excluded.wild_level,
                wild_hp = excluded.wild_hp,
                wild_max_hp = excluded.wild_max_hp,
                wild_attack = excluded.wild_attack,
                wild_defense = excluded.wild_defense,
                wild_speed = excluded.wild_speed,
                wild_catch_rate = excluded.wild_catch_rate,
                wild_image_url = excluded.wild_image_url,
                wild_nature = excluded.wild_nature,
                player_pokemon_id = excluded.player_pokemon_id,
                player_db_id = excluded.player_db_id,
                player_name = excluded.player_name,
                player_level = excluded.player_level,
                player_hp = excluded.player_hp,
                player_max_hp = excluded.player_max_hp,
                player_attack = excluded.player_attack,
                player_defense = excluded.player_defense,
                player_speed = excluded.player_speed,
                player_nature = excluded.player_nature,
                turn_number = 1,
                turn_owner = 'player',
                last_action_timestamp = excluded.last_action_timestamp
        """, (
            user_id,
            wild_data["id"],
            wild_data["name"],
            wild_data.get("wild_level", 5),
            stats["hp"],
            stats["hp"],
            stats["attack"],
            stats["defense"],
            stats["speed"],
            wild_data.get("capture_rate", 120),
            wild_data.get("image_url", ""),
            wild_nature,
            player_starter["pokemon_id"] if "pokemon_id" in player_starter else player_starter["id"],
            player_db_id,
            player_starter["name"],
            player_starter["level"],
            player_starter["hp"],
            player_starter["max_hp"],
            player_starter["attack"],
            player_starter["defense"],
            player_starter["speed"],
            player_nature,
            now_ts,
        ))
        await db.commit()


async def get_active_battle(user_id: int, db_path: str = "hexamonbot.db", max_inactivity_seconds: int = 120) -> Optional[Dict[str, Any]]:
    """Retrieve active battle record. Automatically ends battle if inactive > 120 seconds (2 minutes)."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM active_battles WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None

            bdict = dict(row)
            last_ts = bdict.get("last_action_timestamp")
            if last_ts is not None and last_ts > 0 and (time.time() - last_ts) > max_inactivity_seconds:
                # Inactive for > 2 minutes (120s)! Wild Pokémon fled. End battle.
                await db.execute("DELETE FROM active_battles WHERE user_id = ?", (user_id,))
                await db.commit()
                return {"expired": True, "wild_name": bdict.get("wild_name", "Wild Pokémon")}

            return bdict


async def update_active_battle(
    user_id: int,
    wild_hp: int,
    player_hp: int,
    turn_number: int,
    turn_owner: str,
    db_path: str = "hexamonbot.db"
) -> None:
    """Update HP and turn state in active battle with current timestamp."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "UPDATE active_battles SET wild_hp = ?, player_hp = ?, turn_number = ?, turn_owner = ?, last_action_timestamp = ? WHERE user_id = ?",
            (max(0, wild_hp), max(0, player_hp), turn_number, turn_owner, time.time(), user_id)
        )
        await db.commit()


async def end_active_battle(user_id: int, db_path: str = "hexamonbot.db") -> None:
    """Delete active battle record when battle concludes."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("DELETE FROM active_battles WHERE user_id = ?", (user_id,))
        await db.commit()


async def add_caught_pokemon(
    user_id: int,
    pokemon_data: Dict[str, Any],
    level: int,
    db_path: str = "hexamonbot.db"
) -> bool:
    """Save a newly caught wild Pokémon into user_pokemon table with IVs, EVs, rarity, and nature."""
    async with aiosqlite.connect(db_path) as db:
        stats = pokemon_data["stats"]
        ivs = pokemon_data.get("ivs", {"hp": 15, "attack": 15, "defense": 15, "sp_attack": 15, "sp_defense": 15, "speed": 15, "total_pct": 48.4})
        rarity = pokemon_data.get("rarity", "Common")
        nature = pokemon_data.get("nature", "Hardy")

        await db.execute("""
            INSERT INTO user_pokemon (
                user_id, pokemon_id, name, nickname, level,
                hp, max_hp, attack, defense, sp_attack, sp_defense, speed, is_starter,
                iv_hp, iv_attack, iv_defense, iv_sp_attack, iv_sp_defense, iv_speed, iv_total_pct,
                rarity, nature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            pokemon_data["id"],
            pokemon_data["name"],
            pokemon_data["name"],
            level,
            stats["hp"],
            stats["hp"],
            stats["attack"],
            stats["defense"],
            stats.get("special-attack", stats.get("sp_attack", 50)),
            stats.get("special-defense", stats.get("sp_defense", 50)),
            stats["speed"],
            ivs.get("hp", 15),
            ivs.get("attack", 15),
            ivs.get("defense", 15),
            ivs.get("sp_attack", 15),
            ivs.get("sp_defense", 15),
            ivs.get("speed", 15),
            ivs.get("total_pct", 48.4),
            rarity,
            nature,
        ))
        await db.commit()
        return True


async def has_user_caught_pokemon(user_id: int, pokemon_id: int, db_path: str = "hexamonbot.db") -> bool:
    """Check if the user already has caught a Pokémon with the given pokemon_id."""
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            "SELECT 1 FROM user_pokemon WHERE user_id = ? AND pokemon_id = ? LIMIT 1",
            (user_id, pokemon_id)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None


async def get_user_team(user_id: int, limit: int = 6, db_path: str = "hexamonbot.db") -> List[Dict[str, Any]]:
    """Retrieve up to 6 team Pokémon for the user (starter first, then caught)."""
    from iv_ev_system import calculate_effective_stats

    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM user_pokemon WHERE user_id = ? ORDER BY is_starter DESC, id ASC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()

        team = []
        for row in rows:
            pdict = dict(row)
            base_stats = {
                "hp": pdict["max_hp"],
                "attack": pdict["attack"],
                "defense": pdict["defense"],
                "sp_attack": pdict["sp_attack"],
                "sp_defense": pdict["sp_defense"],
                "speed": pdict["speed"]
            }
            ivs = {
                "hp": pdict.get("iv_hp", 15),
                "attack": pdict.get("iv_attack", 15),
                "defense": pdict.get("iv_defense", 15),
                "sp_attack": pdict.get("iv_sp_attack", 15),
                "sp_defense": pdict.get("iv_sp_defense", 15),
                "speed": pdict.get("iv_speed", 15),
                "total_pct": pdict.get("iv_total_pct", 48.4)
            }
            evs = {
                "hp": pdict.get("ev_hp", 0),
                "attack": pdict.get("ev_attack", 0),
                "defense": pdict.get("ev_defense", 0),
                "sp_attack": pdict.get("ev_sp_attack", 0),
                "sp_defense": pdict.get("ev_sp_defense", 0),
                "speed": pdict.get("ev_speed", 0)
            }

            eff_stats = calculate_effective_stats(base_stats, pdict["level"], ivs, evs, pdict.get("nature", "Hardy"))

            pdict["max_hp"] = eff_stats["hp"]
            pdict["attack"] = eff_stats["attack"]
            pdict["defense"] = eff_stats["defense"]
            pdict["sp_attack"] = eff_stats["sp_attack"]
            pdict["sp_defense"] = eff_stats["sp_defense"]
            pdict["speed"] = eff_stats["speed"]
            pdict["image_url"] = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pdict['pokemon_id']}.png"
            team.append(pdict)

        return team


async def update_user_pokemon_hp(pokemon_db_id: int, current_hp: int, db_path: str = "hexamonbot.db") -> None:
    """Update current HP of a user's Pokémon in user_pokemon table."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE user_pokemon SET hp = ? WHERE id = ?", (max(0, current_hp), pokemon_db_id))
        await db.commit()


async def switch_active_battle_pokemon(user_id: int, pokemon_db_id: int, db_path: str = "hexamonbot.db") -> Optional[Dict[str, Any]]:
    """Switch active battler in active_battles to the specified user_pokemon record."""
    team = await get_user_team(user_id, limit=6, db_path=db_path)
    target = next((p for p in team if p["id"] == pokemon_db_id), None)
    if not target or target["hp"] <= 0:
        return None

    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            UPDATE active_battles SET
                player_pokemon_id = ?,
                player_db_id = ?,
                player_name = ?,
                player_level = ?,
                player_hp = ?,
                player_max_hp = ?,
                player_attack = ?,
                player_defense = ?,
                player_speed = ?,
                player_nature = ?,
                last_action_timestamp = ?
            WHERE user_id = ?
        """, (
            target["pokemon_id"],
            target["id"],
            target["name"],
            target["level"],
            target["hp"],
            target["max_hp"],
            target["attack"],
            target["defense"],
            target["speed"],
            target.get("nature", "Hardy"),
            time.time(),
            user_id
        ))
        await db.commit()

    return target


async def add_user_pokedollars(user_id: int, amount: int, db_path: str = "hexamonbot.db") -> int:
    """Add Pokédollars (PD) to user account and return new total balance."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE users SET pokedollars = pokedollars + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()
        async with db.execute("SELECT pokedollars FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if (row and row[0] is not None) else amount


async def get_user_pokedollars(user_id: int, db_path: str = "hexamonbot.db") -> int:
    """Retrieve user's current Pokédollars (PD) balance."""
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT pokedollars FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if (row and row[0] is not None) else 0


async def add_user_tm(user_id: int, tm_id: str, quantity: int = 1, db_path: str = "hexamonbot.db") -> int:
    """Add a Technical Machine (TM) to user's inventory tms_json."""
    inv = await get_or_create_inventory(user_id, db_path=db_path)
    tms = inv.get("tms", {})
    tms[tm_id] = tms.get(tm_id, 0) + quantity
    tms_str = json.dumps(tms)

    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE user_inventory SET tms_json = ? WHERE user_id = ?", (tms_str, user_id))
        await db.commit()

    return tms[tm_id]


async def record_user_win(user_id: int, exp_gained: int = 50, db_path: str = "hexamonbot.db") -> None:
    """Record a battle win and award trainer exp."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "UPDATE users SET wins = wins + 1, trainer_exp = trainer_exp + ? WHERE user_id = ?",
            (exp_gained, user_id)
        )
        await db.commit()


async def record_user_loss(user_id: int, db_path: str = "hexamonbot.db") -> None:
    """Record a battle loss or flee."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("UPDATE users SET losses = losses + 1 WHERE user_id = ?", (user_id,))
        await db.commit()


async def update_user_card_settings(
    user_id: int,
    card_theme: Optional[str] = None,
    card_text_color: Optional[str] = None,
    card_avatar: Optional[str] = None,
    db_path: str = "hexamonbot.db"
) -> None:
    """Update Trainer Card theme, text color, or avatar settings."""
    async with aiosqlite.connect(db_path) as db:
        if card_theme is not None:
            await db.execute("UPDATE users SET card_theme = ? WHERE user_id = ?", (card_theme, user_id))
        if card_text_color is not None:
            await db.execute("UPDATE users SET card_text_color = ? WHERE user_id = ?", (card_text_color, user_id))
        if card_avatar is not None:
            await db.execute("UPDATE users SET card_avatar = ? WHERE user_id = ?", (card_avatar, user_id))
        await db.commit()


async def get_user_full_stats(user_id: int, db_path: str = "hexamonbot.db") -> Dict[str, Any]:
    """Retrieve full user statistics and Trainer Card customization settings."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user_row = await cursor.fetchone()
            if not user_row:
                return {}
            user_data = dict(user_row)

        async with db.execute("SELECT COUNT(*) FROM user_pokemon WHERE user_id = ?", (user_id,)) as cursor:
            count_row = await cursor.fetchone()
            user_data["total_pokemon"] = count_row[0] if count_row else 0

        return user_data

