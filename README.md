# By Ldarkrai
-----

# SelfMudae

`SelfMudae` es un bot de automatización (self-bot) para Discord, diseñado específicamente para interactuar con el popular bot Mudae. Su objetivo es automatizar el proceso de "rolling" (tiradas), reclamar personajes y series deseadas, y gestionar tareas repetitivas.

El bot funciona cargando módulos (Cogs) que se ejecutan en segundo plano:

  * **Roller (`cogs/roller.py`):** Gestiona las tiradas horarias, el reclamo de personajes y el "snipeo" de kakera.
  * **Tasks (`cogs/task.py`):** Gestiona tareas automáticas como `$daily`, `$pokeslot`, `$arlp` y `$kl`.

# Además, utiliza un servidor web [Flask](https://flask.palletsprojects.com/) básico que se ejecuta en un hilo separado. Esto es comúnmente usado para mantener el bot activo en plataformas de hosting gratuito (como Replit, Render, etc.).

-----

## ⚠️ ADVERTENCIA MUY IMPORTANTE ⚠️

Este proyecto es un **self-bot**. Su uso **viola los Términos de Servicio de Discord** porque automatiza una cuenta de usuario normal.

**El uso de este script puede resultar en la suspensión o el baneo permanente de tu cuenta de Discord.** Úsalo bajo tu propio y absoluto riesgo. El creador no se hace responsable de ninguna consecuencia negativa.

-----

## 🚀 Características Principales

  * **Auto-Roller Horario:** Inicia automáticamente una sesión de tiradas (`$wa`, `$ha`, etc.) cada hora en el minuto que especifiques.
  * **Auto-Claim de Personajes:** Reacciona automáticamente para reclamar personajes si aparecen sin dueño y están en tu lista de `desired_characters`.
  * **Auto-Claim de Series:** Reacciona para reclamar personajes de series que estén en tu lista de `desired_series`.
  * **Auto-Reacción de Kakera:** Intenta reaccionar automáticamente a los botones de kakera que estén definidos en `desired_kakeras` (por ejemplo, "kakeraP", "kakeraW").
  * **Gestión de Tareas:** Automatiza el envío de comandos como `$daily`, `$pokeslot` (`$p`), `$arlp`, y `$kl` (Kakera Loot) en intervalos definidos.
  * **Comandos de Control:** Te permite activar y desactivar las funciones automáticas y cambiar configuraciones clave directamente desde Discord.

-----

## ⚙️ Instalación y Configuración

### 1\. Requisitos Previos

  * [Python 3.8+](https://www.python.org/)
  * Las dependencias listadas en `requirements.txt`.

### 2\. Instalación

1.  Descarga o clona este repositorio.
2.  Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Renombra (si es necesario) y edita el archivo `config.json` para rellenar **todos** los campos.

### 3\. Obtener tu Token y los IDs

La configuración del `config.json` es la parte más importante.

  * **`token`**: Es tu token de autorización personal de Discord.
      * **¡NUNCA COMPARTAS ESTE TOKEN CON NADIE\!** Quien lo tenga, tiene control total de tu cuenta.
      * Puedes obtenerlo desde la consola de desarrollador de tu navegador (F12) en la pestaña "Network" (Red) mientras usas Discord web. Busca peticiones a `/api/v9/` y mira en los "Request Headers" (Encabezados de la petición) el valor de `authorization`.
  * **`mudae_id`**: Es el ID de usuario del bot Mudae en tu servidor. Por defecto suele ser `432610292342587392`.
  * **`server_id` y `channel_id`**: IDs del servidor y canal donde quieres que el bot opere.
  * **`kl_channel_id`**: (Opcional) ID del canal específico para las tareas de `$kl` y `$p`.

Para obtener cualquier ID en Discord, activa el "Modo de desarrollador" en `Ajustes > Avanzado` y luego haz clic derecho sobre un usuario, servidor o canal y selecciona "Copiar ID".

### 4\. Ejecutar el Bot

Una vez configurado, simplemente ejecuta el archivo `main.py`:

```bash
python main.py
```

Si todo está correcto, verás mensajes en la consola indicando que el bot se ha conectado y los módulos (Cogs) se han cargado.

-----

## 🔧 Explicación del `config.json`

Este archivo es el cerebro de tu bot.

| Clave | Descripción |
| :--- | :--- |
| **`token`** | Tu token de autorización de Discord. **MANTENER SECRETO.** |
| **`mudae_id`** | El ID de usuario del bot Mudae. |
| **`server_id`** | El ID del servidor donde se harán los rolls. |
| **`channel_id`** | El ID del canal principal para los rolls. |
| **`auto_roller_enabled`** | `true` para activar el auto-roller, `false` para desactivarlo. |
| **`roll_command`** | El comando de roll que usas (ej. "wa", "ha", "wg", "hg"). |
| **`repeat_minute`** | El minuto de cada hora en que el bot comenzará a rolear (ej. "15" para las XX:15). |
| **`max_rolls_per_session`** | Número máximo de rolls que el bot hará en cada sesión horaria. |
| **`desired_series`** | Una lista de nombres de series. El bot intentará reclamar cualquier personaje de estas series. |
| **`desired_characters`** | Una lista de nombres de personajes específicos que el bot intentará reclamar. |
| **`desired_kakeras`** | Una lista de tipos de kakera que el bot intentará reaccionar (ej. "kakeraP", "kakeraW"). |
| **`tasks`** | Un objeto para activar o desactivar las tareas automáticas (`daily`, `pokeslot`, `arlp`, `kl`). |
| **`kl_channel_id`** | El ID del canal donde se usarán los comandos `$kl` y `$p`. |
| **`kl_amount`** | La cantidad de kakera a gastar en cada comando `$kl`. |

-----

## 🤖 Comandos de Control

Puedes controlar el bot enviando mensajes en cualquier canal donde estés (el bot se escucha a sí mismo). El prefijo por defecto es `+`.

### Módulo Roller (`cogs/roller.py`)

  * `+autoroll [on/off]`
    Activa o desactiva el auto-roller principal.

  * `+setchannel [ID_del_canal]`
    Cambia el canal principal de operación (para rolls).

  * `+setserver [ID_del_servidor]`
    Cambia el servidor principal de operación.

  * `+setminute [minuto]`
    Establece el minuto (0-59) en el que comenzarán los rolls horarios. (Requiere reinicio para aplicar).

### Módulo Tasks (`cogs/task.py`)

  * `+task [nombre_tarea] [on/off]`
    Activa o desactiva una tarea específica.

      * *Nombres de tarea:* `daily`, `pokeslot`, `arlp`, `kl`.

  * `+setkl [cantidad]`
    Establece la cantidad de kakera a usar en el comando `$kl` (1-12000).

  * `+setklchannel [ID_del_canal]`
    Establece el canal para las tareas de `$kl` y `$p`.

  * `+ping`
    Comprueba si el bot está activo. Debería responder "Pong\! 🍉".

-----

## 🚫 Posibles Errores y Soluciones

1.  **¡Baneo de Cuenta\!**

      * **Error:** Tu cuenta ha sido desactivada.
      * **Causa:** Has sido detectado usando un self-bot, lo cual viola los ToS de Discord.
      * **Solución:** No hay solución. **Este es el riesgo principal y es permanente.**

2.  **El bot no se inicia (Error de Token).**

      * **Error:** `Improper token has been passed.`
      * **Solución:** El `token` en tu `config.json` es incorrecto o ha expirado. Vuelve a obtenerlo y pégalo correctamente.

3.  **El bot está online pero no rolea ni reacciona.**

      * **Causa 1:** Los IDs (`mudae_id`, `server_id`, `channel_id`) en `config.json` son incorrectos.
      * **Solución 1:** Asegúrate de haber copiado los IDs correctos usando el Modo Desarrollador.
      * **Causa 2:** `auto_roller_enabled` está en `false`.
      * **Solución 2:** Usa el comando `+autoroll on`.

4.  **El bot no reacciona al kakera o no reclama personajes.**

      * **Causa:** Mudae ha actualizado la forma en que muestra sus mensajes (embeds) o botones.
      * **Solución:** Este bot depende de la estructura de los mensajes de Mudae. Si Mudae cambia, el código de `cogs/roller.py` (específicamente la función `on_message`) necesita ser actualizado para parsear la nueva estructura.

5.  **El bot deja de funcionar después de un tiempo (Hosting).**

      * **Causa:** La plataforma de hosting gratuito (como Replit) ha detenido tu proceso.
      * **Solución:** El servidor Flask en `main.py` está diseñado para prevenir esto, pero es posible que necesites un servicio de "uptime pinger" (como UptimeRobot) que haga peticiones a la URL de tu bot Flask cada pocos minutos para mantenerlo despierto.

6.  **Confusión de Prefijo de Comandos.**

      * **Causa:** El archivo `main.py` define el prefijo como `+`, pero la documentación interna de los cogs (docstrings) menciona `!`.
      * **Solución:** El prefijo correcto para los comandos es `+`, tal como se define en `main.py`.

-----

## 💡 Próximas Mejoras

Este proyecto es una base y se puede mejorar. Las siguientes son ideas para futuras actualizaciones:

  * **Mejorar la lógica de reclamo:** La lógica de `on_message` puede ser optimizada para manejar mejor los "resets" de claims y evitar reaccionar si los claims no están disponibles.
  * **Manejo de Errores Avanzado:** Implementar un mejor registro (logging) de errores para depurar más fácilmente por qué un reclamo o una tarea falló.
  * **Interfaz Web:** Usar el servidor Flask para algo más que el uptime, como un pequeño panel de control para ver estadísticas o cambiar la configuración.
  * **Evitar Detección:** Implementar patrones de espera (sleep) más aleatorios entre acciones para simular un comportamiento humano y reducir (aunque no eliminar) el riesgo de detección.

-----

## 📦 Dependencias

  * [discord.py-self](https://pypi.org/project/discord.py-self/)
  * [Flask](https://pypi.org/project/Flask/)
