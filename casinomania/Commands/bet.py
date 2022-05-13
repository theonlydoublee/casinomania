import lightbulb, hikari

from casinomania.functions.readWrite import setBet, getBet, getCCTotal

betPL = lightbulb.Plugin('betPL')
SlashCommand = lightbulb.SlashCommand


@betPL.command()
@lightbulb.option('amount', 'Amount to bet', type=int, max_value=2000, min_value=1)
@lightbulb.command('bet', 'Set bet amount', ephemeral=True)
@lightbulb.implements(SlashCommand)
async def cmd_bet(ctx: lightbulb.context.Context):
    amount = ctx.options.amount
    guildID = ctx.guild_id
    userID = ctx.user.id
    maxBet = getCCTotal(guildID, userID)

    if amount > maxBet:
        setBet(guildID, userID, maxBet)
        await ctx.respond(f'Amount too high\nGoing all in at: {maxBet}')
    else:
        setBet(guildID, userID, amount)
        await ctx.respond(f'Now betting: {getBet(guildID, userID)}')


def load(bot: lightbulb.BotApp):
    bot.add_plugin(betPL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(betPL)
