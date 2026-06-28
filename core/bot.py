import aiohttp
import logging
import os
import discord

from core.palworld_api import PalworldAPI
from discord.ext import commands
from discord import app_commands
from core.database import Database

class ServerBot(commands.Bot):

    def __init__(self):
        
        self.logger = logging.getLogger("ServerBot")
       

        self.config = {
        "discord_token": os.getenv("DISCORD_TOKEN"),

    "palworld": {
        "host": os.getenv("PALWORLD_HOST"),
        "port": int(os.getenv("PALWORLD_PORT", 8212)),
        "username": os.getenv("PALWORLD_USERNAME"),
        "password": os.getenv("PALWORLD_PASSWORD"),
        "start_script": os.getenv("PALWORLD_START_SCRIPT")
    }
}
        if not self.config["discord_token"]:
            raise ValueError(
        "DISCORD_TOKEN missing from .env"
    )
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents
        )
        self.http_session = None
    async def setup_hook(self):
        self.http_session = aiohttp.ClientSession()
        self.palworld = PalworldAPI(self)
        self.database = Database()
        await self.database.initialize()
        self.logger.info(
            "Initialized database connection."
        )
        cogs = []
        for filename in os.listdir("cogs"):

            if filename.endswith(".py"):

                cog_name = f"cogs.{filename[:-3]}"

                cogs.append(cog_name)

        for cog in cogs:

            try:
                await self.load_extension(cog)

                self.logger.info(
                    f"Loaded cog: {cog}"
                )

            except Exception:
                self.logger.exception(
                    f"Failed loading cog: {cog}"
                )

        try:
           
            synced = await self.tree.sync()

            self.logger.info(
                f"Synced {len(synced)} slash commands."
            )

        except Exception:
            self.logger.exception(
                "Failed syncing slash commands."
            )

        self.tree.on_error = self.on_app_command_error
    async def close(self):
        self.logger.info("Closing HTTP session...")
        if self.http_session:
            await self.http_session.close()

        await super().close()
    async def on_ready(self):

        self.logger.info(
            f"Logged in as {self.user} "
            f"(ID: {self.user.id})"
        )

        self.logger.info(
            f"Connected to {len(self.guilds)} guild(s)"
        )

    async def on_command_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        self.logger.exception(
            f"Command Error: {error}"
        )

    async def on_app_command_error(
    self,
    interaction: discord.Interaction,
    error
):

        if isinstance(
        error,
        app_commands.CheckFailure
    ):

            message = (
            "❌ You do not have permission "
            "to use this command."
        )

        else:

            self.logger.exception(
            f"Slash Command Error: {error}"
        )

            message = (
            "⚠️ An unexpected error occurred."
        )

        try:

         if interaction.response.is_done():

            await interaction.followup.send(
                message,
                ephemeral=True
            )

         else:

            await interaction.response.send_message(
                message,
                ephemeral=True
            )

        except Exception:
            self.logger.exception("Failed to send error message.")