import logging
import discord
from discord import app_commands


def is_server_admin():

    async def predicate(
        interaction: discord.Interaction
    ):

        bot = interaction.client

        role_id = await bot.database.get_admin_role(
            interaction.guild.id
        )

        if role_id is None:

            if interaction.user.guild_permissions.administrator:
                return True

            raise app_commands.CheckFailure(
                "No admin role has been configured."
            )

        user_role_ids = [
            role.id
            for role in interaction.user.roles
        ]

        if role_id in user_role_ids:
            return True

        logging.getLogger(
            "ServerBot"
        ).warning(
            f"{interaction.user} attempted "
            f"an admin command."
        )

        raise app_commands.CheckFailure(
            "Admin role required."
        )

    return app_commands.check(predicate)