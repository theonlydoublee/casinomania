import json
import os


def readGuildFile(guildID):
    if not os.path.exists(f'casinomania/Data/{guildID}.json'):
        with open(f'casinomania/Data/{guildID}.json', 'w') as file:
            data = {
                        # userID: 100
                    }
            json.dump(data, file, indent=2)
        file.close()

    with open(f'casinomania/Data/{guildID}.json', 'r') as file:
        data = json.loads(file.read())
        # print(f"reading: {data}")
        return data


def writeGuildFile(data, guildID):
    with open(f'casinomania/Data/{guildID}.json', 'w') as file:
        json.dump(data, file, indent=2)
        # print(f"writing: {data}")
        file.close()


def setCCTotal(guildID, userID, ccTotal):
    data = readGuildFile(guildID)
    data[str(userID)]['coins'] = ccTotal
    # print(data)
    # print(f"set: {data}")
    writeGuildFile(data, guildID)


def getCCTotal(guildID, userID):
    data = readGuildFile(guildID)
    total = data[str(userID)]['coins']
    # print(data)
    # print(f"set: {data}")
    return total


def setBet(guildID, userID, betAmount):
    data = readGuildFile(guildID)
    data[str(userID)]['bet'] = betAmount
    # print(data)
    # print(f"set: {data}")
    writeGuildFile(data, guildID)


def getBet(guildID, userID):
    data = readGuildFile(guildID)
    total = data[str(userID)]['bet']
    # print(data)
    # print(f"set: {data}")
    return total
