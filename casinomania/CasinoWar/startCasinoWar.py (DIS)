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
        casinoWarStart.d.CWplaying[str(intGuildID)]
        # print(casinoWarStart.d.CWplaying)

    except:
        casinoWarStart.d.CWplaying[str(intGuildID)] = False
        # print(casinoWarStart.d.CWplaying)

    if casinoWarStart.d.CWplaying[str(intGuildID)]:
        return

    if str(eventS.interaction.type) != "MESSAGE_COMPONENT":
        return

    if str(eventS.interaction.component_type) != "BUTTON":
        return
    if str(eventS.interaction.custom_id) != 'startCW':
        return

    casinoWarStart.d.CWplaying[str(intGuildID)] = True

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

    playerValues = []
    handMsg = None

    deck = create_Decks(2 + offset, casinoWarStart.bot)
    random.shuffle(deck)
    dealerHand = []
    card = random.choice(deck)
    dealerHand.append(card)
    deck.remove(card)

    # Game Logic
    # compare dealer hand to players
    # Win logic, whoever has the higher hand wins
    # Adds coins to users when winning
    # Each player draws 1 card to their "deck" on game start
    # Shows player their card then moves to next player shortly after
    # Prints out the winners and amount won
    dealerCardNames = await make_hand(dealerHand)
    img = await createImages.cards_image(dealerCardNames, event.interaction.app.get_me().id, intGuildID)

    startEmbed = hikari.Embed(title='Dealer Hand').set_thumbnail().set_image(img)

    dealerMsg = await msg.edit(content='', embed=startEmbed, replace_attachments=True, components=[])

    dealerTotal = await getTotValue(dealerHand)

    playerValues = []
    handMsg = None
    for player in players:
        playing = True
        hand = []
        card = random.choice(deck)
        hand.append(card)
        deck.remove(card)
        playerCardNames = []
        for card in hand:
            playerCardNames.append(await getCardName(card['value'], card['suit']))

        print('this is game logic running')

        player = await event.interaction.app.rest.fetch_member(intGuildID, player)

        img = await createImages.cards_image(playerCardNames, player.user.id, intGuildID)

        handEmbed = hikari.Embed(title=player.user.username).set_image(img)  # .set_thumbnail(DealerImg)

        handMsg = await event.interaction.app.rest.create_message(channel=startChnID, content='', embed=handEmbed)
        cardTotal = await getTotValue(hand)

        playerValues.append({"player": player, "cardTotal": cardTotal})
        await sleep(2)  # wait 0.3 seconds
        await handMsg.delete()

    img3 = await createImages.cards_image(dealerCardNames, event.interaction.app.get_me().id, intGuildID)
    # create embed for dealer's hand
    dealerEmbed = hikari.Embed(title='Dealer Hand').set_thumbnail().set_image(img3)
    # edit msg to show dealer's hand
    await dealerMsg.edit(content='', embed=dealerEmbed, replace_attachments=True, components=[])

    msgID = await casinoWarStart.app.rest.fetch_message(message=startMsgID, channel=startChnID)
    await msgID.edit(component=btnCW)
    casinoWarStart.d.CWplaying[str(intGuildID)] = False

    winningsEmbed = hikari.Embed(title='Winnings')
    # add player and outcome to embed
    for player in playerValues:
        # intGuildID = intGuildID
        playerID = player['player'].user.id  # grab ID of user
        # initialize vars for scope
        outcome = ''
        ccTotal = 0
        handTotal = player['cardTotal']  # grab player hand total
        if handTotal == dealerTotal:  # tie, nothing happens
            outcome = 'Tied'
            ccTotal = getCCTotal(intGuildID, playerID)
        elif handTotal > dealerTotal:  # beat dealer or (player < 21 and dealer bust), win bet
            outcome = 'Won'
            await addCoins(intGuildID, playerID, getBet(intGuildID, playerID))
            ccTotal = getCCTotal(intGuildID, playerID)
        elif handTotal < dealerTotal:  # player < dealer, lose bet
            outcome = 'Lost'
            await remCoins(intGuildID, playerID, getBet(intGuildID, playerID))
            ccTotal = getCCTotal(intGuildID, playerID)
        # set new account total for user
        setCCTotal(intGuildID, playerID, ccTotal)
        # add field to emberd with player info and new account total
        winningsEmbed.add_field(name=f"{player['player'].user.username} - {outcome}",
                                value=f'Now has {ccTotal} CasinoCoins')

    # create msg with winnings embed
    winningsMsg = await event.interaction.app.rest.create_message(startChnID, content='', embed=winningsEmbed)

    await dealerMsg.delete()
    await sleep(5)
    await winningsMsg.delete()

    # await event.interaction.message.delete()
    # await dealerMsg.delete()

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
    await msgID.edit(component=btnCW)  # edit msg to update
    casinoWarStart.d.CWplaying[str(intGuildID)] = False  # set to false since game over


def load(bot: lightbulb.BotApp):
    bot.add_plugin(casinoWarStart)
    casinoWarStart.d.CWplaying = {}


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(casinoWarStart)
