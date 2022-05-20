import lightbulb, hikari
import random

from casinomania.functions.readWrite import readGuildFile, writeGuildFile
bjJoin = lightbulb.Plugin("bjJoin")


@bjJoin.listener(hikari.events.MemberCreateEvent)
async def joinEvent(event: hikari.events.MemberCreateEvent) -> None:
    # Filter out all unwanted interactions
    # print(event)
    # if not isinstance(event.interaction, hikari.ComponentInteraction):
    #     return

    print('New member joined')
    memberID = str(event.member.user.id)
    data = readGuildFile(event.guild_id)
    # data[str(memberID)] = memberID
    data[str(memberID)] = {'coins': 100, 'bet': 10}
    # data[str(memberID)]['bet'] = 10

    writeGuildFile(data, event.guild_id)


@bjJoin.listener(hikari.GuildJoinEvent)
async def joinedGuild(event: hikari.GuildJoinEvent):
    guildID = event.guild_id
    members = await event.app.rest.fetch_members(guildID)

    data = readGuildFile(event.guild_id)

    for member in members:
        if not member.is_bot:
            # print(member)
            data[str(member.user.id)] = {'coins': 100, 'bet': 10}

    writeGuildFile(data, guildID)


def load(bot: lightbulb.BotApp):
    print('loading listeners')
    bot.add_plugin(bjJoin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(bjJoin)