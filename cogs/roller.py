# --- IMPORTS ---
import discord
from discord.ext import commands, tasks
from discord.enums import InteractionType
from curses import version
import json
import asyncio
import re
import time
from datetime import datetime

# --- Variables y Funciones de Ayuda ---

with open('config.json', 'r') as f:
    config = json.load(f)

MUDAE_ID = config['mudae_id']

def save_config():
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

class RollerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_rolling_session_active = False # Flag
        self.claim_available = True
        self.session_roll_count = 0
        self.kakera_cooldown_until = 0
        self.hourly_roller_task.start()


    # --- TAREA EN BUCLE PARA ROLLS HORARIOS ---

    @tasks.loop(hours=1)
    async def hourly_roller_task(self):
        """Tarea principal que se ejecuta una vez por hora para iniciar los rolls."""
        if not config.get('auto_roller_enabled', False):
            return

        if self.is_rolling_session_active:
            print("Intento de inicio de rolls, pero una sesión ya está activa.")
            return
            
        self.is_rolling_session_active = True
        channel = self.bot.get_channel(int(config['channel_id']))
        if channel:
            await self.start_roll_session(channel, config['max_rolls_per_session'])
        
        # Al terminar la sesión, reseteamos la flag
        self.is_rolling_session_active = False

    @hourly_roller_task.before_loop
    async def before_hourly_task(self):
        """Espera a que el bot esté listo y calcula el tiempo hasta el próximo minuto designado."""
        await self.bot.wait_until_ready()
        
        now = datetime.now()
        target_minute = int(config.get('repeat_minute', 0))
        
        # Calculamos los segundos hasta el próximo minuto designado
        if now.minute >= target_minute:
            # Si ya pasó el minuto de esta hora, esperamos hasta la siguiente hora
            next_hour = (now.hour + 1) % 24
            wait_seconds = ( (next_hour - now.hour -1) * 3600 ) + ( (60 - now.minute + target_minute) * 60 ) - now.second
        else:
            wait_seconds = (target_minute - now.minute) * 60 - now.second

        print(f"Esperando {wait_seconds / 60:.2f} minutos para el primer ciclo de rolls.")
        await asyncio.sleep(wait_seconds)


    # --- FUNCIÓN PRINCIPAL PARA LA SESIÓN DE ROLLS ---

    async def start_roll_session(self, channel, amount):
        print(f"Iniciando sesión de {amount} rolls en el canal {channel.name}.")
        self.session_roll_count = 0

        for i in range(amount):
            self.session_roll_count += 1
            if i > 0 and i % 15 == 0:
                print(f"--- Pausa estratégica después de {i} rolls. ---")
                await asyncio.sleep(10)
            
            try:
                await channel.send(f"${config['roll_command']}")
            except Exception as e:
                print(f"Error al enviar el comando slash: {e}")

            await asyncio.sleep(3.5) # Espera entre rolls

    # --- LISTENER DE MENSAJES ---

    @commands.Cog.listener()
    async def on_message(self, message):
        # Escuchamos solo a Mudae en el canal correcto
        if message.author.id != MUDAE_ID or str(message.channel.id) != config['channel_id']:
            return

        # Comprobamos si es un mensaje de reseteo de claims
        # ---  SE DEBE MEJORAR ESTA PARTE  ---
        if "Your claims reset" in message.content and f"<@{self.bot.user.id}>" in message.content:
            self.claim_available = True
            print("Claims reseteados. El próximo ciclo de rolls podrá reclamar.")
            return

        if message.embeds:
            # --- LÓGICA DE EXTRACCIÓN DE DATOS RESTAURADA ---
            try:
                embed = message.embeds[0]
                cardName = embed.author.name
                description = embed.description
                parts = description.replace('\n', '**').split('**')
                cardSeries = parts[0]
                cardPower = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            except (AttributeError, IndexError, KeyError, ValueError):
                return

            is_unclaimed = embed.footer.text is None

            if is_unclaimed:
                print(f"{self.session_roll_count} - [UNCLAIMED] ---- {cardPower} - {cardName} - {cardSeries}")
            else:
                print(f"{self.session_roll_count} - [CLAIMED] ---- {cardPower} - {cardName} - {cardSeries}")

            if is_unclaimed and self.claim_available:
                claim_reason = None
                if cardName in config['desired_characters']:
                    claim_reason = f"PERSONAJE DESEADO: {cardName}"
                elif cardSeries in config['desired_series']:
                    claim_reason = f"PERSONAJE DE SERIE DESEADA: {cardName}"

                if claim_reason:
                    print(claim_reason)
                    await message.add_reaction("🍉")
                    self.claim_available = False # Marcamos que ya no podemos reclamar
                    # No detenemos el bucle de rolls, solo esta flag

            # --- Logica de claim de kakera ---
            # --- LÓGICA DE KAKERA REFORZADA ---
            try:
                if time.time() < self.kakera_cooldown_until:
                    return
    
                if not message.components:
                    return # Si no hay botones, no hay nada que hacer
    
                # Iteramos a través de las filas de botones
                for action_row in message.components:
                    # Iteramos a través de los botones en esa fila
                    for component in action_row.children:
                        # Nos aseguramos de que sea un botón y tenga un emoji
                        if isinstance(component, discord.Button) and component.emoji:
                            
                            # --- PASO DE DEPURACIÓN ---
                            # Imprimimos el nombre del emoji que el bot está viendo
                            print(f"  -> Botón detectado con emoji: '{component.emoji.name}'")
    
                            if component.emoji.name in config['desired_kakeras']:
                                print(f"  ✅ COINCIDENCIA ENCONTRADA! Intentando reaccionar a {component.emoji.name} de {cardName}")
                                
                                await component.click()
                                
                                def check(m):
                                    return m.author.id == MUDAE_ID and m.channel == message.channel and "No puedes reaccionar a kakera antes de" in m.content
    
                                try:
                                    cooldown_msg = await self.bot.wait_for('message', check=check, timeout=2.0)
                                    match = re.search(r"antes de (\d+) mi\.", cooldown_msg.content)
                                    if match:
                                        minutes = int(match.group(1))
                                        cooldown_seconds = minutes * 60 + 5
                                        self.kakera_cooldown_until = time.time() + cooldown_seconds
                                        print(f"!!! COOLDOWN DE KAKERA DETECTADO. Desactivado por {minutes} minutos. !!!")
                                        return 
                                except asyncio.TimeoutError:
                                    pass # Éxito, no hubo mensaje de cooldown
    
                            # --- FIN DE LA LÓGICA ---
            except Exception as e:
                # Atrapamos cualquier otro error para que el bot no se detenga
                print(f"!! Error inesperado en la lógica de kakera: {e} !!")


    # --- COMANDOS DE CONTROL ---

    @commands.command()
    async def autoroll(self, ctx, state: str):
        """Enciende o apaga el auto-roller. Uso: !autoroll on/off"""
        if state.lower() == 'on':
            config['auto_roller_enabled'] = True
            await ctx.send("✅ **Auto-roller encendido.**")
        elif state.lower() == 'off':
            config['auto_roller_enabled'] = False
            await ctx.send("❌ **Auto-roller apagado.**")
        else:
            await ctx.send("Uso inválido. Opciones: `on` o `off`.")
        save_config()

    @commands.command()
    async def setchannel(self, ctx, channel_id: str):
        """Cambia el canal donde el bot opera."""
        config['channel_id'] = channel_id
        save_config()
        await ctx.send(f"✅ Canal actualizado a: **{channel_id}**")

    @commands.command()
    async def setserver(self, ctx, server_id: str):
        """Cambia el servidor donde el bot opera."""
        config['server_id'] = server_id
        save_config() # Corregido: se llama como función
        await ctx.send(f"✅ Servidor actualizado a: **{server_id}**")
        
    @commands.command()
    async def setminute(self, ctx, minute: int):
        """Define en qué minuto de la hora se inician los rolls (0-59)."""
        if 0 <= minute <= 59:
            config['repeat_minute'] = str(minute)
            save_config()
            await ctx.send(f"✅ Minuto de roll actualizado a **:{minute:02d}**. Reinicia el bot para aplicar el nuevo horario.")
        else:
            await ctx.send("El minuto debe estar entre 0 y 59.")


async def setup(bot):
    await bot.add_cog(RollerCog(bot))
