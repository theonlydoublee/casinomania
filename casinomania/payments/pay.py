import lightbulb, hikari
from lightbulb.ext import tasks
import lightbulb, hikari
import os
import datetime
from casinomania.functions.readWrite import setBet, getBet, getCCTotal, readGuildFile
from casinomania.functions.simpleFunctions import remCoins, addCoins

payPlugin = lightbulb.Plugin("leaderboardupdater")


@payPlugin.command()
@lightbulb.option('amount', 'amount to send', type=int, required=True, min_value=1)
@lightbulb.option('user', 'user to send CC to', type=hikari.User, required=True)
@lightbulb.command('pay', 'Send CC to another user')
@lightbulb.implements(lightbulb.SlashCommand)
async def cmd_pay(ctx: lightbulb.Context):

    user = ctx.options.user
    amount = ctx.options.amount
    maxPay = getCCTotal(ctx.guild_id, ctx.user.id)

    if ctx.options.user.is_bot:
        await ctx.respond("Can't pay a bot", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if ctx.user.id == ctx.options.user.id:
        await ctx.respond("Can't pay yourself", flags=hikari.MessageFlag.EPHEMERAL)
        return
    if amount > maxPay:
        await ctx.respond(f"Trying to pay more than your total: {maxPay}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    await remCoins(ctx.guild_id, ctx.user.id, amount)
    await addCoins(ctx.guild_id, user.id, amount)
    await ctx.respond(f'{amount} coins paid to {user.mention}\nFrom: {ctx.user.mention}')


def load(bot: lightbulb.BotApp):
    bot.add_plugin(payPlugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(payPlugin)
