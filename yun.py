import aiohttp
import os
os.system("pip install pyrogram asyncio re TgCrypto")
import asyncio
import re
from pyrogram import Client, filters
from functools import wraps

# Initialize Pyrogram client with increased workers and queue size
app = Client("Pokemon_bot", session_string="BQDCoasAWm2rJkz4_ePNJjhSV1cPUPgfuYbqD2uWY3ANC6ymTh2eRWWL_aoRwvvEjwhrhWGwwvrfxqFrPHQ2t4ZMXRGLgF4I9NWwHjW6BGh49KF9hFGF5cfcBx5HcobO9ioPdOA2jTyYAiXUYdHR0Hbqu5jIyLV5sPf-wrmNzM4cIHsjpVj7I0eocCzcOrVPpS5EzBsPoAZaW1P8TbWmJIwOtizreOnlIKDLBlAt4MDLxXeaM7uEKYZGDiWW0i5BolP-6AGkA8zCbLAXWAL2-QKO2y1s8V0YwKfSKXMU181KZNDOmL60CFt2uFqs8IlczheJtK_VCTtq8Hz8f1tv_cx2a0UkQAAAAGmo4A-AA", workers=10)

def cache(func):
    cache_dict = dict()
    @wraps(func)
    async def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache_dict:
            cache_dict[key] = await func(*args, **kwargs)
        return cache_dict[key]
    return wrapper

@cache
async def fetch_pokemon_names():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://pokeapi.co/api/v2/pokemon?limit=15100') as response:
            if response.status == 200:
                data = await response.json()
                return [pokemon['name'] for pokemon in data['results']]
            else:
                print("Failed to fetch Pokémon names")
                return []

async def normalize_name(name):
    return re.sub(r'[^a-zA-Z]', '', name)

async def filter_pokemon_names(names, hint):
    hint = hint.replace(' ', '')
    pattern = '^' + hint.replace('_', '.') + '$'
    regex = re.compile(pattern, re.IGNORECASE)
    print(f"Regex pattern: {pattern}") # 'Debug print'
    matching_names = []
    for name in names:
        normalized_name = await normalize_name(name)
        if regex.match(normalized_name):
            matching_names.append(name)
    return matching_names

async def process_hint(hint):
    pokemon_names = await fetch_pokemon_names()
    matching_names = await filter_pokemon_names(pokemon_names, hint)
    return matching_names

@app.on_message(filters.regex('Hint: (.*)'))
async def handle_hint_message(app, message):
    print("Received hint message!")
    hint = message.text.split("Hint: ")[1]
    result = await process_hint(hint)
    for name in result:
        await message.reply(name)

async def send_guess(chat_id):
    await asyncio.sleep(2)
    await app.send_message(chat_id, "/guess")

@app.on_message()
async def handle_other_messages(app, message):
    print(f"Received message: {message.text}")
    if message.text and "The pokemon was" in message.text:
        asyncio.create_task(send_guess(message.chat.id))
    else:
        print("Not Hint.")


app.run()
