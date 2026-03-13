# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import main
main.run()

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')


def fixDictionary(dictionary):
    newListOfDict = []
    for i in range(len(dictionary)):
        teamName = dictionary[i][0]
        newListOfDict.append({"Team Number": teamName})
        for t in range(len(dictionary)):
            if(t in list(dictionary[i][1].keys())):
                newListOfDict[i].update({str(t):f"{round(dictionary[i][1][t],2)}"})
            else:
                newListOfDict[i].update({str(t):"0"})
    return newListOfDict

data = fixDictionary(main.simulateAllTeamsIndividualy())
print(list(data[0].keys()))
print(df.columns)
print([{"field": i} for i in df.columns])
print([{"field": i} for i in list(data[0].keys())])

# Initialize the app
app = Dash()

# App layout
app.layout = [
    html.Div(children='My First App with Data and a Graph'),
    dag.AgGrid(
        rowData=data,
        columnDefs=[{"field": i, "width": 100} for i in list(data[0].keys())]
    ),
]

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
