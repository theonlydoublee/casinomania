"""
grab player name and wallet
display as highest to lowest > Player Name: Wallet
continuously check the wallet of each player saved within the .json files every 2 minutes
"""
import lightbulb, hikari
from lightbulb.ext import tasks
import lightbulb, hikari
from casinomania.functions.readWrite import readGuildFile, writeGuildFile
import os

from casinomania.functions.readWrite import setBet, getBet, getCCTotal,readGuildFile


lbuplugin = lightbulb.Plugin("leaderboardupdater")

#full_file_paths = get_filepaths("/casinomania/Data")

@tasks.task(m=2, auto_start=True)
async def leaderboardUpdater():
    guildIDs = os.listdir('casinomania/Data/')

    lbEmbed = hikari.Embed(title='Casino Leaderboard',
                           description='The bigger the wallet, the Higher the rank!',
                           ).set_thumbnail('casinomania/images/BlackjackThumbnail.png')
    # print(guildIDs)
    for guildID in guildIDs:
        currentGuildData = readGuildFile(guildID=guildID)
        print(currentGuildData)
        users = []
        for item in currentGuildData:
            if len(item) == 18:
                # logic here
                userID = item
                userCoins = currentGuildData[str(userID)]['coins']
                users.append({'userID': userID, 'userCoins': userCoins})
        # users.sort(key=['userCoins'])
        users = sorted(users, key=lambda k: k['userCoins'], reverse=True)
        i = 0
        for user in users:

            lbEmbed.add_field(name=user['userID'], value=user['userCoins'])
        msg = await lbuplugin.bot.rest.fetch_message(channel=currentGuildData['lbMsg']['channel'], message=currentGuildData['lbMsg']['id'])
        await msg.edit(embed=lbEmbed)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(lbuplugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(lbuplugin)