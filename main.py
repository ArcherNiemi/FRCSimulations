import tba
import pandas as pd
import numpy as np
import random

print("started")
#configure Settings
eventKey = "2026iacf"
startMatch = 52
endMatch = 71
simulations = 10000
matchesPerTeam = 8
teamList = [3928,10439,11219,3055,4260,5935,6805,7531,8766,6419,4728,7257,5442,4646,2847,2654,1108,167,6147,5041,525,7848,967,2227,3267,648,59,5914,11312,8821,8822,11241,5275,11210,6420,3723,9092,5837,9061,9570,1997,10476,3298,5141,5557,5576,5809,6455,7038,8737,8770,9543,9579]

simulationDictionary = {} # {match number: {alliance: {teams: [], score: , win: , rp gained: }}}
dataDictionary = {} # {matches played: , average score: ,stdev: }

startRpDictionary = {} #{teamNum: rp}
endRpDictionary = {} #{teamNum: rp}

startAverageMatchDictionary = {} #{teamNum: {averageMatch: 0, matchCount: 0}}
endAverageMatchDictionary = {} #{teamNum: {averageMatch: 0, matchCount: 0}}

individualSimDictionary = {} #{teamNum: {rank: (sum), rp: (sum), ranks: {rank: (count)}, rps: {rp: (count)}}} -> {teamNum: {averageRank: , averagePlace: , ranks: {rank: percent}, rps: {rp: percent}}}
topSimDictionary = {} #{(1st team, 2nd team , ... , 8th team): sum} -> {(1st team, 2nd team , ... , 8th team): percent}
matchSimDictionary = {} #{match: {alliance: {scoreSum: , scoreSquareSum: , winSum: , rpSum: , rpSumChances: {rp: sum}}}} -> {match: {alliance: {averageScore: , stdevScore: , winChange: , averageRp: , rpChances: {rp: percent}}}}
robotMatchSimDictionary = {} #{team: {rank: {match: {alliance: {scoreSum: , scoreSquareSum: , winSum: , rpSum: , rpSumChances: {rp: sum}, count: }}}}} -> {team: {rank: {match: {alliance: {averageScore: , stdevScore: , winChange: , averageRp: , rpChances: {rp: percent}}}}}}

runRobotMatchSim = True

allMatches = sorted(tba.get_event_matches(eventKey), key=lambda m: m['match_number'])
qualMatches = [match for match in allMatches if match["comp_level"] == "qm"]
print("got TBA data")


rng = np.random.default_rng()

def main():
    configureDicts()
    print("configured dictionaries")
    simulate()
    print("finished simulating")
    compileDicts()
    print("finished compliling")
    saveDicts()
    print("saved data")

def configureDicts():
    makeSimulationDictionary()
    makeDataDictionary()
    makeRpDictionary()
    makeAverageMatchDictionary()

    makeIndividualSimDictionary()
    makeMatchSimDictionary()
    if(runRobotMatchSim):
        makeRobotMatchSimDictionary()


def makeSimulationDictionary():
    global simulationDictionary

    simulationDictionary = {}
    for i in range(endMatch - (startMatch-1)):
        matchNum = i+startMatch
        simulationDictionary.update({matchNum: {'red': {'teams': [], 'score': 0, 'win': False, 'rp': 0}, 'blue': {'teams': [], 'score': 0, 'win': False, 'rp': 0}}})

def makeDataDictionary():
    df = pd.read_csv('data.csv')
    for i, team in enumerate(teamList):
        teamScores = getTeamScores(df, team)

        numberOfDataPoints = len(teamScores)
        averageScore = np.average(teamScores)
        stdevOfScores = np.std(teamScores)

        dataDictionary.update({team: {'dataPoints': numberOfDataPoints, 'average': averageScore, 'stdev': stdevOfScores}})

def makeRpDictionary():
    makeInitialRpDictionary()

    for i in range(startMatch-1):
        matchNum = i+1
        teams = getTeams(matchNum)
        for i, team in enumerate(teams):
            if(i < 3):
                startRpDictionary[team] += getMatchRp(matchNum, 'red')
            else:
                startRpDictionary[team] += getMatchRp(matchNum, 'blue')
        

def getMatchRp(match, alliance):
    return qualMatches[match-1]["score_breakdown"][alliance]["rp"]

def makeInitialRpDictionary():
    for i,team in enumerate(teamList):
        startRpDictionary.update({team: 0})

def makeAverageMatchDictionary():
    makeInitialAverageMatchDictionary()

    for i in range(startMatch-1):
        matchNum = i+1
        teams = getTeams(matchNum)
        for i, team in enumerate(teams):
            startAverageMatchDictionary[team]['matchCount'] += 1
            if(i < 3):
                startAverageMatchDictionary[team]['averageMatch'] += getMatchScore(matchNum, 'red')
            else:
                startAverageMatchDictionary[team]['averageMatch'] += getMatchScore(matchNum, 'blue')
        

def getMatchScore(match, alliance):
    return qualMatches[match-1]["alliances"][alliance]["score"]

def makeInitialAverageMatchDictionary():
    for i,team in enumerate(teamList):
        startAverageMatchDictionary.update({team: {'averageMatch': 0, 'matchCount': 0}})

def getTeamScores(df, team):
    scores = df.loc[df['Team Number'] == team]['Points'].tolist()
    if(scores == []):
        return [0]
    else:
        return scores

def makeIndividualSimDictionary():
    for i, team in enumerate(teamList):
        individualSimDictionary.update({team: {"rank": 0, "rp": 0, "ranks": {}, "rps": {}}})

def makeMatchSimDictionary():
    for i in range(endMatch - (startMatch-1)):
        matchNum = i+startMatch
        matchSimDictionary.update({matchNum: {"red": {"scoreSum": 0, "scoreSquareSum": 0, "winSum": 0, "rpSum": 0, "rpSumChances": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}}, 
                                              "blue": {"scoreSum": 0, "scoreSquareSum": 0, "winSum": 0, "rpSum": 0, "rpSumChances": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}}}})

def makeRobotMatchSimDictionary():
    for i, team in enumerate(teamList):
        robotMatchSimDictionary.update({team: {}})

def simulate():
    global endRpDictionary
    for i in range(simulations):
        simulateAllMatches()

        if(i % 100 == 0):
            print(i)

        endRpDictionary = getAllTeamsRP()

        updateDicts()

        makeSimulationDictionary()

def simulateAllMatches():
    for i in range(endMatch - (startMatch-1)):
        matchNum = i+startMatch
        simulateMatch(matchNum)

def simulateMatch(number):
    teams = getTeams(number)
    teamsData = getTeamData(teams)

    redAlliancePoints  = simulateAlliancePoints(teamsData[:3])
    blueAlliancePoints = simulateAlliancePoints(teamsData[3:])
    
    updateSimulationDict(number, teams, redAlliancePoints, blueAlliancePoints)

def getTeams(matchNumber):
    blueTeams = qualMatches[matchNumber-1]["alliances"]["blue"]["team_keys"]
    redTeams  = qualMatches[matchNumber-1]["alliances"]["red" ]["team_keys"]
    allTeams = redTeams + blueTeams
    return teamKeysToInts(allTeams)

def teamKeysToInts(teams):
    intTeams = []
    for i,team in enumerate(teams):
        intTeams.append(int(team[3:]))
    return intTeams

def getTeamData(teams):
    data = []
    for i,team in enumerate(teams):
        data.append(dataDictionary[team])
    return data

def simulateAlliancePoints(teamsData):
    totalPoints = 0
    for i, teamData in enumerate(teamsData):
        totalPoints += simulateRobotPoints(teamData)
    return totalPoints

def simulateRobotPoints(data):
    points = 0
    if(data['dataPoints'] > 1):
        points = (data['stdev'] * rng.standard_t(data['dataPoints']-1, size=1) + data['average']).item()
    else:
        points = random.uniform(data['average']/2,data['average']*1.5)
    return points

#give rp and determine winner
def updateSimulationDict(match, teams, redPoints, bluePoints):
    global simulationDictionary
    
    if(redPoints > bluePoints):
        redWin = True
        blueWin = False
    else:
        redWin = False
        blueWin = True

    redRp = determineRP(redWin, redPoints)
    blueRp = determineRP(blueWin, bluePoints)

    simulationDictionary[match]['red']['teams'] = teams[:3]
    simulationDictionary[match]['red']['score'] = redPoints
    simulationDictionary[match]['red']['win'] = redWin
    simulationDictionary[match]['red']['rp'] = redRp

    simulationDictionary[match]['blue']['teams'] = teams[3:]
    simulationDictionary[match]['blue']['score'] = bluePoints
    simulationDictionary[match]['blue']['win'] = blueWin
    simulationDictionary[match]['blue']['rp'] = blueRp

    
def determineRP(win, points):
    rp = 0
    if(win):
        rp += 3
    if(points > 100):
        rp += 1
    if(points > 360):
        rp += 1
    return rp

def getAllTeamsRP():
    allTeamsRp = {} #{teamNum: rp}
    for i,team in enumerate(teamList):
        allTeamsRp.update({team: getTeamRP(team) + startRpDictionary[team]})
    return sortRpDict(allTeamsRp)

def getTeamRP(team):
    rp = 0
    teamsMatches = getTeamsMatches(team)

    for i,match in enumerate(teamsMatches):
        matchNum = match['matchNumber']
        alliance = match['alliance']

        rp += simulationDictionary[matchNum][alliance]['rp']

    return rp

def getTeamsMatches(team):
    teamsMatchs = [] #[{alliance: , matchNumber: }]
    for index, (matchNum, matchStats) in enumerate(simulationDictionary.items()):
        if(team in matchStats['red']['teams']):
            teamsMatchs.append({'alliance': 'red', 'matchNumber': matchNum})
        elif(team in matchStats['blue']['teams']):
            teamsMatchs.append({'alliance': 'blue', 'matchNumber': matchNum})
    return teamsMatchs

def sortRpDict(dictionary):
    endAverageMatchDictionary = getTeamAverageMatch()
    matchScoreSorted = dict(sorted(dictionary.items(), key=lambda x: endAverageMatchDictionary.get(x, 0)))
    return dict(sorted(matchScoreSorted.items(), key=lambda item: item[1], reverse=True))

def getTeamAverageMatch():
    allTeamsAverageMatch = {} #{teamNum: averageMatch}
    for i,team in enumerate(teamList):
        totalScore = getTeamTotalScore(team) + startAverageMatchDictionary[team]['averageMatch']
        averageScore = totalScore / matchesPerTeam
        allTeamsAverageMatch.update({team: averageScore})
    return allTeamsAverageMatch



def getTeamTotalScore(team):
    score = 0
    teamsMatches = getTeamsMatches(team)
    for i,match in enumerate(teamsMatches):
        if(startAverageMatchDictionary[team]['matchCount'] + i + 1 > matchesPerTeam):
            return score
        matchNum = match['matchNumber']
        alliance = match['alliance']

        score += simulationDictionary[matchNum][alliance]['score']
    return score

def updateDicts():
    updateIndividualSimDict()
    updateTopSimDict()
    updateMatchSimDict()
    if(runRobotMatchSim):
        updateRobotMatchSimDict()

def updateIndividualSimDict():
    addRpsToIndividualSimDict(endRpDictionary)

def addRpsToIndividualSimDict(rps):
    for i,team in enumerate(teamList):
        rank = list(rps).index(team) + 1
        rp = rps[team]
        individualSimDictionary[team]["rank"] += rank
        individualSimDictionary[team]["rp"] += rp
        updateIndividualSimRanks(team, rank)
        updateIndividualSimRps(team, rp)

def updateIndividualSimRanks(team, rank):
    if(rank in individualSimDictionary[team]["ranks"]):
        individualSimDictionary[team]["ranks"][rank] += 1
    else:
        individualSimDictionary[team]["ranks"].update({rank: 1})

def updateIndividualSimRps(team, rp):
    if(rp in individualSimDictionary[team]["rps"]):
        individualSimDictionary[team]["rps"][rp] += 1
    else:
        individualSimDictionary[team]["rps"].update({rp: 1})

def updateTopSimDict():
    topEightTeams = tuple(endRpDictionary.keys())[:8]
    if(topEightTeams in topSimDictionary):
        topSimDictionary[topEightTeams] += 1
    else:
        topSimDictionary.update({topEightTeams: 1})


def updateMatchSimDict():
    for i,(matchNum, matchStats) in enumerate(simulationDictionary.items()):
        redSimData = getMatchSimData(matchStats["red"])
        blueSimData = getMatchSimData(matchStats["blue"])

        matchSimMatch = matchSimDictionary[matchNum]

        updateMatchSimScores(matchSimMatch, redSimData, blueSimData)
        updateMatchSimSquareScores(matchSimMatch, redSimData, blueSimData)
        updateMatchSimWins(matchSimMatch, redSimData, blueSimData)
        updateMatchSimRps(matchSimMatch, redSimData, blueSimData)
        updateMatchSimRpChances(matchSimMatch, redSimData, blueSimData)


def getMatchSimData(stats):
    if(stats["win"]):
        binaryWin = 1
    else:
        binaryWin = 0
    return {"score": stats["score"], "win": binaryWin, "rp": stats["rp"]}

def updateMatchSimScores(matchSimMatch, redSimData, blueSimData):
    matchSimMatch["red"]["scoreSum"] += redSimData["score"]
    matchSimMatch["blue"]["scoreSum"] += blueSimData["score"]

def updateMatchSimSquareScores(matchSimMatch, redSimData, blueSimData):
    matchSimMatch["red"]["scoreSquareSum"] += redSimData["score"] ** 2
    matchSimMatch["blue"]["scoreSquareSum"] += blueSimData["score"] ** 2

def updateMatchSimWins(matchSimMatch, redSimData, blueSimData):
    matchSimMatch["red"]["winSum"] += redSimData["win"]
    matchSimMatch["blue"]["winSum"] += blueSimData["win"]

def updateMatchSimRps(matchSimMatch, redSimData, blueSimData):
    matchSimMatch["red"]["rpSum"] += redSimData["rp"]
    matchSimMatch["blue"]["rpSum"] += blueSimData["rp"]

def updateMatchSimRpChances(matchSimMatch, redSimData, blueSimData):
    matchSimMatch["red"]["rpSumChances"][redSimData["rp"]] += 1
    matchSimMatch["blue"]["rpSumChances"][blueSimData["rp"]] += 1

def updateMatchSimCount(matchSimMatch, redSimData, blueSimData):
    matchSimMatch["red"]["count"] += 1
    matchSimMatch["blue"]["count"] += 1

def updateRobotMatchSimDict():
    for i,team in enumerate(teamList):
        rank = getTeamRank(team)

        checkIfRankExists(team, rank)

        for i,(matchNum, matchStats) in enumerate(simulationDictionary.items()):
            redSimData = getMatchSimData(matchStats["red"])
            blueSimData = getMatchSimData(matchStats["blue"])
            
            robotMatchSimMatch = robotMatchSimDictionary[team][rank][matchNum]

            updateMatchSimScores(robotMatchSimMatch, redSimData, blueSimData)
            updateMatchSimSquareScores(robotMatchSimMatch, redSimData, blueSimData)
            updateMatchSimWins(robotMatchSimMatch, redSimData, blueSimData)
            updateMatchSimRps(robotMatchSimMatch, redSimData, blueSimData)
            updateMatchSimRpChances(robotMatchSimMatch, redSimData, blueSimData)
            updateMatchSimCount(robotMatchSimMatch, redSimData, blueSimData)


def getTeamRank(team):
    return list(endRpDictionary.keys()).index(team)+1

def checkIfRankExists(team, rank):
    if(not(rank in robotMatchSimDictionary[team])):
        addRankToRobotMatchSimDict(team, rank)

def addRankToRobotMatchSimDict(team, rank):
    newDict = {}

    for i in range(endMatch - (startMatch-1)):
        matchNum = i+startMatch
        newDict.update({matchNum: {"red": {"scoreSum": 0, "scoreSquareSum": 0, "winSum": 0, "rpSum": 0, "rpSumChances": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}, "count": 0}, 
                                   "blue": {"scoreSum": 0, "scoreSquareSum": 0, "winSum": 0, "rpSum": 0, "rpSumChances": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}, "count": 0}}})
    
    robotMatchSimDictionary[team].update({rank: newDict})


def compileDicts():
    compileIndividualSimDict()
    compileTopSimDict()
    compileMatchSimDict()
    if(runRobotMatchSim):
        compileRobotMatchSimDict()

def compileIndividualSimDict():
    global individualSimDictionary
    compiledDict = {}
    for i,team in enumerate(teamList):
        averageRank = getAverageRank(team)
        averageRp = getAverageRp(team)
        allRanks = getAllRanks(team)
        allRps = getAllRps(team)
        compiledDict.update({team: {"averageRank": averageRank, "averageRp": averageRp, "ranks": allRanks, "rps": allRps}})
    individualSimDictionary = sortIndividualSimDict(compiledDict)
    
def sortIndividualSimDict(dictionary):
    return dict(sorted(dictionary.items(), key=lambda item: item[1]["averageRank"]))

def getAverageRank(team):
    return individualSimDictionary[team]["rank"]/simulations

def getAverageRp(team):
    return individualSimDictionary[team]["rp"]/simulations

def getAllRanks(team):
    countRanks = individualSimDictionary[team]["ranks"]
    percentRanks = turnCountIntoPercent(countRanks)
    return sortStats(percentRanks, False, 0)

def turnCountIntoPercent(stats):
    newStats = {}
    for i,stat in enumerate(stats.keys()):
        newStats.update({stat: stats[stat]/simulations})
    return newStats

def sortStats(stats, sortReverse, index):
    return dict(sorted(stats.items(), key=lambda item: item[index], reverse=sortReverse))

def getAllRps(team):
    countRanks = individualSimDictionary[team]["rps"]
    percentRanks = turnCountIntoPercent(countRanks)
    return sortStats(percentRanks, True, 0)

def compileTopSimDict():
    global topSimDictionary
    percentDict = turnCountIntoPercent(topSimDictionary)
    topSimDictionary = sortStats(percentDict, True, 1)

def compileMatchSimDict():
    for i,(matchNum, matchStats) in enumerate(matchSimDictionary.items()):
        for i,alliance in enumerate(["red", "blue"]):
            averageScore, winChance, averageRp = getMatchSimAverages(matchStats[alliance]["scoreSum"], matchStats[alliance]["winSum"], matchStats[alliance]["rpSum"],simulations)
            stdevScore = round(calculateStdev(matchStats[alliance]["scoreSum"],matchStats[alliance]["scoreSquareSum"],simulations),2)
            rpChances = getRpChances(matchStats[alliance]["rpSumChances"], simulations)
            matchSimDictionary[matchNum][alliance] = {"averageScore": averageScore, "stdevScore": stdevScore, "winChance": winChance, "averageRp": averageRp, "rpChances": rpChances}


def createMatchSimLists(stats):
    scores = []
    wins = []
    rps = []
    for i,matchStat in enumerate(stats):
        scores.append(matchStat["score"])
        if(matchStat["win"]):
            wins.append(1)
        else:
            wins.append(0)
        rps.append(matchStat["rp"])
    return (scores, wins, rps)

def getMatchSimAverages(scoreSum, winSum, rpSum, count):
    averageScore = round(scoreSum/count,2)
    winChange = round(winSum/count,5)
    averageRp = round(rpSum/count,2)
    return (averageScore, winChange, averageRp)

def calculateStdev(sum, squareSum, count):
    if(count <= 1):
        return 0
    else:
        sumOfSquaredDeviations = squareSum - ((sum**2)/count)
        variance = sumOfSquaredDeviations/(count-1)
        stdev = variance**0.5
        return stdev

def getRpChances(rpSums,count):
    rpPercents = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    for i, (rp, rpCount) in enumerate(rpSums.items()):
        rpPercents[rp] = round(rpCount / count,5)
    return rpPercents

def compileRobotMatchSimDict():
    for teamI,(team, teamStats) in enumerate(robotMatchSimDictionary.items()):
        for rankI,(rank, rankStats) in enumerate(teamStats.items()):
            for matchI,(matchNum, matchStats) in enumerate(rankStats.items()):
                for i,alliance in enumerate(["red", "blue"]):
                    averageScore, winChance, averageRp = getMatchSimAverages(matchStats[alliance]["scoreSum"], matchStats[alliance]["winSum"], matchStats[alliance]["rpSum"],matchStats[alliance]["count"])
                    stdevScore = round(calculateStdev(matchStats[alliance]["scoreSum"],matchStats[alliance]["scoreSquareSum"],matchStats[alliance]["count"]),2)
                    rpChances = getRpChances(matchStats[alliance]["rpSumChances"],matchStats[alliance]["count"])
                    robotMatchSimDictionary[team][rank][matchNum][alliance] = {"averageScore": averageScore, "stdevScore": stdevScore, "winChance": winChance, "averageRp": averageRp, "rpChances": rpChances}

def saveDicts():
    saveIndividualSimDictionary(individualSimDictionary)
    saveTopSimDictionary(topSimDictionary)
    saveMatchSimDictionary(matchSimDictionary)
    if(runRobotMatchSim):
        saveRobotMatchSimDictionary(robotMatchSimDictionary)

def saveIndividualSimDictionary(dictionary):
    rows = []
    for team, info in dictionary.items():
        rows.append({
            "team": team,
            "averageRank": float(info["averageRank"]),
            "averageRp": float(info["averageRp"]),
            "ranks": info["ranks"],
            "rps": info["rps"]
        })

    df = pd.DataFrame(rows)
    df.to_csv("individualSim.csv", index=False)

def saveTopSimDictionary(dictionary):
    rows = []
    for teams, percent in dictionary.items():
        rows.append({
            "percent": percent,
            "teams": teams
        })

    df = pd.DataFrame(rows)
    df.to_csv("topSim.csv", index=False)

def saveMatchSimDictionary(dictionary):
    rows = []
    for matchNum, stats in dictionary.items():
            rows.append({
                "match": matchNum,
                "redScore": stats["red"]["averageScore"],
                "redStdev": stats["red"]["stdevScore"],
                "redRp": stats["red"]["averageRp"],
                "redWinChance": stats["red"]["winChance"],
                "redRpChances": stats["red"]["rpChances"],
                "blueScore": stats["blue"]["averageScore"],
                "blueStdev": stats["blue"]["stdevScore"],
                "blueRp": stats["blue"]["averageRp"],
                "blueWinChance": stats["blue"]["winChance"],
                "blueRpChances": stats["blue"]["rpChances"]
            })

    df = pd.DataFrame(rows)
    df.to_csv("matchSim.csv", index=False)

def saveRobotMatchSimDictionary(dictionary):
    rows = []
    for teamNum, teamStats in dictionary.items():
        for rankNum, rankStats in teamStats.items():
            for matchNum, matchStats in rankStats.items():
                rows.append({
                    "team": teamNum,
                    "rank": rankNum,
                    "match": matchNum,
                    "redScore": matchStats["red"]["averageScore"],
                    "redStdev": matchStats["red"]["stdevScore"],
                    "redRp": matchStats["red"]["averageRp"],
                    "redWinChance": matchStats["red"]["winChance"],
                    "redRpChances": matchStats["red"]["rpChances"],
                    "blueScore": matchStats["blue"]["averageScore"],
                    "blueStdev": matchStats["blue"]["stdevScore"],
                    "blueRp": matchStats["blue"]["averageRp"],
                    "blueWinChance": matchStats["blue"]["winChance"],
                    "blueRpChances": matchStats["blue"]["rpChances"]
                })

    df = pd.DataFrame(rows)
    df.to_csv("robotMatchSim.csv", index=False)
    
if __name__ == "__main__":
    main()