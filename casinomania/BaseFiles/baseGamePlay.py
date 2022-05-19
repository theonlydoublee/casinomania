import lightbulb, hikari
import random
from asyncio import sleep
from casinomania.functions import createImages
from casinomania.functions.simpleFunctions import getCardName, getTotValue, addCoins, remCoins, create_Decks, make_hand
from casinomania.functions.readWrite import getBet, setBet, setCCTotal, getCCTotal

from casinomania.functions.readWrite import readGuildFile, writeGuildFile

# change these
gameShort = 'game'
gameFull = 'Game Title'
# rename this match
# game should be what gameShort equals
gameStartPL = lightbulb.Plugin(f"{gameShort}Start", include_datastore=True)


@gameStartPL.listener(hikari.events.InteractionCreateEvent)
async def event_gameStart(eventS: hikari.events.InteractionCreateEvent) -> None:
    intGuildID = eventS.interaction.guild_id

    try:
        gameStartPL.d.Gameplaying[str(intGuildID)]
    except:
        gameStartPL.d.Gameplaying[str(intGuildID)] = False

    if gameStartPL.d.Gameplaying[str(intGuildID)]:
        return

    if str(eventS.interaction.type) != "MESSAGE_COMPONENT":
        return

    if str(eventS.interaction.component_type) != "BUTTON":
        return
    if str(eventS.interaction.custom_id) != f'start{gameShort}':
        return

    gameStartPL.d.Gameplaying[str(intGuildID)] = True

    data = readGuildFile(intGuildID)
    startMsgID = data[f'{gameShort}Msg']['id']
    startChnID = data[f'{gameShort}Msg']['channel']

    # rename this to btnGameshort
    btnGame = eventS.interaction.app.rest.build_action_row()
    (
        btnGame.add_button(
            # Gray button style, see also PRIMARY, and DANGER.
            hikari.ButtonStyle.SECONDARY,
            # Set the buttons custom ID to the label.
            f'start{gameShort}',
        )
        # Set the actual label.
        .set_label(f'Create {gameFull} Game').set_is_disabled(True)
        # Finally add the button to the container.
        .add_to_container()
    )
    msgID = await gameStartPL.app.rest.fetch_message(message=startMsgID, channel=startChnID)
    await msgID.edit(component=btnGame)
    await gameStartPL.bot.rest.create_interaction_response(eventS.interaction, eventS.interaction.token, response_type=6)

    gameEmbed = hikari.Embed(title=f'{gameFull}',
                             description='Click Join to join the game\nAnd again to leave\n\nWhen ready to start\nCommand initiator click start',
                             )#.set_thumbnail(f'casinomania/images/{gameShort}Thumbnail.png')

    buttons = [
        {'label': 'Start', 'value': f'{gameShort}Start'},
        {'label': 'Join', 'value': f'{gameShort}Join'},
    ]
    gameBtns = eventS.interaction.app.rest.build_action_row()

    for btn in buttons:
        (
            # Adding the buttons into the action row.
            gameBtns.add_button(
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

    msg = await gameStartPL.app.rest.create_message(channel=startChnID, embed=gameEmbed, component=gameBtns)
    guildName = await gameStartPL.bot.rest.fetch_guild(intGuildID)
    starting = True
    players = []
    event = None
    while starting:
        token = None
        interaction = None
        try:
            event = await gameStartPL.bot.wait_for(
                hikari.InteractionCreateEvent,
                timeout=30,
                predicate=lambda e:
                isinstance(e.interaction, hikari.ComponentInteraction)
                # and e.interaction.user.id == ctx.author.id
                and e.interaction.message.id == msg.id
                and e.interaction.component_type == hikari.ComponentType.BUTTON
                and (e.interaction.custom_id == f'{gameShort}Start' or e.interaction.custom_id == f'{gameShort}Join')
            )
            token = event.interaction.token
            interaction = event.interaction
            custID = event.interaction.custom_id
        except:
            custID = f'{gameShort}Start'

        if custID == f'{gameShort}Start':
            print(f'start {gameFull}')
            starting = False
        else:
            member = event.interaction.member

            memberID = member.id
            if memberID in players:
                players.remove(memberID)
                await event.app.rest.create_interaction_response(interaction.id, content='Left', token=token,
                                                                 response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                print(f'{member.user} left {gameFull} in {guildName.name.title()}')

            else:
                players.append(memberID)
                await event.app.rest.create_interaction_response(event.interaction.id, content='Joined', token=token,
                                                                 response_type=4, flags=hikari.MessageFlag.EPHEMERAL)
                print(f'{member.user} joined {gameFull} in {guildName.name.title()}')

    totPlayers = len(players)

    # Create deck for game
    offset = 0
    while totPlayers > 2:  # only increase offset if more than 2 players
        offset += 1
        totPlayers -= 2  # Number of players for one deck

    deck = create_Decks(2 + offset, gameStartPL.bot)
    random.shuffle(deck)

    # Game Logic

    btnGame = event.interaction.app.rest.build_action_row()
    (
        btnGame.add_button(
            # Gray button style, see also PRIMARY, and DANGER.
            hikari.ButtonStyle.SECONDARY,
            # Set the buttons custom ID to the label.
            f'start{gameShort}',
        )
            # Set the actual label.
            .set_label(f'Create {gameFull} Game').set_is_disabled(False)
            # Finally add the button to the container.
            .add_to_container()
    )
    msgID = await gameStartPL.app.rest.fetch_message(message=startMsgID, channel=startChnID)
    await msgID.edit(component=btnGame)
    gameStartPL.d.Gameplaying[str(intGuildID)] = False


def load(bot: lightbulb.BotApp):
    bot.add_plugin(gameStartPL)
    gameStartPL.d.Gameplaying = {}


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(gameStartPL)
