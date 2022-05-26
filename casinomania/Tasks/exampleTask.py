from lightbulb.ext import tasks
import lightbulb, hikari

from casinomania.leaderboard.updateBoard import leaderboardUpdater

plugin = lightbulb.Plugin("statusUpdater")


# @plugin.command
@tasks.task(s=30, auto_start=True)
async def statusUpdater():
    print('Task Ran')
    await leaderboardUpdater()
    print('task done')


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
