from casinomania.functions import readWrite
import numpy as np


async def getCardName(num, suit):
    # card = f'{num}_of_{suit}.png'
    return f'{num}_of_{suit}.png'


async def addCoins(guildID, userID, count):
    data = readWrite.readGuildFile(guildID)

    try:
        data = readWrite.readGuildFile(guildID)
    except:
        readWrite.setCCTotal(guildID, userID, 100)
        data = readWrite.readGuildFile(guildID)

    wallet = data[str(userID)]['coins']

    # print(str(data[str(userID)]))
    total = count + int(wallet)
    if wallet == 0:
        total = 5
        # data[str(userID)]['bet'] = 5
        readWrite.setBet(guildID,userID,5)

    readWrite.setCCTotal(guildID=guildID, userID=userID, ccTotal=total)


async def remCoins(guildID, userID, count):
    data = readWrite.readGuildFile(guildID)
    try:
        data[str(userID)]
    except:
        readWrite.setCCTotal(guildID, str(userID), 100)
        data = readWrite.readGuildFile(guildID)
        pass

    # print(str(data[str(userID)]))
    total = int(data[str(userID)]['coins']) - count
    if total < 0:
        total = 0
    readWrite.setCCTotal(guildID=guildID, userID=str(userID), ccTotal=total)

    data = readWrite.readGuildFile(guildID)
    bet = data[str(userID)]['bet']
    wallet = data[str(userID)]['coins']
    # print(bet, wallet)
    if bet > wallet:
        print(data[str(userID)])
        data[str(userID)]['bet'] = wallet
        readWrite.setBet(guildID, str(userID), wallet)
        # readWrite.writeGuildFile(data, guildID)


async def getTotValue(hand):
    total = 0
    num_aces = 0
    for card in hand:
        value = card['value']
        if isinstance(value, int):
            total += value
        else:
            if value in ['jack', 'queen', 'king']:
                total += 10
            else:
                # if total <= 10:
                #     total += 11
                # else:
                #     total += 1
                num_aces += 1

    aceHandVals = ace_values(num_aces)
    temp_total = []
    for val in aceHandVals:
        temp_total.append(val + total)

    toRemove = []
    for tot in temp_total:
        if tot > 21:
            toRemove.append(tot)
    for item in toRemove:
        temp_total.remove(item)
    # print(f'List - {temp_total}')

    if len(temp_total) == 0:
        return 100
    return max(temp_total)

    # return total


def get_ace_values(temp_list):
    sum_array = np.zeros((2**len(temp_list), len(temp_list)))
    # This loop gets the permutations
    for i in range(len(temp_list)):
        n = len(temp_list) - i
        half_len = int(2**n * 0.5)
        for rep in range(int(sum_array.shape[0]/half_len/2)):
            sum_array[rep*2**n : rep*2**n+half_len, i]=1
            sum_array[rep*2**n+half_len : rep*2**n+half_len*2, i]=11
    return [int(s) for s in np.sum(sum_array, axis=1)]


def ace_values(num_aces):
    temp_list = []
    for i in range(num_aces):
        temp_list.append([1,11])
    return get_ace_values(temp_list)


def create_Decks(numDecks, ctx):
    deck = []
    for i in range(numDecks):
        for card in ctx.bot.d.cardValues:
            for suit in ctx.bot.d.suits:
                deck.append({'value': card, 'suit': f'{suit}'})
    return deck


async def make_hand(hand):
    cardNames = []
    for card in hand:
        cardNames.append(await getCardName(card['value'], card['suit']))
    return cardNames
