import hikari
import lightbulb
import random

from casinomania.functions import createImages
from casinomania.functions.simpleFunctions import getCardName

pingPL = lightbulb.Plugin("pingPL")


# region Ping Pong
@pingPL.command()
@lightbulb.command("make2", "returns 2 cards")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_ping(ctx: lightbulb.context.Context):
    # await pingPL.bot.rest.create_message(ctx.channel_id, "Create New Message")

    # print(getCardName(random.choice(ctx.bot.d.cardValues), random.choice(ctx.bot.d.suits)))
    # print(getCardName())

    # cards = []
    #
    # for i in range(2):
    #     value = random.choice(ctx.bot.d.cardValues)
    #     suit = random.choice(ctx.bot.d.suits)
    #     card = getCardName(value, suit)
    #     cards.append(card)

    img = await createImages.cards_image(
        [await getCardName(random.choice(ctx.bot.d.cardValues), random.choice(ctx.bot.d.suits)) for i in range(10)],
        ctx.user.id)
    # img = await createImages.cards_image([ cards ], ctx.user.id)

    await ctx.respond('2 Cards', attachment=img)


# endregion


def load(bot: lightbulb.BotApp):
    bot.add_plugin(pingPL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(pingPL)
