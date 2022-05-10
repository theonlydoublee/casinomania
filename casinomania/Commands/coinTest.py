import hikari
import lightbulb
import random

from casinomania.functions import readWrite

from casinomania.functions import createImages
from casinomania.functions.simpleFunctions import getCardName, addCoins, remCoins

coinPL = lightbulb.Plugin("coinPL")


@coinPL.command()
@lightbulb.option('count', 'The amount of coins to add', type=int, min_value=1)
@lightbulb.command("add", "add coins to self")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_add(ctx: lightbulb.context.Context):
    count = ctx.options.count

    await addCoins(ctx.guild_id, ctx.user.id, count)

    totalData = readWrite.readGuildFile(ctx.guild_id)
    print(totalData)
    total = totalData[str(ctx.user.id)]

    await ctx.respond(f'Added {count} coins to you\nYou now have {total} coins')


@coinPL.command()
@lightbulb.option('count', 'The amount of coins to add', type=int, min_value=1)
@lightbulb.command("rem", "rem coins from self")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_rem(ctx: lightbulb.context.Context):
    count = ctx.options.count

    await remCoins(ctx.guild_id, ctx.user.id, count)

    totalData = readWrite.readGuildFile(ctx.guild_id)
    print(totalData)
    total = totalData[str(ctx.user.id)]

    await ctx.respond(f'Removed {count} coins from you\nYou now have {total} coins')


def load(bot: lightbulb.BotApp):
    bot.add_plugin(coinPL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(coinPL)
