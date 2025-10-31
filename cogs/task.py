import discord
from discord.ext import commands, tasks
import json
import asyncio

# --- Variables y Funciones de Ayuda ---
with open('config.json', 'r') as f:
    config = json.load(f)

MUDAE_ID = config['mudae_id']

def save_config():
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Flags de estado para el KL
        self.kl_is_running = False
        self.kl_pins_full = False
        # Iniciamos las tareas
        self.daily_task.start()
        self.pokeslot_task.start()
        self.arlp_task.start()
        self.kakera_loot_manager_task.start() # Nueva tarea administradora

    def cog_unload(self):
        self.daily_task.cancel()
        self.pokeslot_task.cancel()
        self.arlp_task.cancel()
        self.kakera_loot_manager_task.cancel()
    
    # --- TAREAS EN BUCLE (Daily, Pokeslot, Arlp se mantienen igual) ---
    @tasks.loop(hours=20, minutes=5)
    async def daily_task(self):
        if config['tasks']['daily_enabled']:
            channel = self.bot.get_channel(int(config['channel_id']))
            if channel:
                await channel.send("$daily")
                print("Tarea: Comando $daily enviado.")
    
    @tasks.loop(hours=2, minutes=2)
    async def pokeslot_task(self):
        if config['tasks']['pokeslot_enabled']:
            channel = self.bot.get_channel(int(config['tasks']['kl_channel_id']))
            if channel:
                await channel.send("$p")
                print("Tarea: Comando $pokeslot enviado.")

    @tasks.loop(seconds=91)
    async def arlp_task(self):
        if config['tasks']['arlp_enabled']:
            # Si el ARLP está habilitado, también resetea la flag de pins llenos
            if self.kl_pins_full:
                print("Tarea ARLP: Los pins estaban llenos. Se asume que $arlp los limpiará.")
                self.kl_pins_full = False
            
            channel = self.bot.get_channel(int(config['tasks']['kl_channel_id']))
            if channel:
                await channel.send("$arlp")
                print("Tarea: Comando $arlp enviado.")

    # --- LÓGICA PARA KAKERALOOT ---

    @tasks.loop(seconds=5)
    async def kakera_loot_manager_task(self):
        # Condiciones para ejecutar un ciclo de KL:
        # 1. La tarea debe estar habilitada en el config.
        # 2. No debe haber ya un ciclo de KL en ejecución.
        # 3. No debemos estar bloqueados por el límite de pins.
        if config['tasks']['kl_enabled'] and not self.kl_is_running and not self.kl_pins_full:
            self.kl_is_running = True
            await self.execute_kl_cycle()
            self.kl_is_running = False

    async def execute_kl_cycle(self):
        """Ejecuta un único ciclo de $kl y maneja las respuestas y cooldowns."""
        kl_amount = config['tasks']['kl_amount']
        channel_id = int(config['tasks'].get('kl_channel_id', config['channel_id']))
        channel = self.bot.get_channel(channel_id)

        if not channel:
            print("Error KL: Canal de Kakeraloot no encontrado.")
            return

        # 1. Enviar el comando $kl
        await channel.send(f"$kl {kl_amount}")
        print(f"Tarea: Comando $kl {kl_amount} enviado al canal {channel.name}.")

        def check(message):
            # Comprobación de múltiples posibles respuestas de Mudae
            return (message.author.id == MUDAE_ID and
                    message.channel == channel and
                    (f"¿Quieres gastar" in message.content or
                     "Error:" in message.content or
                     "Te faltan" in message.content or
                     "Do you want" in messag.content))

        try:
            # 2. Esperar la respuesta de Mudae
            response_message = await self.bot.wait_for('message', check=check, timeout=10.0)

            # 3. Analizar la respuesta y actuar
            if f"¿Quieres gastar" in response_message.content:
                await channel.send("y")
                print("Tarea KL: Confirmación 'y' enviada.")
            
            elif f"Do you want" in response_message.content:
                await channel.send("y")
                print("Tarea KL: Confirmación 'y' enviada.")
            
            elif "Error:" in response_message.content:
                print("Tarea KL: Límite de pins alcanzado. Pausando KL hasta el próximo $arlp.")
                self.kl_pins_full = True # Activamos la flag para detener los intentos
            
            elif "Te faltan" in response_message.content:
                print("Tarea KL: Kakera insuficiente. Desactivando la tarea de KL.")
                config['tasks']['kl_enabled'] = False
                save_config()

        except asyncio.TimeoutError:
            # Si no hay respuesta, asumimos que el KL fue exitoso (no pidió confirmación)
            print("Tarea KL: No se recibió respuesta especial de Mudae (timeout). Asumiendo éxito.")

        # 4. Calcular y esperar el cooldown dinámico
        cooldown = 0
        if 1 <= kl_amount <= 99:
            cooldown = 3.6 # Cooldown de Discord
        elif 100 <= kl_amount <= 999:
            cooldown = 15
        elif 1000 <= kl_amount <= 12000:
            cooldown = 60
        
        if cooldown > 0:
            print(f"Tarea KL: Esperando {cooldown} segundos de cooldown.")
            await asyncio.sleep(cooldown)

    # Antes de que se inicien los bucles, esperamos a que el bot esté listo
    @daily_task.before_loop
    @pokeslot_task.before_loop
    @arlp_task.before_loop
    @kakera_loot_manager_task.before_loop
    async def before_all_tasks(self):
        await self.bot.wait_until_ready()

    # --- COMANDOS PARA CONTROLAR LAS TAREAS ---

    @commands.command()
    async def task(self, ctx, task_name: str, state: str):
        """
        Enciende o apaga una tarea específica.
        Uso: !task [daily|pokeslot|arlp|kl] [on|off]
        """
        task_name = task_name.lower()
        if f"{task_name}_enabled" not in config['tasks']:
            await ctx.send("Nombre de tarea inválido.")
            return

        if state.lower() == 'on':
            config['tasks'][f"{task_name}_enabled"] = True
            await ctx.send(f"✅ **Tarea '{task_name}' activada.**")
        elif state.lower() == 'off':
            config['tasks'][f"{task_name}_enabled"] = False
            await ctx.send(f"❌ **Tarea '{task_name}' desactivada.**")
        else:
            await ctx.send("Estado inválido. Opciones: `on` o `off`.")
        
        save_config()


    @commands.command()
    async def setkl(self, ctx, amount: int):
        """
        Cambia la cantidad de kakera a usar en el comando $kl.
        Uso: !setkl [cantidad]
        """
        if 1 <= amount <= 12000:
            config['tasks']['kl_amount'] = amount
            save_config()
            await ctx.send(f"✅ **Cantidad de $kl actualizada a {amount}.**")
        else:
            await ctx.send("❌ Cantidad inválida. El valor debe estar entre 1 y 12000.")

    @commands.command()
    async def setklchannel(self, ctx, kl_channel_id: str):
        """Cambia el canal donde el bot opera."""
        config['tasks']['kl_channel_id'] = kl_channel_id
        save_config()
        await ctx.send(f"✅ Canal actualizado a: **{kl_channel_id}**")

    @commands.command()
    async def ping(self, ctx):
        """Comando para verificar si el bot esta activo"""
        await ctx.send("Pong! 🍉")

# --- FUNCIÓN SETUP PARA CARGAR EL COG ---
async def setup(bot):

    await bot.add_cog(TasksCog(bot))
