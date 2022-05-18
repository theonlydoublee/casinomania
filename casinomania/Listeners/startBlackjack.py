import lightbulb, hikari
import random
from asyncio import sleep
from casinomania.functions import createImages
from casinomania.functions.simpleFunctions import getCardName, getTotValue, addCoins, remCoins, create_Decks, make_hand
from casinomania.functions.readWrite import getBet, setBet, setCCTotal, getCCTotal

from casinomania.functions.readWrite import readGuildFile, writeGuildFile

bjStart = lightbulb.Plugin("bjStart", include_datastore=True)


@bjStart.listener(hikari.events.InteractionCreateEvent)
async def event_bjStart(eventS: hikari.events.InteractionCreateEvent) -> None:

    intGuildID = eventS.interaction.guild_id
    if bjStart.d.playing:
        return

    if str(eventS.interaction.type) != "MESSAGE_COMPONENT":
        return

    if str(eventS.interaction.component_type) != "BUTTON":
        return
    if str(eventS.interaction.custom_id) != 'startBJ':
        return

    bjStart.d.playing = True

    data = readGuildFile(intGuildID)
    startMsgID = data['bjMsg']['id']
    startChnID = data['bjMsg']['channel']

    btnBJ = eventS.interaction.app.rest.build_action_row()
    (
        btnBJ.add_button(
            # Gray button style, see also PRIMARY, and DANGER.
            hikari.ButtonStyle.SECONDARY,
            # Set the buttons custom ID to the label.
            'startBJ',
        )
        # Set the actual label.
        .set_label('Create BJ Game').set_is_disabled(True)
        # Finally add the button to the container.
        .add_to_container()
    )
    msgID = await bjStart.app.rest.fetch_message(message=startMsgID, channel=startChnID)
    await msgID.edit(component=btnBJ)
    await bjStart.bot.rest.create_interaction_response(eventS.interaction, eventS.interaction.token, response_type=6)

    bjEmbed = hikari.Embed(title='Blackjack',
                           description='Click Join to join the game\nAnd again to leave\n\nWhen ready to start\nCommand initiator click start',
                           ).set_thumbnail('casinomania/images/BlackjackThumbnail.png')

    buttons = [
        {'label': 'Start', 'value': 'bjStart'},
        {'label': 'Join', 'value': 'bjJoin'},
    ]
    bjBtns = eventS.interaction.app.rest.build_action_row()

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

    msg = await bjStart.app.rest.create_message(channel=startChnID, embed=bjEmbed, component=bjBtns)
    # msg = await resp.message()

    starting = True
    # blackjackPL.bot.d.bjPLayers = []
    # ctx.bot.d.bjPLayers.append('test')
    # print(blackjackPL.bot.d.bjPLayers)
    players = []
    event = None
    # print(type(ctx.bot.d.bjPLayers))
    while starting:
        token = None
        interaction = None
        # try:
        event = await bjStart.bot.wait_for(
            hikari.InteractionCreateEvent,
            timeout=30,
            predicate=lambda e:
            isinstance(e.interaction, hikari.ComponentInteraction)
            # and e.interaction.user.id == ctx.author.id
            and e.interaction.message.id == msg.id
            and e.interaction.component_type == hikari.ComponentType.BUTTON
            # and e.interaction.custom_id == 'bjStart'
        )
        token = event.interaction.token
        interaction = event.interaction
        custID = event.interaction.custom_id
        # except:
        #     custID = 'bjStart'

        if custID == 'bjStart':
            print('start BJ')
            starting = False
            # await event.app.rest.create_interaction_response(event.interaction.id, content='Started', token=event.interaction.token, response_type=4)
            # break
        else:
            member = event.interaction.member

            # print(member.id)
            # list = ctx.bot.d.bjPLayers
            # list.append(member.id)
            # ctx.bot.d.bjPLayers = list
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
    offset = 0
    while totPlayers > 2:
        offset += 1
        totPlayers -= 2

    deck = create_Decks(2+offset, bjStart.bot)
    random.shuffle(deck)
    dealerHand = []

    for i in range(2):
        card = random.choice(deck)
        dealerHand.append(card)
        deck.remove(card)

    dealerCardNames = await make_hand(dealerHand)
    # for card in dealerHand:
    #     dealerCardNames.append(await getCardName(card['value'], card['suit']))
    img = await createImages.cards_image(dealerCardNames, event.interaction.app.get_me().id, intGuildID, True)

    startEmbed = hikari.Embed(title='Dealer Hand').set_thumbnail().set_image(img)

    dealerMsg = await msg.edit(content='', embed=startEmbed, replace_attachments=True, components=[])

    # await event.app.rest.create_message(ctx.channel_id, content='Start game logic')

    plrButtons = [
        {'label': 'Hit', 'value': 'bjHit'},
        {'label': 'Stand', 'value': 'bjStand'},
    ]
    plrBtns = event.interaction.app.rest.build_action_row()

    for btn in plrButtons:
        (
            # Adding the buttons into the action row.
            plrBtns.add_button(
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

    playerValues = []
    handMsg = None
    for player in players:
        playing = True
        hand = []
        for i in range(2):
            card = random.choice(deck)
            hand.append(card)
            deck.remove(card)
        playerCardNames = []
        for card in hand:
            playerCardNames.append(await getCardName(card['value'], card['suit']))

        player = await event.interaction.app.rest.fetch_member(intGuildID, player)
        # player = await event.interaction.app.rest.fetch_member(event.guild_id, player)
        img = await createImages.cards_image(playerCardNames, player.user.id, intGuildID)
        handEmbed = hikari.Embed(title=player.user.username).set_image(img)
        handMsg = await event.interaction.app.rest.create_message(channel=startChnID, content='', embed=handEmbed,
                                                                  component=plrBtns)
        # handMsg = await event.interaction.app.rest.create_message(channel=event.channel_id, content='', embed=handEmbed,
        #                                                           component=plrBtns)
        cardTotal = 0
        interaction = None
        token = None
        cardTotal = await getTotValue(hand)

        while playing:
            custID = 'bjStand'
            print(cardTotal)
            if cardTotal < 21:
                try:
                    event2 = await event.interaction.app.wait_for(
                        hikari.InteractionCreateEvent,
                        timeout=30,
                        predicate=lambda e:
                        isinstance(e.interaction, hikari.ComponentInteraction)
                        and e.interaction.user.id == player.id
                        and e.interaction.message.id == handMsg.id
                        and e.interaction.component_type == hikari.ComponentType.BUTTON
                        # and e.interaction.custom_id == 'bjStart'
                    )
                    interaction = event2.interaction
                    token = event2.interaction.token
                    custID = event2.interaction.custom_id
                except:
                    custID = 'bjStand'
                    pass

            else:
                custID = 'bjStand'

            if custID == 'bjStand':
                try:
                    await event.app.rest.create_interaction_response(interaction, token, response_type=6,
                                                                     content='Standing',
                                                                     flags=hikari.MessageFlag.EPHEMERAL)
                except:
                    pass
                print(player.user.username + " Stood")
                playing = False
                # break
            elif custID == 'bjHit':
                await event.app.rest.create_interaction_response(interaction, token, response_type=6, content='Hitting',
                                                                 flags=hikari.MessageFlag.EPHEMERAL)

                print(player.user.username + " is Hitting")
                card = random.choice(deck)
                hand.append(card)
                deck.remove(card)
                # print(hand)
                playerCardNames.append(await getCardName(card['value'], card['suit']))
                # print(playerCardNames)
                img2 = await createImages.cards_image(playerCardNames, player.user.id, intGuildID)
                handEmbed2 = hikari.Embed(title=player.user.username).set_image(img2)
                await handMsg.edit(content='', embed=handEmbed2, component=plrBtns, replace_attachments=True)

            cardTotal = await getTotValue(hand)

        playerValues.append({"player": player, "cardTotal": cardTotal})
        await sleep(1)
        await handMsg.delete()

    dealerPlay = True
    dealerTotal = 0
    while dealerPlay:

        dealerTotal = await getTotValue(dealerHand)

        if dealerTotal < 17:
            card = random.choice(deck)
            dealerHand.append(card)
            deck.remove(card)
            dealerCardNames.append(await getCardName(card['value'], card['suit']))
        else:
            dealerPlay = False

    for ply in playerValues:
        print(ply["player"].user.username + " " + str(ply['cardTotal']))
    print(f'Dealer {dealerTotal}')

    img3 = await createImages.cards_image(dealerCardNames, event.interaction.app.get_me().id, intGuildID)

    dealerEmbed = hikari.Embed(title='Dealer Hand').set_thumbnail().set_image(img3)

    await dealerMsg.edit(content='', embed=dealerEmbed, replace_attachments=True, components=[])

    winningsEmbed = hikari.Embed(title='Winnings')
    for player in playerValues:
        # intGuildID = intGuildID
        playerID = player['player'].user.id
        outcome = ''
        ccTotal = 0
        handTotal = player['cardTotal']
        if handTotal > 21:
            outcome = 'Busted'
            await remCoins(intGuildID, playerID, getBet(intGuildID, playerID))
            ccTotal = getCCTotal(intGuildID, playerID)
        elif handTotal == dealerTotal:
            outcome = 'Tied'
            ccTotal = getCCTotal(intGuildID, playerID)
        elif (handTotal > dealerTotal) or dealerTotal == 100:
            outcome = 'Won'
            await addCoins(intGuildID, playerID, getBet(intGuildID, playerID))
            ccTotal = getCCTotal(intGuildID, playerID)
        elif handTotal < dealerTotal:
            outcome = 'Lost'
            await remCoins(intGuildID, playerID, getBet(intGuildID, playerID))
            ccTotal = getCCTotal(intGuildID, playerID)
        setCCTotal(intGuildID, playerID, ccTotal)
        winningsEmbed.add_field(name=f"{player['player'].user.username} - {outcome}",
                                value=f'Now has {ccTotal} CasinoCoins')

    winningsMsg = await event.interaction.app.rest.create_message(startChnID, content='', embed=winningsEmbed)

    await sleep(10)
    await dealerMsg.delete()
    await sleep(1)
    await winningsMsg.delete()

    btnBJ = event.interaction.app.rest.build_action_row()
    (
        btnBJ.add_button(
            # Gray button style, see also PRIMARY, and DANGER.
            hikari.ButtonStyle.SECONDARY,
            # Set the buttons custom ID to the label.
            'startBJ',
        )
            # Set the actual label.
            .set_label('Create BJ Game').set_is_disabled(False)
            # Finally add the button to the container.
            .add_to_container()
    )
    msgID = await bjStart.app.rest.fetch_message(message=startMsgID, channel=startChnID)
    await msgID.edit(component=btnBJ)
    bjStart.d.playing = False


def load(bot: lightbulb.BotApp):
    bot.add_plugin(bjStart)
    bjStart.d.playing = False


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(bjStart)
