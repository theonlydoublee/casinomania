import hikari, lightbulb
from casinomania.functions.readWrite import readGuildFile, writeGuildFile

blackjackPL = lightbulb.Plugin('blackjackPL')

SlashCommand = lightbulb.SlashCommand


@blackjackPL.command()
@lightbulb.command('bj', 'Create message with btn to start Blackjack')
@lightbulb.implements(SlashCommand)
async def cmd_IniBJ(ctx: lightbulb.Context):
    # await ctx.bot.rest.create_interaction_response(ctx.interaction, token=ctx.interaction.token, response_type=5)
    data = readGuildFile(ctx.guild_id)

    channel = await ctx.bot.rest.fetch_channel(ctx.channel_id)
    chName = channel.name

    if chName != 'blackjack':
        await ctx.respond('Not in Blackjack channel', flags=hikari.MessageFlag.EPHEMERAL)
        return

    try:
        await ctx.bot.rest.fetch_message(data['bjMsg']['channel'], data['bjMsg']['id'])

        await ctx.respond(f"Button already exists in <#{data['bjMsg']['channel']}>", flags=hikari.MessageFlag.EPHEMERAL)
    except:
        btnBJ = ctx.bot.rest.build_action_row()
        (
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
        )
        msg = await ctx.bot.rest.create_message(ctx.channel_id, component=btnBJ)
        chID = ctx.channel_id

        data['bjMsg'] = {'id': str(msg.id), 'channel': str(chID)}

        # data['bjMsg']['id'] = str(msg.id)
        # data['bjMsg']['channel'] = str(chID)
        writeGuildFile(data, ctx.guild_id)

        await ctx.respond(content='Created Message', flags=hikari.MessageFlag.EPHEMERAL)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(blackjackPL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(blackjackPL)
