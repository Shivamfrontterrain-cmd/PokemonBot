import asyncio
import os
import aiosqlite
from database import init_db, get_user, get_user_starter, register_user_with_starter
from pokeapi import fetch_pokemon_data, get_starter_info


async def run_tests():
    test_db = "test_hexamonbot.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    print("--- 1. Testing Database Initialization ---")
    await init_db(test_db)
    print("Database initialized successfully.")

    print("\n--- 2. Testing PokéAPI Starter Fetching ---")
    bulbasaur = await fetch_pokemon_data(1)
    charmander = await fetch_pokemon_data(4)
    squirtle = await fetch_pokemon_data(7)
    
    assert bulbasaur["name"] == "Bulbasaur"
    assert charmander["name"] == "Charmander"
    assert squirtle["name"] == "Squirtle"
    print(f"Fetched starters: {bulbasaur['name']}, {charmander['name']}, {squirtle['name']}")
    print(f"Charmander stats: {charmander['stats']}")
    print(f"Charmander artwork URL: {charmander['image_url']}")

    print("\n--- 3. Testing Starter Registration for User 1001 ---")
    user_id = 1001
    username = "ash_ketchum"
    first_name = "Ash"

    success, msg = await register_user_with_starter(user_id, username, first_name, charmander, test_db)
    assert success is True, f"Registration failed: {msg}"
    print(f"Registration result: {msg}")

    print("\n--- 4. Testing DUPLICATE Selection Prevention ---")
    # User 1001 attempts to choose Bulbasaur second time
    success_dup, msg_dup = await register_user_with_starter(user_id, username, first_name, bulbasaur, test_db)
    assert success_dup is False, "ERROR: Duplicate selection was NOT prevented!"
    print(f"Duplicate prevention verified: {msg_dup}")

    print("\n--- 5. Testing Starter Retrieval ---")
    user = await get_user(user_id, test_db)
    assert user["starter_chosen"] == 1
    starter = await get_user_starter(user_id, test_db)
    assert starter["name"] == "Charmander"
    assert starter["level"] == 5
    assert starter["is_starter"] == 1
    print(f"Retrieved user starter: {starter['name']} (Lvl {starter['level']})")

    # Clean up test database
    if os.path.exists(test_db):
        os.remove(test_db)

    print("\n[SUCCESS] ALL FEATURE 1 TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_tests())
