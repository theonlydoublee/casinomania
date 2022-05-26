"""
Create embedded message post for testing //
Adjust so that the text appears as a tiered list: Highest total is largest text, next two places medium, and the rest are small
Have embedded message be updated by updateBoard.py
"""
import hikari, lightbulb
from casinomania.functions.readWrite import readGuildFile, writeGuildFile

leaderboardPL = lightbulb.Plugin('leaderboardPL')

SlashCommand = lightbulb.SlashCommand


from casinomania.leaderboard.updateBoard import leaderboardUpdater

@leaderboardPL.command()
@lightbulb.command('lb', 'Here is the Leaderboard!')
@lightbulb.implements(SlashCommand)
async def cmd_IniBJ(ctx: lightbulb.Context):
    # await ctx.bot.rest.create_interaction_response(ctx.interaction, token=ctx.interaction.token, response_type=5)
    data = readGuildFile(ctx.guild_id)
    print(ctx.guild_id)
    # print(data['lbMsg'])
    channel = await ctx.bot.rest.fetch_channel(ctx.channel_id)
    chName = channel.name

    if chName != 'leaderboard':
        await ctx.respond('Not in Leaderboard channel', flags=hikari.MessageFlag.EPHEMERAL)
        return

    try:
        await ctx.bot.rest.fetch_message(data['lbMsg']['channel'], data['lbMsg']['id'])

        await ctx.respond(f"Leaderboard already exists in <#{data['lbMsg']['channel']}>", flags=hikari.MessageFlag.EPHEMERAL)
    except:
        placeholder = hikari.Embed(title='Wait for bot to update', description='...')
        msg = await leaderboardPL.app.rest.create_message(channel=ctx.channel_id, embed=placeholder)

        data['lbMsg'] = {'channel': ctx.channel_id, 'id': msg.id}

        # data['lbMsg']['channel'] = ctx.channel_id
        # data['lbMsg']['id'] = msg.id
        writeGuildFile(data, ctx.guild_id)
        # await leaderboardUpdater()

        # btnBJ = ctx.bot.rest.build_action_row()
        """(
            btnBJ.add_button(
                # Gray button style, see also PRIMARY, and DANGER.
                hikari.ButtonStyle.SECONDARY,
                # Set the buttons custom ID to the label.
                'startBJ',
            )
            # Set the actual label.
            .set_label('Create BJ Game')
            # Finally add the button to the container.
            .add_to_container()
        )"""

        await ctx.respond(content='Created Message', flags=hikari.MessageFlag.EPHEMERAL)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(leaderboardPL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(leaderboardPL)
