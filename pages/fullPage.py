from dash import Dash, dcc, html, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd
import ast
import dash

df = pd.read_csv("simulation2.csv")

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

def filterDict(teams, rows):
    newDict = {}
    for i in range(len(rows)):
        key = ast.literal_eval(rows[i]["teams"])

        works = True
        for t in range(len(teams)):
            if(not(int(teams[t]) in key)):
                works = False
        if(works):
            newDict[key] = float(rows[i]["probability"])

    rows = [{"teams": str(k), "probability": v} for k, v in newDict.items()]
    return rows

dash.register_page(__name__, path="/fullPage")

layout = html.Div([
    html.Div("My First App with Data and a Graph"),

    dcc.Input(id="depthInput", type="number", placeholder="number", value=2),
    dcc.Input(id="filterInput", type="text", placeholder="number"),

    dag.AgGrid(
        id="output",
        columnDefs=[
            {"field": "teams", "width": 300},
            {"field": "probability"}
        ],
        rowData=[],
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 20
        }
    ),
])


@callback(
    Output("output", "rowData"),
    Input("depthInput", "value"),
    Input("filterInput", "value"),
)
def update_grid(depth, team_filter):

    if depth is None:
        return []

    rows = updateDict(int(depth))

    if team_filter is not None and team_filter != "":
        splitTeams = str(team_filter).split(",")
        rows = filterDict(splitTeams, rows)

    return rows