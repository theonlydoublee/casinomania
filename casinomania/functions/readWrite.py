import json
import os


def readGuildFile(guildID):
    os.makedirs(f'casinomania/Data/{guildID}', exist_ok=True)

    if not os.path.exists(f'casinomania/Data/{guildID}/{guildID}.json'):
        with open(f'casinomania/Data/{guildID}/{guildID}.json', 'w') as file:
            data = {
                    "bjMsg": {
                        "id": "0",
                        "channel": "0"
                    }
                    }
            json.dump(data, file, indent=2)
        file.close()

    with open(f'casinomania/Data/{guildID}/{guildID}.json', 'r') as file:
        data = json.loads(file.read())
        # print(f"reading: {data}")
        return data


def writeGuildFile(data, guildID):
    os.makedirs(f'casinomania/Data/{guildID}', exist_ok=True)

    with open(f'casinomania/Data/{guildID}/{guildID}.json', 'w') as file:
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


def setBet(guildID, userID, betAmount, game):
    data = readGuildFile(guildID)
    data[str(userID)][f'{game}'] = betAmount
    # print(data)
    # print(f"set: {data}")
    writeGuildFile(data, guildID)


def getBet(guildID, userID, game):
    data = readGuildFile(guildID)
    total = data[str(userID)][f'{game}']
    # print(data)
    # print(f"set: {data}")
    return total
