import tba
import pandas as pd

eventKey = "2026iacf"

allMatches = sorted(tba.get_event_matches(eventKey), key=lambda m: m['match_number'])
qualMatches = [match for match in allMatches if match["comp_level"] == "qm"]

teamList = [3928,10439,11219,3055,4260,5935,6805,7531,8766,6419,4728,7257,5442,4646,2847,2654,1108,167,6147,5041,525,7848,967,2227,3267,648,59,5914,11312,8821,8822,11241,5275,11210,6420,3723,9092,5837,9061,9570,1997,10476,3298,5141,5557,5576,5809,6455,7038,8737,8770,9543,9579]

def findTeamsMatches():
    dictionary = {}
    for i,team in enumerate(teamList):
        teamMatches = findTeamMatches(team)
        dictionary.update({team: teamMatches})
    saveData(dictionary)


def findTeamMatches(team):
    matches = []
    for i,match in enumerate(qualMatches):
        for i,alliance in enumerate(["red","blue"]):
            for i,teamKey in enumerate(match["alliances"][alliance]["team_keys"]):
                if(team == int(teamKey[3:])):
                    matches.append(int(match["match_number"]))
    return matches


def saveData(dictionary):
    rows = []
    for team, matches in dictionary.items():
        rows.append({
            "teams": team,
            "matches": matches
        })

    df = pd.DataFrame(rows)
    df.to_csv("matches.csv", index=False)

if __name__ == "__main__":
    findTeamsMatches()