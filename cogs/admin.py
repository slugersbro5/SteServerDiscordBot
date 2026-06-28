import discord

from discord.ext import commands
from discord import app_commands


class Admin(commands.Cog):

    setup_group = app_commands.Group(
        name="setup",
        description="Server configuration commands"
    )

    def __init__(self, bot):
        self.bot = bot

    @setup_group.command(
        name="adminrole",
        description="Set the role allowed to manage the server."
    )
    @app_commands.default_permissions(administrator=True)
    async def adminrole(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        await self.bot.database.set_admin_role(
            interaction.guild.id,
            role.id
        )

        await interaction.response.send_message(
            f"✅ Admin role set to {role.mention}",
            ephemeral=True
        )

    @setup_group.command(
        name="logchannel",
        description="Set the admin logging channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_logchannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        await self.bot.database.set_log_channel(
            interaction.guild.id,
            channel.id
        )

        await interaction.response.send_message(
            f"✅ Log channel set to {channel.mention}",
            ephemeral=True
        )
    

async def setup(bot):
    await bot.add_cog(
        Admin(bot)
    )