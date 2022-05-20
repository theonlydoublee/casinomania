import hikari, lightbulb
from casinomania.functions.readWrite import readGuildFile, writeGuildFile

gamePL = lightbulb.Plugin('gamePL')

SlashCommand = lightbulb.SlashCommand


@gamePL.command()
@lightbulb.command('cw', 'Create message with btn to start Casino War')
@lightbulb.implements(SlashCommand)
async def cmd_IniGame(ctx: lightbulb.Context):
    # await ctx.bot.rest.create_interaction_response(ctx.interaction, token=ctx.interaction.token, response_type=5)
    data = readGuildFile(ctx.guild_id)

    channel = await ctx.bot.rest.fetch_channel(ctx.channel_id)
    chName = channel.name

    if chName != 'casino-war':
        await ctx.respond('Not in Casino War channel', flags=hikari.MessageFlag.EPHEMERAL)
        return

    try:
        await ctx.bot.rest.fetch_message(data['cwMsg']['channel'], data['cwMsg']['id'])

        await ctx.respond(f"Button already exists in <#{data['cwMsg']['channel']}>", flags=hikari.MessageFlag.EPHEMERAL)
    except:
        btnBJ = ctx.bot.rest.build_action_row()
        (
            btnBJ.add_button(
                # Gray button style, see also PRIMARY, and DANGER.
                hikari.ButtonStyle.SECONDARY,
                # Set the buttons custom ID to the label.
                'startCW',
            )
            # Set the actual label.
            .set_label('Create Casino War Game')
            # Finally add the button to the container.
            .add_to_container()
        )
        msg = await ctx.bot.rest.create_message(ctx.channel_id, component=btnBJ)
        chID = ctx.channel_id
        data['cwMsg'] = {'id': str(msg.id), 'channel': str(chID)}

        # data['gameMsg']['id'] = str(msg.id)
        # data['gameMsg']['channel'] = str(chID)
        writeGuildFile(data, ctx.guild_id)

        await ctx.respond(content='Created Message', flags=hikari.MessageFlag.EPHEMERAL)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(gamePL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(gamePL)
