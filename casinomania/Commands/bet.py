import lightbulb, hikari

from casinomania.functions.readWrite import setBet

betPL = lightbulb.Plugin('betPL')
SlashCommand = lightbulb.SlashCommand


@betPL.command()
@lightbulb.option('amount', 'Amount to bet', type=int, max_value=100, min_value=1)
@lightbulb.command('bet', 'Set bet amount')
@lightbulb.implements(SlashCommand)
async def cmd_bet(ctx: lightbulb.context.Context):
    await ctx.respond('test')


def load(bot: lightbulb.BotApp):
    bot.add_plugin(betPL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(betPL)
