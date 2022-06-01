import lightbulb, hikari
import random

from casinomania.functions.readWrite import readGuildFile, writeGuildFile

payMessage = lightbulb.Plugin("payMesage")


@payMessage.listener(hikari.events.GuildMessageCreateEvent)
async def joinEvent(event: hikari.events.GuildMessageCreateEvent) -> None:
    channel = payMessage.bot.cache.get_guild_channel(event.channel_id)
    # channel = await payMessage.bot.rest.fetch_channel(event.channel_id)
    if (not event.member.is_bot) and (channel.name.lower() == 'payments'):
        await event.message.delete()


def load(bot: lightbulb.BotApp):
    bot.add_plugin(payMessage)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(payMessage)
