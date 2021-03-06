import os
from asyncio import sleep

import hikari
import miru
from lightbulb.ext import tasks
from dotenv import load_dotenv
import lightbulb


from casinomania.functions.readWrite import setBet, getBet, getCCTotal,readGuildFile


# https://github.com/parafoxia/hikari-intro/blob/main/lightbulb_bot/__main__.py

# Create a new message
# await pluginName.bot.rest.create_message(ctx.channel_id, "Create New Message")


def create_bot() -> lightbulb.BotApp:
    # load TOKEN and GUILDS from .env file
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    # GUILDS = (int(os.getenv("GUILD1")),
    #           # int(os.getenv("GUILD2"))
    #           )
    intents = []
    bot = lightbulb.BotApp(
        token=TOKEN,
        intents=hikari.Intents.ALL
        # default_enabled_guilds=GUILDS,
        # help_slash_command=True,
    )

    @bot.command()
    @lightbulb.add_checks(lightbulb.owner_only)
    @lightbulb.command('reload', 'reload plugins')
    @lightbulb.implements(lightbulb.SlashCommand)
    async def cmd_reload(ctx: lightbulb.context.Context) -> None:
        plugins = []

        for e in bot.extensions:
            plugins.append(e)

        for c in plugins:
            # print(c)
            bot.reload_extensions(c)
        await ctx.respond(content='Reloaded the plugins', flags=hikari.MessageFlag.EPHEMERAL)

    # bot.load_extensions_from("./casinomania/BaseFiles")
    # bot.load_extensions_from("./casinomania/Commands")
    bot.load_extensions_from("./casinomania/Leaderboard")

    bot.load_extensions_from("./casinomania/Listeners")
    bot.load_extensions_from("./casinomania/Blackjack")
    bot.load_extensions_from("./casinomania/CasinoWar")
    bot.load_extensions_from("./casinomania/payments")
    bot.load_extensions_from("./casinomania/Tasks")

    # Loads tasks and autostart tasks will start
    tasks.load(bot)

    miru.load(bot)

    bot.d.cardValues = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'jack', 'queen', 'king', 'ace']
    # bot.d.cardValues = ['king', 'ace']
    bot.d.suits = ['clubs', 'hearts', 'spades', 'diamonds']

    return bot


if __name__ == "__main__":
    bot = create_bot()
    bot.run()
    # sleep(10)

