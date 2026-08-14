import asyncio
import os
import aiosqlite
from database import (
    init_db,
    get_user,
    register_user_with_starter,
    get_or_create_inventory,
    use_pokeball,
    create_active_battle,
    get_active_battle,
    update_active_battle,
    end_active_battle,
    add_caught_pokemon,
    get_user_starter
)
from pokeapi import fetch_pokemon_data
from battle_engine import calculate_damage, calculate_catch_success


async def run_tests():
    test_db = "test_feature3.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    print("--- 1. Testing Database & Table Setup ---")
    await init_db(test_db)
    print("Database initialized successfully.")

    print("\n--- 2. Testing Starter Setup & Default Inventory (10 Pokéballs, 5 Great Balls) ---")
    charmander = await fetch_pokemon_data(4)
    user_id = 3003
    success, msg = await register_user_with_starter(user_id, "trainer_blue", "Blue", charmander, test_db)
    assert success is True

    inv = await get_or_create_inventory(user_id, test_db)
    assert inv["pokeball"] == 10, f"Expected 10 pokeballs, got {inv['pokeball']}"
    assert inv["greatball"] == 5, f"Expected 5 greatballs, got {inv['greatball']}"
    print(f"Inventory verified: Pokeballs={inv['pokeball']}, Great Balls={inv['greatball']}")

    print("\n--- 3. Testing Active Battle Initialization ---")
    pikachu = await fetch_pokemon_data(25)
    pikachu["wild_level"] = 6

    player_pokemon = await get_user_starter(user_id, test_db)
    await create_active_battle(user_id, pikachu, player_pokemon, test_db)

    battle = await get_active_battle(user_id, test_db)
    assert battle["wild_name"] == "Pikachu"
    assert battle["wild_hp"] == pikachu["stats"]["hp"]
    assert battle["player_name"] == "Charmander"
    print(f"Battle created: Player {battle['player_name']} vs Wild {battle['wild_name']} (Lvl {battle['wild_level']})")

    print("\n--- 4. Testing Turn-Based Damage Calculation ---")
    dmg = calculate_damage(5, 40, battle["player_attack"], battle["wild_defense"])
    assert dmg > 0
    new_wild_hp = max(0, battle["wild_hp"] - dmg)
    await update_active_battle(user_id, new_wild_hp, battle["player_hp"], test_db)
    
    battle_updated = await get_active_battle(user_id, test_db)
    assert battle_updated["wild_hp"] == new_wild_hp
    print(f"Turn executed: Dealt {dmg} damage! Wild HP now {new_wild_hp}/{battle['wild_max_hp']}")

    print("\n--- 5. Testing Pokéball Throw & Catch Calculation ---")
    used = await use_pokeball(user_id, "greatball", test_db)
    assert used is True
    inv_after = await get_or_create_inventory(user_id, test_db)
    assert inv_after["greatball"] == 4
    print(f"Pokéball used successfully! Remaining Great Balls: {inv_after['greatball']}")

    # Low HP catch calculation test
    caught, pct = calculate_catch_success(battle["wild_max_hp"], 5, 120, "greatball")
    print(f"Catch probability at 5 HP with Great Ball: {pct}% (Caught={caught})")

    print("\n--- 6. Testing Saving Caught Pokémon ---")
    saved = await add_caught_pokemon(user_id, pikachu, 6, test_db)
    assert saved is True
    await end_active_battle(user_id, test_db)

    battle_ended = await get_active_battle(user_id, test_db)
    assert battle_ended is None
    print("Battle ended cleanly and caught Pikachu saved to user box!")

    if os.path.exists(test_db):
        os.remove(test_db)

    print("\n[SUCCESS] ALL FEATURE 3 TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_tests())
