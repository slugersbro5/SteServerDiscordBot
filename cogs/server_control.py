import discord
import asyncio

from discord.ext import commands
from discord import app_commands

from core.permissions import is_server_admin
from core.logging_utils import send_log

class ServerControl(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    async def send_offline_message(
        self,
        interaction: discord.Interaction,
    ):
        """Send a consistent offline response."""

        await interaction.followup.send(
            "🔴 Palworld server is currently offline.",
            ephemeral=True,
        )    

    async def log_action(
        self,
        guild_id: int,
        title: str,
        requester: str,
        **fields,
    ):
        """Send an admin log embed."""

        embed = discord.Embed(
            title=title,
            timestamp=discord.utils.utcnow(),
        )

        embed.add_field(
            name="Requested By",
            value=requester,
            inline=False,
        )

        for name, value in fields.items():

            embed.add_field(
                name=name.replace("_", " ").title(),
                value=str(value),
                inline=False,
            )

        await send_log(
            self.bot,
            guild_id,
            embed,
        )
### Server Status Command ###
    @app_commands.command(
    name="serverstatus",
    description="Check Palworld server status"
)
    @is_server_admin()
    async def server_status(
        self,
        interaction: discord.Interaction
    ):

        self.bot.logger.info(
            f"Received /serverstatus from: {interaction.user}"
        )

        await interaction.response.defer(
            ephemeral=True
        )

        try:

            self.bot.logger.info(
                "Calling Palworld API"
            )

            info = await self.bot.palworld.get_info()

            if info is None:

                await self.send_offline_message(interaction)

                return

            self.bot.logger.info(
                f"Response: {info}"
            )

            await interaction.followup.send(
                str(info),
                ephemeral=True
            )

        except Exception as e:

            self.bot.logger.exception(
                f"Unexpected error: {e}"
            )

            await interaction.followup.send(
                "⚠️ An unexpected error occurred.",
                ephemeral=True
            )   
### Server Player Command ###            
    @app_commands.command(
    name="serverplayers",
    description="Show online Palworld players."
)
    @is_server_admin()
    async def server_players(
            self,
            interaction: discord.Interaction
        ):

            self.bot.logger.info(
                f"Received /serverplayers from: {interaction.user}"
            )

            await interaction.response.defer(
                ephemeral=True
            )

            try:

                players = await self.bot.palworld.get_players()

                if players is None:

                    await interaction.followup.send(
                        "🔴 Palworld server is currently offline.",
                        ephemeral=True
                    )

                    return

                player_list = players.get(
                    "players",
                    []
                )

                embed = discord.Embed(
                    title="🎮 Online Players"
                )

                embed.add_field(
                    name="Players Online",
                    value=str(len(player_list)),
                    inline=False
                )

                if player_list:

                    names = []

                    for player in player_list:

                        names.append(
                            player.get(
                                "name",
                                "Unknown"
                            )
                        )

                    embed.add_field(
                        name="Player List",
                        value="\n".join(
                            f"• {name}"
                            for name in names
                        )[:1024],
                        inline=False
                    )

                else:

                    embed.add_field(
                        name="Player List",
                        value="No players online.",
                        inline=False
                    )

                await interaction.followup.send(
                    embed=embed,
                    ephemeral=True
                )

            except Exception as e:

                self.bot.logger.exception(
                    f"Unexpected error: {e}"
                )

                await interaction.followup.send(
                    "⚠️ An unexpected error occurred.",
                    ephemeral=True
    
                )
### Server Save Command ###
    @app_commands.command(
    name="serversave",
    description="Save the Palworld world."
)
    @is_server_admin()
    async def server_save(
        self,
        interaction: discord.Interaction
    ):

        self.bot.logger.info(
            f"Received /serversave from: {interaction.user}"
        )

        await interaction.response.defer(
            ephemeral=True
        )

        try:

            result = await self.bot.palworld.save()

            if result is None:

                await interaction.followup.send(
                    "🔴 Palworld server is currently offline.",
                    ephemeral=True
                )

                return

            await interaction.followup.send(
                "💾 World save command sent successfully.",
                ephemeral=True
            )
            embed = discord.Embed(
    title="💾 World Save Initiated"
)

            embed.add_field(
                name="Requested By",
                value=interaction.user.mention,
                inline=False
            )

            await send_log(
                self.bot,
                interaction.guild.id,
                embed
)
        except Exception as e:

            self.bot.logger.exception(
                f"Unexpected error: {e}"
            )

            await interaction.followup.send(
                "⚠️ An unexpected error occurred.",
                ephemeral=True
            )

### Server Shutdown Command ###
    @app_commands.command(
    name="servershutdown",
    description="Shutdown the Palworld server."
)
    @is_server_admin()
    @app_commands.describe(
        wait_time="Seconds before shutdown",
        message="Message shown to players"
    )
    async def server_shutdown(
        self,
        interaction: discord.Interaction,
        wait_time: int = 30,
        message: str = "Server shutting down."
    ):

        self.bot.logger.info(
            f"Received /servershutdown from: {interaction.user}"
        )

        if wait_time < 0:

            await interaction.response.send_message(
                "❌ Wait time cannot be negative.",
                ephemeral=True
            )

            return

        if wait_time > 3600:

            await interaction.response.send_message(
                "❌ Maximum wait time is 3600 seconds.",
                ephemeral=True
            )

            return

        await interaction.response.defer(
            ephemeral=True
        )

        try:

            result = await self.bot.palworld.shutdown(
                wait_time,
                message
            )

            if result is None:

                await interaction.followup.send(
                    "🔴 Palworld server is currently offline.",
                    ephemeral=True
                )

                return

            embed = discord.Embed(
                title="🛑 Server Shutdown Initiated"
            )

            embed.add_field(
                name="Requested By",
                value=interaction.user.mention,
                inline=False
            )

            embed.add_field(
                name="Wait Time",
                value=f"{wait_time} seconds",
                inline=False
            )

            embed.add_field(
                name="Message",
                value=message,
                inline=False
            )

            await send_log(
                self.bot,
                interaction.guild.id,
                embed
            )

            await interaction.followup.send(
                (
                    f"🛑 Shutdown initiated.\n"
                    f"Server will stop in {wait_time} seconds."
                ),
                ephemeral=True
            )

        except Exception as e:

            self.bot.logger.exception(
                f"Unexpected error: {e}"
            )

            await interaction.followup.send(
                "⚠️ An unexpected error occurred.",
                ephemeral=True
            )
## Server Start Command ##
    @app_commands.command(
        name="serverstart",
        description="Start the Palworld server."
    )
    @is_server_admin()
    async def server_start(
        self,
        interaction: discord.Interaction
    ):

        self.bot.logger.info(
            f"Received /serverstart from: {interaction.user}"
        )

        await interaction.response.defer(
            ephemeral=True
        )

        try:

            info = await self.bot.palworld.get_info()

            if info is not None:

                await interaction.followup.send(
                    "🟢 Palworld server is already running.",
                    ephemeral=True
                )

                return

            await self.bot.palworld.start()

            embed = discord.Embed(
                title="🚀 Server Startup Initiated"
            )

            embed.add_field(
                name="Requested By",
                value=interaction.user.mention,
                inline=False
            )

            await send_log(
                self.bot,
                interaction.guild.id,
                embed
            )

            await interaction.followup.send(
                (
                    "🚀 Server startup initiated.\n"
                    "The server may take a minute to come online."
                ),
                ephemeral=True
            )

        except Exception as e:

            self.bot.logger.exception(
                f"Unexpected error: {e}"
            )

            await interaction.followup.send(
                "⚠️ An unexpected error occurred.",
                ephemeral=True
            )
## Server Restart Command ##
    @app_commands.command(
    name="serverrestart",
    description="Restart the Palworld server."
)
    @is_server_admin()
    @app_commands.describe(
        wait_time="Seconds before shutdown",
        message="Message shown to players"
    )
    async def server_restart(
        self,
        interaction: discord.Interaction,
        wait_time: int = 30,
        message: str = "Server restarting."
    ):

        self.bot.logger.info(
            f"Received /serverrestart from: {interaction.user}"
        )

        await interaction.response.defer(
            ephemeral=True
        )
    
        try:

            if not await self.bot.palworld.is_running():

                await interaction.followup.send(
                    "🔴 Palworld server is currently offline.",
                    ephemeral=True
                )

                return

            await interaction.followup.send(
                (
                    f"🔄 Restart initiated.\n"
                    f"Shutdown in {wait_time} seconds."
                ),
                ephemeral=True
            )

            asyncio.create_task(
                self.perform_restart(
                    interaction.guild.id,
                    interaction.user.mention,
                    wait_time,
                    message
                )
            )

        except Exception as e:

            self.bot.logger.exception(
                f"Unexpected error: {e}"
            )

            await interaction.followup.send(
                "⚠️ An unexpected error occurred.",
                ephemeral=True
            )
    async def perform_restart(
        self,
        guild_id,
        requester,
        wait_time,
        message
    ):

        try:

            self.bot.logger.info(
                "Beginning restart sequence."
            )

            await self.bot.palworld.save()

            await asyncio.sleep(5)

            await self.bot.palworld.shutdown(
                wait_time,
                message
            )

            await asyncio.sleep(
                wait_time + 30
            )

            await self.bot.palworld.start()

            embed = discord.Embed(
                title="🔄 Server Restart Completed",
                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="Requested By",
                value=requester,
                inline=False
            )
            embed.add_field(
                name="Wait Time",
                value=f"{wait_time} seconds",
                inline=False
            )
            embed.add_field(
                name="Message",
                value=message,
                inline=False
            )
            await send_log(
                self.bot,
                guild_id,
                embed
            )

            self.bot.logger.info(
                "Restart sequence completed."
            )

        except Exception as e:

            self.bot.logger.exception(
                f"Restart failed: {e}"
            )
async def setup(bot):
    await bot.add_cog(
        ServerControl(bot)
    )