import hikari, lightbulb, miru
import random
from asyncio import sleep
from casinomania.functions import createImages
from casinomania.functions.simpleFunctions import getCardName, getTotValue, addCoins, remCoins, create_Decks, make_hand
from casinomania.functions.readWrite import getBet, setBet, setCCTotal, getCCTotal
from casinomania.functions.readWrite import readGuildFile, writeGuildFile

casinoWarPL = lightbulb.Plugin('casinoWarPL', include_datastore=True)

SlashCommand = lightbulb.SlashCommand


class MyModal(miru.Modal):
    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        # ModalContext.values is a mapping of {TextInput: value}
        values = [value for value in ctx.values.values()]
        # await ctx.respond(f"Received the following input: ```{' | '.join(values)}```")
        print()
        try:
            channel = ctx.channel_id
            chName = (await ctx.bot.rest.fetch_channel(ctx.channel_id)).name
            # print(f'Change bet in {chName} - {ctx.user.username}')
            amount = int(values[0])
            guildID = ctx.guild_id
            userID = ctx.user.id
            maxBet = int(getCCTotal(guildID, userID))

            # print(amount)
            # int(amount)
            if amount < 1:
                await ctx.respond(f'Only positive ints allowed', flags=hikari.MessageFlag.EPHEMERAL)
            elif amount > maxBet:
                setBet(guildID, userID, maxBet, chName)
                await ctx.respond(f'Amount too high\nGoing all in at: {maxBet}', flags=hikari.MessageFlag.EPHEMERAL)
            else:
                setBet(guildID, userID, amount, chName)
                # await ctx.respond(f'Now betting: {getBet(guildID, userID)}')
                await ctx.respond(content=f'Now betting {values[0]}', flags=hikari.MessageFlag.EPHEMERAL)
        except:
            await ctx.respond(content=f'Enter a valid bet, int only', flags=hikari.MessageFlag.EPHEMERAL)


class CasinoWar(miru.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)  # Setting timeout to None

    @miru.button(label="Create Casino War Game", custom_id="startCW")
    async def btn_CW(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        intGuildID = ctx.guild_id


        try:
            casinoWarPL.d.CWplaying[str(intGuildID)]
        except:
            casinoWarPL.d.CWplaying[str(intGuildID)] = False

        if casinoWarPL.d.CWplaying[str(intGuildID)]:
            return

        msgd = await ctx.respond('starting game')
        casinoWarPL.d.CWplaying[str(intGuildID)] = True

        data = readGuildFile(intGuildID)
        startMsgID = data['cwMsg']['id']
        startChnID = data['cwMsg']['channel']

        cwButtons = [
            {'label': 'Create Casino War Game', 'value': 'startCW'},
            {'label': 'Bet', 'value': 'cwBet'},
        ]
        # Disable the btn to start game
        btnCW = ctx.interaction.app.rest.build_action_row()
        for btn in cwButtons:
            (
                # Adding the buttons into the action row.
                btnCW.add_button(
                    # Gray button style, see also PRIMARY, and DANGER.
                    hikari.ButtonStyle.SECONDARY,
                    # Set the buttons custom ID to the label.
                    btn['value'],
                )
                    # Set the actual label.
                    .set_label(btn['label']).set_is_disabled(True)
                    # Finally add the button to the container.
                    .add_to_container()
            )

        msgID = await casinoWarPL.app.rest.fetch_message(message=startMsgID, channel=startChnID)
        await msgID.edit(component=btnCW)

        cwEmbed = hikari.Embed(title='Casino War',
                               description='Click Join to join the game\nAnd again to leave\n\nWhen ready to start\nCommand initiator click start',
                               ).set_thumbnail('casinomania/images/CasinoWarThumbnail.png')

        buttons = [
            {'label': 'Start', 'value': 'cwStart'},
            {'label': 'Join', 'value': 'cwJoin'},
        ]
        cwBtns = ctx.interaction.app.rest.build_action_row()

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

        msg = await casinoWarPL.app.rest.create_message(channel=startChnID, embed=cwEmbed, component=cwBtns)
        await msgd.delete()
        starting = True
        players = []
        event = None
        while starting:
            token = None
            interaction = None
            try:
                event = await casinoWarPL.bot.wait_for(
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
                # print('start Casino War')
                starting = False
            else:
                member = event.interaction.member

                memberID = member.id
                if memberID in players:
                    players.remove(memberID)
                    await event.app.rest.create_interaction_response(interaction.id, content='Left', token=token,
                                                                     response_type=4,
                                                                     flags=hikari.MessageFlag.EPHEMERAL)
                    # print(f'{member.user} left')

                else:
                    players.append(memberID)
                    await event.app.rest.create_interaction_response(event.interaction.id, content='Joined',
                                                                     token=token,
                                                                     response_type=4,
                                                                     flags=hikari.MessageFlag.EPHEMERAL)
                    # print(f'{member.user} joined')

        totPlayers = len(players)

        # Create deck for game
        offset = 0
        while totPlayers > 2:  # only increase offset if more than 2 players
            offset += 1
            totPlayers -= 2  # Number of players for one deck

        playerValues = []
        handMsg = None

        deck = create_Decks(2 + offset, casinoWarPL.bot)
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

            # print('this is game logic running')

            player = await event.interaction.app.rest.fetch_member(intGuildID, player)

            img = await createImages.cards_image(playerCardNames, player.user.id, intGuildID)

            handEmbed = hikari.Embed(title=player.user.username).set_image(img)  # .set_thumbnail(DealerImg)

            handMsg = await event.interaction.app.rest.create_message(channel=startChnID, content='', embed=handEmbed)
            cardTotal = await getTotValue(hand)

            playerValues.append({"player": player, "cardTotal": cardTotal})
            await sleep(2)  # wait 0.3 seconds
            await handMsg.delete()

        msgID = await casinoWarPL.app.rest.fetch_message(message=startMsgID, channel=startChnID)
        await msgID.edit(component=btnCW)
        casinoWarPL.d.CWplaying[str(intGuildID)] = False

        winningsEmbed = hikari.Embed(title='Winnings')
        # add player and outcome to embed
        for player in playerValues:
            game = 'casino-war'
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
                await addCoins(intGuildID, playerID, getBet(intGuildID, playerID, game))
                ccTotal = getCCTotal(intGuildID, playerID)
            elif handTotal < dealerTotal:  # player < dealer, lose bet
                outcome = 'Lost'
                await remCoins(intGuildID, playerID, getBet(intGuildID, playerID, game))
                ccTotal = getCCTotal(intGuildID, playerID)
            # set new account total for user
            setCCTotal(intGuildID, playerID, ccTotal)
            # add field to embed with player info and new account total
            winningsEmbed.add_field(name=f"{player['player'].user.username} - {outcome}",
                                    value=f'Now has {ccTotal} CasinoCoins')

        # create msg with winnings embed
        winningsMsg = await event.interaction.app.rest.create_message(startChnID, content='', embed=winningsEmbed)

        await dealerMsg.delete()
        await sleep(5)
        await winningsMsg.delete()

        msgID = await casinoWarPL.app.rest.fetch_message(message=startMsgID, channel=startChnID)
        await msgID.edit(components=CasinoWar().build())  # edit msg to update
        casinoWarPL.d.CWplaying[str(intGuildID)] = False  # set to false since game over
        return
        
    @miru.button(label="Bet", custom_id="btnCWBet")
    async def btn_BetCW(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        guildID = ctx.guild_id
        userID = ctx.user.id
        maxBet = int(getCCTotal(guildID, userID))

        modal = MyModal(f"Set Your Bet You have {maxBet} coins", timeout=30)
        modal.add_item(miru.TextInput(label="Bet", placeholder="Ex: 10", required=True, ))
        # await ctx.respond_with_modal(modal)
        await modal.send(ctx.interaction)


@casinoWarPL.command()
@lightbulb.command('cw', 'Create message with btn to start Casino War')
@lightbulb.implements(SlashCommand)
async def cmd_IniCW(ctx: lightbulb.Context):
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
        view = CasinoWar()
        msg = await ctx.bot.rest.create_message(ctx.channel_id, components=view.build())
        view.start_listener()

        chID = ctx.channel_id
        data['cwMsg'] = {'id': str(msg.id), 'channel': str(chID)}

        writeGuildFile(data, ctx.guild_id)

        await ctx.respond(content='Created Message', flags=hikari.MessageFlag.EPHEMERAL)


@casinoWarPL.listener(event=lightbulb.events.LightbulbStartedEvent)
async def startup_views(event: lightbulb.events.LightbulbStartedEvent) -> None:
    view = CasinoWar()
    view.start_listener()


def load(bot: lightbulb.BotApp):
    bot.add_plugin(casinoWarPL)
    casinoWarPL.d.CWplaying = {}


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(casinoWarPL)
