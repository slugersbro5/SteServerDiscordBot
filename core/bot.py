import logging
import os

import aiohttp
import discord

from discord import app_commands
from discord.ext import commands

from core.database import Database
from core.palworld_api import PalworldAPI
from core.palworld_service import PalworldService
from core.process_manager import ProcessManager


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
                "directory": os.getenv("PALWORLD_DIRECTORY"),
                "executable": os.getenv("PALWORLD_EXECUTABLE"),
            },
        }

        self._validate_config()

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

        self.http_session: aiohttp.ClientSession | None = None

    def _validate_config(self):

        required = [
            ("DISCORD_TOKEN", self.config["discord_token"]),
            ("PALWORLD_HOST", self.config["palworld"]["host"]),
            ("PALWORLD_USERNAME", self.config["palworld"]["username"]),
            ("PALWORLD_PASSWORD", self.config["palworld"]["password"]),
            ("PALWORLD_DIRECTORY", self.config["palworld"]["directory"]),
            ("PALWORLD_EXECUTABLE", self.config["palworld"]["executable"]),
        ]

        missing = [
            name
            for name, value in required
            if not value
        ]

        if missing:

            raise ValueError(
                "Missing required environment variables:\n"
                + "\n".join(missing)
            )

    async def setup_hook(self):

        self.logger.info("Initializing HTTP session...")

        self.http_session = aiohttp.ClientSession()

        self.logger.info("Initializing database...")

        self.database = Database()

        await self.database.initialize()

        self.logger.info("Database initialized.")

        self.logger.info("Creating Palworld services...")

        api = PalworldAPI(self)

        process_manager = ProcessManager(self)

        self.palworld = PalworldService(
            api,
            process_manager,
        )

        await self.load_cogs()

        await self.sync_commands()

        self.tree.on_error = self.on_app_command_error

        self.logger.info("Bot startup complete.")

    async def load_cogs(self):

        self.logger.info("Loading cogs...")

        for filename in sorted(os.listdir("cogs")):

            if not filename.endswith(".py"):

                continue

            cog = f"cogs.{filename[:-3]}"

            try:

                await self.load_extension(cog)

                self.logger.info(
                    f"Loaded cog: {cog}"
                )

            except Exception:

                self.logger.exception(
                    f"Failed loading cog: {cog}"
                )

    async def sync_commands(self):

        self.logger.info("Synchronizing slash commands...")

        try:

            synced = await self.tree.sync()

            self.logger.info(
                f"Synced {len(synced)} slash commands."
            )

        except Exception:

            self.logger.exception(
                "Failed syncing slash commands."
            )

    async def close(self):

        self.logger.info(
            "Closing HTTP session..."
        )

        if self.http_session:

            await self.http_session.close()

        await super().close()

    async def on_ready(self):

        self.logger.info(
            f"Logged in as {self.user} "
            f"(ID: {self.user.id})"
        )

        self.logger.info(
            f"Connected to {len(self.guilds)} guild(s)."
        )

    async def on_command_error(
        self,
        interaction: discord.Interaction,
        error,
    ):

        self.logger.exception(
            f"Command Error: {error}"
        )

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error,
    ):

        if isinstance(
            error,
            app_commands.CheckFailure,
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
                    ephemeral=True,
                )

            else:

                await interaction.response.send_message(
                    message,
                    ephemeral=True,
                )

        except Exception:

            self.logger.exception(
                "Failed to send error message."
            )