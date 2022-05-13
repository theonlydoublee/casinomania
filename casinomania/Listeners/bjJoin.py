import lightbulb, hikari
import random

from casinomania.functions.readWrite import readGuildFile, writeGuildFile
bjJoin = lightbulb.Plugin("bjJoin")


@bjJoin.listener(hikari.events.MemberCreateEvent)
async def joinEvent(event: hikari.events.MemberCreateEvent) -> None:
    # Filter out all unwanted interactions
    print(event)
    # if not isinstance(event.interaction, hikari.ComponentInteraction):
    #     return

    memberID = event.member.user.id
    data = readGuildFile(event.guild_id)

    data[str(memberID)]['coins'] = 100
    data[str(memberID)]['bet'] = 10

    writeGuildFile(data, event.guild_id)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(bjJoin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(bjJoin)