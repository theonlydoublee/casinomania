import lightbulb, hikari
import random
from asyncio import sleep
from casinomania.functions import createImages
from casinomania.functions.simpleFunctions import getCardName, getTotValue, addCoins, remCoins, create_Decks, make_hand
from casinomania.functions.readWrite import getBet, setBet, setCCTotal, getCCTotal

from casinomania.functions.readWrite import readGuildFile, writeGuildFile

casinoWarStart = lightbulb.Plugin("cwStart", include_datastore=True)


@casinoWarStart.listener(hikari.events.InteractionCreateEvent)
async def event_cwStart(eventS: hikari.events.InteractionCreateEvent) -> None:
    intGuildID = eventS.interaction.guild_id
    try:
        casinoWarStart.d.Gameplaying[str(intGuildID)]
        # print(casinoWarStart.d.Gameplaying)

    except:
        casinoWarStart.d.Gameplaying[str(intGuildID)] = False
        print(casinoWarStart.d.Gameplaying)

    if casinoWarStart.d.Gameplaying[str(intGuildID)]:
        return

    if str(eventS.interaction.type) != "MESSAGE_COMPONENT":
        return

    if str(eventS.interaction.component_type) != "BUTTON":
        return
    if str(eventS.interaction.custom_id) != 'startCW':
        return

    casinoWarStart.d.Gameplaying[str(intGuildID)] = True

    data = readGuildFile(intGuildID)
    startMsgID = data['cwMsg']['id']
    startChnID = data['cwMsg']['channel']

    btnCW = eventS.interaction.app.rest.build_action_row()
    (
        btnCW.add_button(
            # Gray button style, see also PRIMARY, and DANGER.
            hikari.ButtonStyle.SECONDARY,
            # Set the buttons custom ID to the label.
            'startCW',
        )
        # Set the actual label.
        .set_label('Create Casino War Game').set_is_disabled(True)
        # Finally add the button to the container.
        .add_to_container()
    )
    msgID = await casinoWarStart.app.rest.fetch_message(message=startMsgID, channel=startChnID)
    await msgID.edit(component=btnCW)
    await casinoWarStart.bot.rest.create_interaction_response(eventS.interaction, eventS.interaction.token, response_type=6)

    cwEmbed = hikari.Embed(title='Casino War',
                           description='Click Join to join the game\nAnd again to leave\n\nWhen ready to start\nCommand initiator click start',
                           ).set_thumbnail('casinomania/images/CasinoWarThumbnail.png')

    buttons = [
        {'label': 'Start', 'value': 'cwStart'},
        {'label': 'Join', 'value': 'cwJoin'},
    ]
    cwBtns = eventS.interaction.app.rest.build_action_row()

    for btn in buttons:
        (
            # Adding the buttons into the action row.
            cwBtns.add_button(
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

    msg = await casinoWarStart.app.rest.create_message(channel=startChnID, embed=cwEmbed, component=cwBtns)

    starting = True
    players = []
    event = None
    while starting:
        token = None
        interaction = None
        try:
            event = await casinoWarStart.bot.wait_for(
                hikari.InteractionCreateEvent,
                timeout=30,
                predicate=lambda e:
                isinstance(e.interaction, hikari.ComponentInteraction)
                # and e.interaction.user.id == ctx.author.id
                and e.interaction.message.id == msg.id
                and e.interaction.component_type == hikari.ComponentType.BUTTON
                and (e.interaction.custom_id == 'cwStart' or e.interaction.custom_id == 'cwJoin')
            )
            token = event.interaction.token
            interaction = event.interaction
            custID = event.interaction.custom_id
        except:
            custID = 'cwStart'

        if custID == 'cwStart':
            print('start Casino War')
            starting = False
        else:
            member = event.interaction.member

            memberID = member.id
            if memberID in players:
                players.remove(memberID)
                await event.app.rest.create_interaction_response(interaction.id, content='Left', token=token,
                                                                 response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                print(f'{member.user} left')

            else:
                players.append(memberID)
                await event.app.rest.create_interaction_response(event.interaction.id, content='Joined', token=token,
                                                                 response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                print(f'{member.user} joined')

    totPlayers = len(players)

    # Create deck for game
    offset = 0
    while totPlayers > 2:  # only increase offset if more than 2 players
        offset += 1
        totPlayers -= 2  # Number of players for one deck

    deck = create_Decks(2 + offset, casinoWarStart.bot)
    random.shuffle(deck)

    # Game Logic
    print('this is game logic running')
    await event.interaction.message.delete()

    btnCW = event.interaction.app.rest.build_action_row()
    (
        btnCW.add_button(
            # Gray button style, see also PRIMARY, and DANGER.
            hikari.ButtonStyle.SECONDARY,
            # Set the buttons custom ID to the label.
            'startCW',
        )
        # Set the actual label.
        .set_label('Create Casino War Game').set_is_disabled(False)
        # Finally add the button to the container.
        .add_to_container()
    )
    msgID = await casinoWarStart.app.rest.fetch_message(message=startMsgID, channel=startChnID)
    await msgID.edit(component=btnCW)
    casinoWarStart.d.Gameplaying[str(intGuildID)] = False


def load(bot: lightbulb.BotApp):
    bot.add_plugin(casinoWarStart)
    casinoWarStart.d.Gameplaying = {}


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(casinoWarStart)
