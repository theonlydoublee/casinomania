import hikari
import lightbulb

from casinomania.functions import createImages

pingPL = lightbulb.Plugin("pingPL")


# region Ping Pong
@pingPL.command()
@lightbulb.command("ping", "Says 'pong!'")
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_ping(ctx: lightbulb.context):
    # await pingPL.bot.rest.create_message(ctx.channel_id, "Create New Message")

    await createImages.cards_image(['2_of_clubs.png', '3_of_diamonds.png', '5_of_spades.png'])

    await ctx.respond('Pong!')
# endregion


def load(bot: lightbulb.BotApp):
    bot.add_plugin(pingPL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(pingPL)

