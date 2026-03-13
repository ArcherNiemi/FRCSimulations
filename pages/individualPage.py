# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import ast
import dash

df = pd.read_csv('individualSim.csv')


def fixDictionary(dataFrame):
    newListOfDict = []
    teams = dataFrame["teams"]
    probability = dataFrame["value"].apply(ast.literal_eval)
    for i in range(len(teams)):
        teamName = teams[i]
        newListOfDict.append({"Team Number": teamName})
        for t in range(len(teams)):
            if(t in list(probability[i].keys())):
                newListOfDict[i].update({str(t):f"{round(probability[i][t],2)}"})
            else:
                newListOfDict[i].update({str(t):"0"})
    return newListOfDict

data = fixDictionary(df)

columnList = [{"field": "Team Number", "width":120}] + [{"field": i, "width": 60} for i in list(data[0].keys())[2:]]

dash.register_page(__name__, path="/individualPage")

# App layout
layout = [
    html.Div(children='My First App with Data and a Graph'),
    dag.AgGrid(
        rowData=data,
        columnDefs=columnList
    ),
]
