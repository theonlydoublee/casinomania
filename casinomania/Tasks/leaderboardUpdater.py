from lightbulb.ext import tasks
import lightbulb, hikari

from casinomania.leaderboard.updateBoard import leaderboardUpdater

plugin = lightbulb.Plugin("statusUpdater")


@tasks.task(m=1.5, auto_start=True)
async def statusUpdater():
    await leaderboardUpdater()


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
