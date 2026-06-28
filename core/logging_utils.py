import discord


async def send_log(
    bot,
    guild_id: int,
    embed: discord.Embed
):

    channel_id = await bot.database.get_log_channel(
        guild_id
    )

    if not channel_id:
        return

    channel = bot.get_channel(channel_id)

    if not channel:
        return

    await channel.send(
        embed=embed
    )