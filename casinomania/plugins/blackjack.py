import hikari, lightbulb
import random

from casinomania.functions import createImages
from casinomania.functions.simpleFunctions import getCardName

blackjackPL = lightbulb.Plugin('blackjackPL')

SlashCommand = lightbulb.SlashCommand


@blackjackPL.command()
@lightbulb.command('start', 'start a game of blackjack')
@lightbulb.implements(SlashCommand)
async def cmd_Start(ctx: lightbulb.context.Context):
    bjEmbed = hikari.Embed(title='Blackjack',
                           description='Click Join to join the game\nAnd again to leave\n\nWhen ready to start\nCommand initiator click start',
                           ).set_thumbnail('casinomania/images/BlackjackThumbnail.png')

    buttons = [
        {'label': 'Start', 'value': 'bjStart'},
        {'label': 'Join', 'value': 'bjJoin'},
    ]
    bjBtns = ctx.bot.rest.build_action_row()

    for btn in buttons:
        (
            # Adding the buttons into the action row.
            bjBtns.add_button(
                # Gray button style, see also PRIMARY, and DANGER.
                hikari.ButtonStyle.SECONDARY,
                # Set the buttons custom ID to the label.
                btn['value'],
            )
                # Set the actual label.
                .set_label(btn['label'])
                # Finally add the button to the container.
                .add_to_container()
        )

    resp = await ctx.respond(bjEmbed, component=bjBtns)
    msg = await resp.message()

    test = True
    blackjackPL.bot.d.bjPLayers = []
    # ctx.bot.d.bjPLayers.append('test')
    # print(blackjackPL.bot.d.bjPLayers)
    players = []
    event = None
    # print(type(ctx.bot.d.bjPLayers))
    while test:
        event = await ctx.bot.wait_for(
            hikari.InteractionCreateEvent,
            timeout=30,
            predicate=lambda e:
            isinstance(e.interaction, hikari.ComponentInteraction)
            # and e.interaction.user.id == ctx.author.id
            and e.interaction.message.id == msg.id
            and e.interaction.component_type == hikari.ComponentType.BUTTON
            # and e.interaction.custom_id == 'bjStart'
        )
        if event.interaction.custom_id == 'bjStart':
            print('start BJ')
            test = False
            await event.app.rest.create_interaction_response(event.interaction.id, content='Started', token=event.interaction.token, response_type=4)
            # break
        else:
            member = event.interaction.member

            # print(member.id)
            # list = ctx.bot.d.bjPLayers
            # list.append(member.id)
            # ctx.bot.d.bjPLayers = list
            memberID = member.id
            if memberID in players:
                blackjackPL.bot.d.bjPLayers.pop(blackjackPL.bot.d.bjPLayers.index(memberID))
                await event.app.rest.create_interaction_response(event.interaction.id, content='Left', token=event.interaction.token, response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                print(f'{member.user} left')

            else:
                blackjackPL.bot.d.bjPLayers.append(memberID)
                await event.app.rest.create_interaction_response(event.interaction.id, content='Joined', token=event.interaction.token, response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                print(f'{member.user} joined')

            # print(blackjackPL.bot.d.bjPLayers)
            players = blackjackPL.bot.d.bjPLayers

    # print('gjfdshgkjsliud')
    print(players)

    img = await createImages.cards_image(
        [await getCardName(random.choice(ctx.bot.d.cardValues), random.choice(ctx.bot.d.suits)) for i in range(2)],
        ctx.user.id, True)

    startEmbed = hikari.Embed(title='Dealer Hand').set_thumbnail().set_image(img)

    await msg.edit(content='', embed=startEmbed, replace_attachments=True, components=[])

    # await event.app.rest.create_message(ctx.channel_id, content='Start game logic')

    # do a for loop for players list for playing one at a time and only allow that user to interact


def load(bot: lightbulb.BotApp):
    bot.add_plugin(blackjackPL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(blackjackPL)
