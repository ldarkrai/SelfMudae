import discord
from discord.ext import commands
from flask import Flask
import json
import threading
import asyncio

# --- 1. CONFIGURATION AND SETUP ---

# LOAD CONFIG
with open('config.json', 'r') as f:
    config = json.load(f)

# BOT'S INSTANCE
bot = commands.Bot(command_prefix='+', self_bot=True)

# FLASK'S INSTANCE
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return 

# --- 2. LOGIC  ---

@bot.event
async def on_ready():
    print(f'Conectado como {bot.user.name}')
    # Load modules
    cogs_to_load = ['cogs.roller', 'cogs.task']

    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f'Module {cog} load.')
        except Exception as e:
            print(f'Error with module {cog}: {e}')
    print("Módulos (Cogs) cargados correctamente.")

# --- 3. EJECUTION ---

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

async def run_bot():
    await bot.start(config['token'])

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Servidor Flask iniciado en un hilo separado.")
    print("Iniciando el bot de Discord...")
    asyncio.run(run_bot())