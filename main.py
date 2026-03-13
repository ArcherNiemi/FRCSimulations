import tba
import pandas as pd
import numpy as np
import copy

eventKey = "2026mnwi"

startMatch = 56
endMatch = 76
offsetMatches = 3


originalRPDictionary = {}
RPDictionary = {}
dataDictionary = {}

matches = tba.get_event_matches(eventKey)

rng = np.random.default_rng()

simulations = 10000

teamList = [111,
112,
167,
525,
695,
967,
2220,
2290,
2358,
2508,
2530,
2531,
2549,
2667,
2977,
2987,
3055,
3061,
3090,
3206,
3284,
3928,
4065,
4143,
4174,
4646,
4663,
4859,
5339,
5541,
5576,
5822,
5847,
5914,
6419,
6420,
7531,
7850,
7858,
9082,
11246]

def run():
    makeRPDictionary()
    makeDataDictionary()
    simulateAllTeamsIndividualy()

def simulateOneTeamPlacing(team):
    global RPDictionary
    placingList = []
    for i in range(simulations):
        for t in range(endMatch - startMatch):
            simulateMatch(t + startMatch)
        if(i % 100 == 0):
            print(i)
        sortedRpDictionary = dict(sorted(RPDictionary.items(), key=lambda item: item[1], reverse=True))
        placingList.append(list(sortedRpDictionary.keys()).index(team) + 1)
        RPDictionary = copy.deepcopy(originalRPDictionary)
    placingDict = {}
    for i in range(len(placingList)):
        if(not(placingList[i] in placingDict)):
            placingDict.update({placingList[i]: 1})
        else:
            placingDict[placingList[i]] += 1
    finalDict = {}
    for i in range(len(placingDict)):
        finalDict.update({list(placingDict.keys())[i]: list(placingDict.values())[i]/simulations})
    finalDict = dict(sorted(finalDict.items(), key=lambda item: item[1], reverse=True))
    print(finalDict)


def simulateAllTeamsIndividualy():
    global RPDictionary
    rawDictionary = {}
    for i in range(len(teamList)):
        rawDictionary.update({teamList[i]: []})
    for i in range(simulations):
        for t in range(endMatch - startMatch):
            simulateMatch(t + startMatch)
        if(i % 100 == 0):
            print(i)
        sortedRpDictionary = dict(sorted(RPDictionary.items(), key=lambda item: item[1], reverse=True))
        for t in range(len(rawDictionary)):
            list(rawDictionary.values())[t].append(list(sortedRpDictionary.keys()).index(list(rawDictionary.keys())[t]) + 1)
        RPDictionary = copy.deepcopy(originalRPDictionary)
    totalFinalDict = {}
    for i in range(len(rawDictionary)):
        placingDict = {}
        for t in range(len(list(rawDictionary.values())[i])):
            if(not(list(rawDictionary.values())[i][t] in placingDict)):
                placingDict.update({list(rawDictionary.values())[i][t]: 1})
            else:
                placingDict[list(rawDictionary.values())[i][t]] += 1
        finalDict = {}
        for t in range(len(placingDict)):
            finalDict.update({list(placingDict.keys())[t]: list(placingDict.values())[t]/simulations})
        finalDict = dict(sorted(finalDict.items(), key=lambda item: item[1], reverse=True))
        totalFinalDict.update({list(rawDictionary.keys())[i]: finalDict})
    totalFinalDict = dict(sorted(totalFinalDict.items(), key=lambda item: list(item[1].values())[0], reverse=True))
    totalFinalDict = dict(sorted(totalFinalDict.items(), key=lambda item: list(item[1].keys())[0]))
    for i in range(len(totalFinalDict)):
        print(f"{list(totalFinalDict.items())[i]}\n")

def makeRPDictionary():
    global RPDictionary
    global originalRPDictionary
    for i in range(len(teamList)):
        RPDictionary.update({teamList[i]: [0,0]})
    for i in range(startMatch - 1):
        for t in range(3):
            RPDictionary[int(matches[i+offsetMatches]["alliances"]["blue"]["team_keys"][t][3:])][0] += matches[i+offsetMatches]["score_breakdown"]["blue"]["rp"]
            RPDictionary[int(matches[i+offsetMatches]["alliances"]["red"]["team_keys"][t][3:])][0] += matches[i+offsetMatches]["score_breakdown"]["red"]["rp"]
    originalRPDictionary = copy.deepcopy(RPDictionary)

def makeDataDictionary():
    global populationMean
    df = pd.read_csv('data.csv')
    totalSum = 0
    totalCount = 0
    for i in range(len(teamList)):
        team = int(teamList[i])
        pointListStr = df.loc[df['Team Number'] == team]['Points'].tolist()
        pointList = [float(item) for item in pointListStr]
        sum = 0
        for i in range(len(pointList)):
            sum += pointList[i]
            totalSum += pointList[i]
            totalCount += 1
        finalList = [len(pointList), sum / len(pointList), np.std(pointList)]
        dataDictionary.update({team: finalList})
    populationMean = totalSum / totalCount

def simulateMatch(number):
    blueTeams = matches[number + offsetMatches]["alliances"]["blue"]["team_keys"]
    redTeams = matches[number + offsetMatches]["alliances"]["red"]["team_keys"]
    redList = []
    blueList = []
    for i in range(3):
        blueList.append(dataDictionary[int(blueTeams[i][3:])])
        redList.append(dataDictionary[int(redTeams[i][3:])])
    redSum = 0
    blueSum = 0
    for i in range(3):
        redSum += (redList[i][2] * rng.standard_t(redList[i][0]-1, size=1) + redList[i][1]).item()
        blueSum += (blueList[i][2] * rng.standard_t(blueList[i][0]-1, size=1) + blueList[i][1]).item()
   
    redRp = 0
    blueRp = 0
    if(redSum > blueSum):
        redRp += 3
    else:
        blueRp += 3
    if(redSum > 100):
        redRp += 1
        if(redSum > 360):
            redRp += 1
    if(blueSum > 100):
        blueRp += 1
        if(blueSum > 360):
            blueRp += 1
    for i in range(3):
        RPDictionary[int(redTeams[i][3:])][0] += redRp
        RPDictionary[int(blueTeams[i][3:])][0] += blueRp
if __name__ == "__main__":
    run()