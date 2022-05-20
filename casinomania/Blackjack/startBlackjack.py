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
    intGuildID = eventS.interaction.guild_id  # get guildID

    try:
        bjStart.d.BJplaying[str(intGuildID)]  # Check if gameplaying var has guild in it
    except:
        bjStart.d.BJplaying[str(intGuildID)] = False  # if guild not in var, add and set to false

    if bjStart.d.BJplaying[str(intGuildID)]:  # if var is true, then game in progress
        return

    # check for interaction on a msg that is a button and has custom id for game being played
    if str(eventS.interaction.type) != "MESSAGE_COMPONENT":
        return

    if str(eventS.interaction.component_type) != "BUTTON":
        return

    if str(eventS.interaction.custom_id) != 'startBJ':
        return

    bjStart.d.BJplaying[str(intGuildID)] = True  # set to true so another game can't start

    # grab the msg and channel the game button is in
    data = readGuildFile(intGuildID)
    startMsgID = data['bjMsg']['id']
    startChnID = data['bjMsg']['channel']

    # Disable the btn to start game
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
    # Grabs the message and edits with new button
    msgID = await bjStart.app.rest.fetch_message(message=startMsgID, channel=startChnID)
    await msgID.edit(component=btnBJ)
    # respond to button press so interaction does not fail
    await bjStart.bot.rest.create_interaction_response(eventS.interaction, eventS.interaction.token, response_type=6)

    # create embed for joining and starting the game
    bjEmbed = hikari.Embed(title='Blackjack',
                           description='Click Join to join the game\nAnd again to leave\n\nWhen ready to start\nCommand initiator click start',
                           ).set_thumbnail('casinomania/images/BlackjackThumbnail.png')
    # List of buttons to have on msg to start game
    buttons = [
        {'label': 'Start', 'value': 'bjStart'},
        {'label': 'Join', 'value': 'bjJoin'},
    ]
    # builds the buttons to be added to msg
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

    # create the msg with start and join btns
    msg = await bjStart.app.rest.create_message(channel=startChnID, embed=bjEmbed, component=bjBtns)

    # Set var to True if starting new game
    starting = True

    # initialize vars for game
    players = []
    event = None

    # loop until start btn is pressed
    while starting:
        # initialize vars for each btn event
        token = None
        interaction = None
        # in try except to start game if btn interaction times out
        try:
            # wait for a btn on msg to be clicked
            event = await bjStart.bot.wait_for(
                hikari.InteractionCreateEvent,
                timeout=30,
                predicate=lambda e:
                isinstance(e.interaction, hikari.ComponentInteraction)
                # and e.interaction.user.id == ctx.author.id  # can be used to only allow user that created game to start
                and e.interaction.message.id == msg.id  # Only waits for interaction on created msg with embed
                and e.interaction.component_type == hikari.ComponentType.BUTTON  # only a btn interaction
                and (e.interaction.custom_id == 'bjStart' or e.interaction.custom_id == 'bjJoin')  # custom ids of btns so only waits for that game
            )
            # set vars for later use
            token = event.interaction.token
            interaction = event.interaction
            custID = event.interaction.custom_id  # grab cust id to know what was clicked
        except:
            custID = 'bjStart'  # if time out, start game

        # Check if start was clicked
        if custID == 'bjStart':
            print('start BJ')  # debug log
            starting = False  # set starting to false for game to start
        else:
            # join game logic
            # grab the user that clicked btn
            member = event.interaction.member

            # grab unique id of user
            memberID = member.id
            # logic to see if player already joined
            if memberID in players:  # if in game, remove
                players.remove(memberID)  # remove user from list
                # respond to user saying they left
                await event.app.rest.create_interaction_response(interaction.id, content='Left', token=token,
                                                                 response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                # print(f'{member.user} left')  # debug print

            else:
                players.append(memberID)  # add user to list
                # respond to user saying they joined
                await event.app.rest.create_interaction_response(event.interaction.id, content='Joined', token=token,
                                                                 response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                # print(f'{member.user} joined')  # debug print

    totPlayers = len(players)  # grab tot num players in game
    offset = 0  # iniitalize var
    ppd = 2  # how many plyers per deck
    while totPlayers > ppd:  # get offset of how many decks to add
        offset += 1  # add one more deck
        totPlayers -= ppd  # subtract ppd

    # create deck for game
    deck = create_Decks(2+offset, bjStart.bot)  # 2 is base start num of decks
    random.shuffle(deck)  # shuffle deck
    dealerHand = []  # initialize dealer hand

    # draw cards for dealer
    for i in range(2):  # 2 is number cards for starting dealer hand
        card = random.choice(deck)  # grab random card from deck
        dealerHand.append(card)  # add card to dealer hand
        deck.remove(card)  # remove card from deck

    # grab image names of cards in hand for dealer
    dealerCardNames = await make_hand(dealerHand)
    # create the image of dealers hand
    DealerImg = await createImages.cards_image(dealerCardNames, event.interaction.app.get_me().id, intGuildID, True)

    # create embed for msg to dealers hadn
    startEmbed = hikari.Embed(title='Dealer Hand').set_thumbnail().set_image(DealerImg)

    # edit msg to have dealer's hand
    dealerMsg = await msg.edit(content='', embed=startEmbed, replace_attachments=True, components=[])

    # btns on player hand to interact
    plrButtons = [
        {'label': 'Hit', 'value': 'bjHit'},
        {'label': 'Stand', 'value': 'bjStand'},
    ]
    # build buttons
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

    # initialize vars
    playerValues = []
    handMsg = None
    # go through each player for one turn at a time
    for player in players:
        # set playing to true because bj can have multiple turn for one player
        playing = True
        # initialize hand vars
        hand = []
        playerCardNames = []
        # draw 2 cards for player
        for i in range(2):
            card = random.choice(deck)
            hand.append(card)
            deck.remove(card)
        # grab card image names
        for card in hand:
            playerCardNames.append(await getCardName(card['value'], card['suit']))

        # grab the player object from guild
        player = await event.interaction.app.rest.fetch_member(intGuildID, player)
        # create image of player's hand
        img = await createImages.cards_image(playerCardNames, player.user.id, intGuildID)
        # create embed using player's hand and username
        handEmbed = hikari.Embed(title=player.user.username).set_image(img)#.set_thumbnail(DealerImg)
        # create the msg using the embed and btns
        handMsg = await event.interaction.app.rest.create_message(channel=startChnID, content='', embed=handEmbed,
                                                                  component=plrBtns)
        # initialize vars
        interaction = None
        token = None
        cardTotal = await getTotValue(hand)  # grab card total of hand in case of instant 21

        # loop while user is playing
        while playing:
            # custID = 'bjStand'  # may not need so commented out until tested
            # print(cardTotal)  # deug print

            # check if user had total under 21
            if cardTotal < 21:
                try:
                    # wait for user to click hit or stand
                    event2 = await event.interaction.app.wait_for(
                        hikari.InteractionCreateEvent,
                        timeout=30,
                        predicate=lambda e:
                        isinstance(e.interaction, hikari.ComponentInteraction)
                        and e.interaction.user.id == player.id  # only current player can interact
                        and e.interaction.message.id == handMsg.id  # listen on the player hand msg
                        and e.interaction.component_type == hikari.ComponentType.BUTTON  # btn only interaction
                        # and e.interaction.custom_id == 'bjStart'
                    )
                    # grab values from the event
                    interaction = event2.interaction
                    token = event2.interaction.token
                    custID = event2.interaction.custom_id
                except:
                    # if user does not interact, stand
                    custID = 'bjStand'
                    pass

            else:
                # stand if user has 21 or higher
                custID = 'bjStand'

            # check for which btn clicked
            if custID == 'bjStand':
                try:
                    # create a response so interaction does not fail on user's side
                    await event.app.rest.create_interaction_response(interaction, token, response_type=6,
                                                                     content='Standing',
                                                                     flags=hikari.MessageFlag.EPHEMERAL)
                except:
                    # continue if creating interaction breaks
                    pass
                # print(player.user.username + " Stood")  # debug print
                playing = False
                # break
            elif custID == 'bjHit':
                # create a response so interaction does not fail on user's side
                await event.app.rest.create_interaction_response(interaction, token, response_type=6, content='Hitting',
                                                                 flags=hikari.MessageFlag.EPHEMERAL)

                # print(player.user.username + " is Hitting")  # debug print

                # draw card for user
                card = random.choice(deck)
                hand.append(card)
                deck.remove(card)

                # add card to player's hand
                playerCardNames.append(await getCardName(card['value'], card['suit']))
                # create image of new hand
                img2 = await createImages.cards_image(playerCardNames, player.user.id, intGuildID)
                # create embed with new img
                handEmbed2 = hikari.Embed(title=player.user.username).set_image(img2)
                # edit msg wth new img
                await handMsg.edit(content='', embed=handEmbed2, component=plrBtns, replace_attachments=True)

            # grab hand total after each interaction
            cardTotal = await getTotValue(hand)

        # when player turn done, add to list for later use
        playerValues.append({"player": player, "cardTotal": cardTotal})
        await sleep(1.5)  # wait 0.3 seconds
        await handMsg.delete()  # delete player hand, done so don't get rate limited on msg editing

    # initialize vals for dealers turn
    dealerPlay = True
    dealerTotal = 0
    # play dealer
    while dealerPlay:
        # get hand total of dealer
        dealerTotal = await getTotValue(dealerHand)

        # dealer rule to hit until value is 17 or higher
        if dealerTotal < 17:
            # draw card and add to dealer's hand
            card = random.choice(deck)
            dealerHand.append(card)
            deck.remove(card)
            dealerCardNames.append(await getCardName(card['value'], card['suit']))
        else:
            # stop delear from drawing cards
            dealerPlay = False

    ## debug print for terminal
    # for ply in playerValues:
    #     print(ply["player"].user.username + " " + str(ply['cardTotal']))
    # print(f'Dealer {dealerTotal}')

    # create img of dealer hand
    img3 = await createImages.cards_image(dealerCardNames, event.interaction.app.get_me().id, intGuildID)
    # create embed for dealer's hand
    dealerEmbed = hikari.Embed(title='Dealer Hand').set_thumbnail().set_image(img3)
    # edit msg to show dealer's hand
    await dealerMsg.edit(content='', embed=dealerEmbed, replace_attachments=True, components=[])

    # create embed
    winningsEmbed = hikari.Embed(title='Winnings')
    # add player and outcome to embed
    for player in playerValues:
        # intGuildID = intGuildID
        playerID = player['player'].user.id  # grab ID of user
        # initialize vars for scope
        outcome = ''
        ccTotal = 0
        handTotal = player['cardTotal']  # grab player hand total
        if handTotal > 21:  # if more that 21, lose bet
            outcome = 'Busted'
            await remCoins(intGuildID, playerID, getBet(intGuildID, playerID))
            ccTotal = getCCTotal(intGuildID, playerID)
        elif handTotal == dealerTotal:  # tie, nothing happens
            outcome = 'Tied'
            ccTotal = getCCTotal(intGuildID, playerID)
        elif (handTotal > dealerTotal) or dealerTotal == 100:  # beat dealer or (player < 21 and dealer bust), win bet
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

    # wait before deleting msgs
    await sleep(10)
    await dealerMsg.delete()
    await sleep(1)
    await winningsMsg.delete()

    # rebuild btn to be enabled
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
    # grab msg to re-enable btn
    msgID = await bjStart.app.rest.fetch_message(message=startMsgID, channel=startChnID)
    await msgID.edit(component=btnBJ)  # edit msg to update
    bjStart.d.BJplaying[str(intGuildID)] = False  # set to false since game over


# plugin load and unload functions
def load(bot: lightbulb.BotApp):
    bot.add_plugin(bjStart)
    bjStart.d.BJplaying = {}


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(bjStart)
