import hikari, lightbulb
from casinomania.functions.readWrite import readGuildFile, writeGuildFile


SlashCommand = lightbulb.SlashCommand

# change these
gameShort = 'game'
gameFull = 'Game Title'
# rename this match
# gamePL should be what gameShort equals ending in PL
gamePL = lightbulb.Plugin(f'{gameShort}PL')


@gamePL.command()
@lightbulb.command(f'{gameShort}', f'Create message with btn to start {gameFull}')
@lightbulb.implements(SlashCommand)
async def cmd_IniGame(ctx: lightbulb.Context):
    # await ctx.bot.rest.create_interaction_response(ctx.interaction, token=ctx.interaction.token, response_type=5)
    data = readGuildFile(ctx.guild_id)

    try:
        await ctx.bot.rest.fetch_message(data[f'{gameShort}Msg']['channel'], data[f'{gameShort}Msg']['id'])

        await ctx.respond(f"Button already exists in <#{data[f'{gameShort}Msg']['channel']}>", flags=hikari.MessageFlag.EPHEMERAL)
    except:
        # rename this
        btnGame = ctx.bot.rest.build_action_row()
        (
            btnGame.add_button(
                # Gray button style, see also PRIMARY, and DANGER.
                hikari.ButtonStyle.SECONDARY,
                # Set the buttons custom ID to the label.
                f'start{gameShort}',
            )
            # Set the actual label.
            .set_label(f'Create {gameFull} Game')
            # Finally add the button to the container.
            .add_to_container()
        )
        msg = await ctx.bot.rest.create_message(ctx.channel_id, component=btnGame)
        chID = ctx.channel_id
        data[f'{gameShort}Msg'] = {'id': str(msg.id), 'channel': str(chID)}

        # data['gameMsg']['id'] = str(msg.id)
        # data['gameMsg']['channel'] = str(chID)
        writeGuildFile(data, ctx.guild_id)

        await ctx.respond(content='Created Message', flags=hikari.MessageFlag.EPHEMERAL)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(gamePL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(gamePL)
