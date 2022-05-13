from asyncio import sleep

import hikari, lightbulb
import random

from casinomania.functions import createImages
from casinomania.functions.simpleFunctions import getCardName, getTotValue, addCoins, remCoins
from casinomania.functions.readWrite import getBet,setBet,setCCTotal,getCCTotal

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

    starting = True
    blackjackPL.bot.d.bjPLayers = []
    # ctx.bot.d.bjPLayers.append('test')
    # print(blackjackPL.bot.d.bjPLayers)
    players = []
    event = None
    # print(type(ctx.bot.d.bjPLayers))
    while starting:
        token = None
        interaction = None
        try:
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
            token = event.interaction.token
            interaction = event.interaction
            custID = event.interaction.custom_id
        except:
            custID = 'bjStart'

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
                blackjackPL.bot.d.bjPLayers.pop(blackjackPL.bot.d.bjPLayers.index(memberID))
                await ctx.app.rest.create_interaction_response(interaction.id, content='Left', token=token, response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                print(f'{member.user} left')

            else:
                blackjackPL.bot.d.bjPLayers.append(memberID)
                await ctx.app.rest.create_interaction_response(event.interaction.id, content='Joined', token=token, response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                print(f'{member.user} joined')

            # print(blackjackPL.bot.d.bjPLayers)
            players = blackjackPL.bot.d.bjPLayers

    # print('gjfdshgkjsliud')
    # print(players)

    deck = []
    for i in range(2):
        for card in ctx.bot.d.cardValues:
            for suit in ctx.bot.d.suits:
                deck.append({'value': card, 'suit': f'{suit}'})

    random.shuffle(deck)
    # for i in range(10):
    #     print(random.choice(deck))
    dealerHand = []

    for i in range(2):
        card = random.choice(deck)
        dealerHand.append(card)
        deck.remove(card)

    # print(len(deck))
    # print(dealerHand)

    dealerCardNames = []
    for card in dealerHand:
        dealerCardNames.append(await getCardName(card['value'], card['suit']))
    img = await createImages.cards_image(dealerCardNames, ctx.bot.get_me().id, True)

    startEmbed = hikari.Embed(title='Dealer Hand').set_thumbnail().set_image(img)

    dealerMsg = await msg.edit(content='', embed=startEmbed, replace_attachments=True, components=[])

    # await event.app.rest.create_message(ctx.channel_id, content='Start game logic')

    plrButtons = [
        {'label': 'Hit', 'value': 'bjHit'},
        {'label': 'Stand', 'value': 'bjStand'},
    ]
    plrBtns = ctx.bot.rest.build_action_row()

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

        player = await ctx.bot.rest.fetch_member(ctx.guild_id, player)
        img = await createImages.cards_image(playerCardNames, player.user.id)
        handEmbed = hikari.Embed(title=player.user.username).set_image(img)
        handMsg = await ctx.bot.rest.create_message(channel=ctx.channel_id, content='', embed=handEmbed, component=plrBtns)
        cardTotal = 0
        interaction = None
        token = None
        while playing:
            custID = 'bjStand'

            if cardTotal < 21:
                try:
                    event2 = await ctx.bot.wait_for(
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
                    await ctx.app.rest.create_interaction_response(interaction, token, response_type=4, content='Standing', flags=hikari.MessageFlag.EPHEMERAL)
                except:
                    pass
                print(player.user.username + " Stood")
                playing = False
                # break
            elif custID == 'bjHit':
                await ctx.app.rest.create_interaction_response(interaction, token, response_type=4, content='Hitting', flags=hikari.MessageFlag.EPHEMERAL)

                print(player.user.username + " is Hitting")
                card = random.choice(deck)
                hand.append(card)
                deck.remove(card)
                # print(hand)
                playerCardNames.append(await getCardName(card['value'], card['suit']))
                # print(playerCardNames)
                img2 = await createImages.cards_image(playerCardNames, player.user.id)
                handEmbed2 = hikari.Embed(title=player.user.username).set_image(img2)
                await handMsg.edit(content='', embed=handEmbed2, component=plrBtns, replace_attachments=True)

            cardTotal = await getTotValue(hand)

        playerValues.append({"player": player, "cardTotal": cardTotal})
        await sleep(1)
        await handMsg.delete()

    for ply in playerValues:
        print(ply["player"].user.username + " " + str(ply['cardTotal']))
    # print(playerValues)

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

        # for card in dealerHand:
        #     dealerCardNames.append(await getCardName(card['value'], card['suit']))

    print(f'Dealer {dealerTotal}')

    img3 = await createImages.cards_image(dealerCardNames, ctx.bot.get_me().id)

    dealerEmbed = hikari.Embed(title='Dealer Hand').set_thumbnail().set_image(img3)

    await dealerMsg.edit(content='', embed=dealerEmbed, replace_attachments=True, components=[])

    winningsEmbed = hikari.Embed(title='Winnings')
    for player in playerValues:
        guildID = ctx.guild_id
        playerID = player['player'].user.id
        outcome = ''
        ccTotal = 0
        handTotal = player['cardTotal']
        if handTotal > 21:
            outcome = 'Busted'
            await remCoins(guildID, playerID, getBet(guildID, playerID))
            ccTotal = getCCTotal(guildID, playerID)
        elif handTotal == dealerTotal:
            outcome = 'Tied'
            ccTotal = getCCTotal(guildID, playerID)
        elif (handTotal > dealerTotal) or dealerTotal == 100:
            outcome = 'Won'
            await addCoins(guildID, playerID, getBet(guildID, playerID))
            ccTotal = getCCTotal(guildID, playerID)
        elif handTotal < dealerTotal:
            outcome = 'Lost'
            await remCoins(guildID, playerID, getBet(guildID, playerID))
            ccTotal = getCCTotal(guildID, playerID)
        setCCTotal(guildID, playerID, ccTotal)
        winningsEmbed.add_field(name=f"{player['player'].user.username} - {outcome}", value=f'Now has {ccTotal} CasinoCoins')

    winningsMsg = await ctx.bot.rest.create_message(ctx.channel_id, content='', embed=winningsEmbed)

    await sleep(10)
    await dealerMsg.delete()
    await sleep(1)
    await winningsMsg.delete()


def load(bot: lightbulb.BotApp):
    bot.add_plugin(blackjackPL)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(blackjackPL)
