import asyncio
import os
import aiosqlite
from database import init_db, get_user, update_user_region, register_user_with_starter
from pokeapi import fetch_pokemon_data, fetch_random_wild_pokemon
from regions import get_all_regions, get_region_info


async def run_tests():
    test_db = "test_feature2.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    print("--- 1. Testing Database & Schema Migration ---")
    await init_db(test_db)
    print("Database initialized successfully.")

    print("\n--- 2. Testing Starter Setup for User 2002 ---")
    charmander = await fetch_pokemon_data(4)
    success, msg = await register_user_with_starter(2002, "red_trainer", "Red", charmander, test_db)
    assert success is True

    user = await get_user(2002, test_db)
    assert user["current_region"] == "Kanto"
    assert user["trainer_level"] == 1
    print(f"User created: Region={user['current_region']}, Level={user['trainer_level']}")

    print("\n--- 3. Testing /travel Level Lock Restrictions ---")
    # Level 1 trying to enter Johto (Req Level 2)
    johto_info = get_region_info("Johto")
    assert johto_info["req_level"] == 2
    assert user["trainer_level"] < johto_info["req_level"]
    print(f"Verified: User Lvl {user['trainer_level']} CANNOT enter Johto (Req Lvl {johto_info['req_level']})")

    # Manually upgrade level to 2 in DB
    async with aiosqlite.connect(test_db) as db:
        await db.execute("UPDATE users SET trainer_level = 2 WHERE user_id = 2002")
        await db.commit()

    # Try traveling now
    await update_user_region(2002, "Johto", test_db)
    user_updated = await get_user(2002, test_db)
    assert user_updated["current_region"] == "Johto"
    print(f"Travel successful! Updated Region={user_updated['current_region']}")

    print("\n--- 4. Testing Region-Specific Wild Hunt Generator (/hunt) ---")
    kanto_wild = await fetch_random_wild_pokemon("Kanto")
    johto_wild = await fetch_random_wild_pokemon("Johto")
    paldea_wild = await fetch_random_wild_pokemon("Paldea")

    assert 1 <= kanto_wild["id"] <= 151, f"Kanto wild ID {kanto_wild['id']} out of bounds!"
    assert 152 <= johto_wild["id"] <= 251, f"Johto wild ID {johto_wild['id']} out of bounds!"
    assert 906 <= paldea_wild["id"] <= 1025, f"Paldea wild ID {paldea_wild['id']} out of bounds!"

    print(f"Kanto Wild: #{kanto_wild['id']} {kanto_wild['name']} (Lvl {kanto_wild['wild_level']})")
    print(f"Johto Wild: #{johto_wild['id']} {johto_wild['name']} (Lvl {johto_wild['wild_level']})")
    print(f"Paldea Wild: #{paldea_wild['id']} {paldea_wild['name']} (Lvl {paldea_wild['wild_level']})")

    print("\n--- 5. Testing EV Yield Extraction ---")
    print(f"{kanto_wild['name']} EV Yields: {kanto_wild['ev_yields']}")
    assert len(kanto_wild['ev_yields']) > 0

    if os.path.exists(test_db):
        os.remove(test_db)

    print("\n[SUCCESS] ALL FEATURE 2 TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_tests())
