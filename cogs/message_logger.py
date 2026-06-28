import discord

from discord.ext import commands

from core.logging_utils import send_log


class MessageLogger(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(
        self,
        before,
        after
    ):

        if before.author.bot:
            return

        if before.content == after.content:
            return

        embed = discord.Embed(
            title="Message Edited"
        )

        embed.add_field(
            name="User",
            value=before.author.mention,
            inline=False
        )

        embed.add_field(
            name="Channel",
            value=before.channel.mention,
            inline=False
        )

        embed.add_field(
            name="Before",
            value=before.content[:1000] or "*empty*",
            inline=False
        )

        embed.add_field(
            name="After",
            value=after.content[:1000] or "*empty*",
            inline=False
        )
        embed.add_field(
            name="Message",
            value=f"[Jump to message]({after.jump_url})",
            inline=False
        )
        await send_log(
            self.bot,
            before.guild.id,
            embed
        )
    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message
    ):

        if message.author.bot:
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted"
        )

        embed.add_field(
            name="User",
            value=message.author.mention,
            inline=False
    )

        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=False
        )

        embed.add_field(
            name="Content",
            value=message.content[:1000] or "*empty*",
            inline=False
        )

        await send_log(
            self.bot,
            message.guild.id,
            embed
        )
    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):

        embed = discord.Embed(
            title="🟢 Member Joined"
        )

        embed.add_field(
            name="Member",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:F>",
            inline=False
        )

        await send_log(
            self.bot,
            member.guild.id,
            embed
        )

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):

        embed = discord.Embed(
            title="🔴 Member Left"
        )

        embed.add_field(
            name="Member",
            value=f"{member} ({member.id})",
            inline=False
        )

        await send_log(
            self.bot,
            member.guild.id,
            embed
        )
async def setup(bot):

    await bot.add_cog(
        MessageLogger(bot)
    )