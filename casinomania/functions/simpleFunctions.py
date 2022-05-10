from casinomania.functions import readWrite


async def getCardName(num, suit):
    # card = f'{num}_of_{suit}.png'
    return f'{num}_of_{suit}.png'


async def addCoins(guildID, userID, count):
    data = readWrite.readGuildFile(guildID)
    print(str(data[str(userID)]))
    total = count + int(data[str(userID)])
    readWrite.setGuildFile(guildID=guildID, userID=userID, ccTotal=total)


async def remCoins(guildID, userID, count):
    data = readWrite.readGuildFile(guildID)
    print(str(data[str(userID)]))
    total = int(data[str(userID)]) - count
    if total < 0:
        total = 0
    readWrite.setGuildFile(guildID=guildID, userID=userID, ccTotal=total)

