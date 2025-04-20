import logging
import logging.config
import warnings
from pyrogram import Client, __version__, idle
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from pytz import timezone
from datetime import datetime
import asyncio
from plugins.web_support import web_server
import pyromod
import os
import importlib.util

# DEBUG LOGGING FOR PLUGIN LOADS
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="SnowRenamer",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},  # Automatically load plugins
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()

        # Log plugin loading manually (optional, detailed debug)
        plugin_dir = "plugins"
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py"):
                path = os.path.join(plugin_dir, filename)
                module_name = f"plugins.{filename[:-3]}"
                try:
                    spec = importlib.util.spec_from_file_location(module_name, path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    logging.info(f"✅ Loaded plugin: {filename}")
                except Exception as e:
                    logging.error(f"❌ Failed to load plugin {filename}: {e}")

        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        self.force_channel = Config.FORCE_SUB

        if Config.FORCE_SUB:
            try:
                link = await self.export_chat_invite_link(Config.FORCE_SUB)
                self.invitelink = link
            except Exception as e:
                logging.warning(e)
                logging.warning("Make sure the bot is admin in the force sub channel.")
                self.force_channel = None

        # Start web server
        runner = web.AppRunner(await web_server())
        await runner.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(runner, bind_address, Config.PORT).start()

        logging.info(f"{me.first_name} ✅✅ BOT started successfully ✅✅")

        try:
            await self.send_message(Config.OWNER, f"**__{me.first_name} is Started.....✨️__**")
        except:
            pass

        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"**__{me.mention} is Restarted !!**\n\n📅 Date : `{date}`\n⏰ Time : `{time}`\n🌐 Timezone : `Asia/Kolkata`\n\n🉐 Version : `v{__version__} (Layer {layer})`"
                )
            except:
                print("Please make sure the bot is admin in your log channel.")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")


bot_instance = Bot()

def main():
    warnings.filterwarnings("ignore", message="There is no current event loop")

    async def start_bot():
        await bot_instance.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    loop.run_forever()

if __name__ == "__main__":
    main()
