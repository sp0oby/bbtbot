import re, json

def roundToNearestZero(number):
    n = abs(number)
    if n < 1:
        s = f'{n:.99f}'
        index = re.search('[1-9]', s).start()
        return s[:index + 4]
    else:
        return str(round(n, 2))

def removeDuplicateEntries(allEntries):
    finalEntries = []
    validEntries = []
    for x in allEntries:
        if not x.transactionHash.hex() in finalEntries:
            finalEntries.append(x.transactionHash.hex())
            validEntries.append(x)

    return validEntries

def getHandWithNumber(number):
    data = {
        '0': 'rock',
        '1': 'paper',
        '2': 'scissor',
        '3': 'lizard',
        '4': 'spock'
    }

    return data[str(number)]


def getResult(number):
    data = {
        '1': 'won',
        '0': 'lost',
        '2': 'draw'
    }

    return data[str(number)]


def insertTX(tx):
    currentData = getAllTX()

    with open('./alltx.json', 'w') as file:
        currentData.append(tx)
        json.dump(currentData, file)

def getAllTX():
    with open('./alltx.json', 'r') as file:
        fileData = json.load(file)

    return fileData
