from dash import Dash, dcc, html, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd
import ast
import dash

df = pd.read_csv("simulateScenarios.csv")

app = Dash()

amountDisplaying = 2

current_page = 0

def updateDict(numberOfPlaces):
    newDict = {}

    teams = df["teams"].apply(ast.literal_eval)

    for i in range(len(teams)):
        key = tuple(teams[i][:numberOfPlaces])

        if key not in newDict:
            newDict[key] = float(df["value"][i])
        else:
            newDict[key] += float(df["value"][i])

    newDict = dict(sorted(newDict.items(), key=lambda item: item[1], reverse=True))

    # convert to AgGrid format
    rows = [{"teams": str(k), "probability": v} for k, v in newDict.items()]
    return rows

def filterDict(teams, ranks, rows):
    newDict = {}
    for i in range(len(rows)):
        key = ast.literal_eval(rows[i]["teams"])

        works = True
        for t in range(len(teams)):
            if(not(int(teams[t]) in key)):
                works = False
                break
            rankWorks = False
            if(ranks != ['None'] and ranks != [""]):
                for w in range(len(ranks)):
                    if(list(ast.literal_eval(rows[i]["teams"])).index(int(teams[t]))+1 == int(ranks[w])):
                        rankWorks = True
                if(rankWorks == False):
                    works = False
        if(works):
            newDict[key] = float(rows[i]["probability"])

    rows = [{"teams": str(k), "probability": round(v,4)} for k, v in newDict.items()]
    return rows

dash.register_page(__name__, path="/fullPage")

layout = html.Div([

    dcc.Input(id="depthInput", type="number", placeholder="depth", value=2),
    dcc.Input(id="teamInput", type="text", placeholder="teams"),
    dcc.Input(id="rankInput", type="text", placeholder="rank"),

    dag.AgGrid(
        id="output",
        columnDefs=[
            {"field": "teams", "width": 350},
            {"field": "probability"}
        ],
        rowData=[],
    ),
    dcc.Textarea(
        id="textArea",
        value="probability: 100%",
        readOnly=True
    )
])


@callback(
    [Output("output", "rowData"),
    Output("textArea", "value")],
    Input("depthInput", "value"),
    Input("teamInput", "value"),
    Input("rankInput", "value"),
)
def update_grid(depth, team_filter, ranks):

    if depth is None:
        return [None, "1"]

    rows = updateDict(int(depth))

    if team_filter is not None and team_filter != "":
        splitRanks = str(ranks).split(",")
        print(splitRanks)
        splitTeams = str(team_filter).split(",")
        rows = filterDict(splitTeams, splitRanks, rows)
    
    sum = 0
    for i in range(len(rows)):
        sum += rows[i]["probability"]

    return [rows, str(round(sum,4))]