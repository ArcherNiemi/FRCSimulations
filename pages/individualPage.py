from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import ast
import dash

df = pd.read_csv('individualSim.csv')

def fixDictionary(df):
    rows = []

    for _, row in df.iterrows():
        rank_dict = ast.literal_eval(row["ranks"])
        rp_dict = ast.literal_eval(row["rps"])

        new_row = {
            "Team Number": int(row["team"]),
            "Average Rank": round(row["averageRank"], 2),
            "Average Rp": round(row["averageRp"], 2),
        }

        # Add rank probabilities
        for rank in range(1, 55):
            new_row[f"Rank {rank}"] = round(rank_dict.get(rank, 0), 4)

        # Add RP probabilities
        for rp in range(0, 40):
            new_row[f"RP {rp}"] = round(rp_dict.get(rp, 0), 4)

        rows.append(new_row)

    return rows
data = fixDictionary(df)

columnList = (
    [{"field": "Team Number", "width": 150}]
    + [{"field": "Average Rank", "width": 150}]
    + [{"field": "Average Rp", "width": 150}]
    + [{"field": f"Rank {i}", "width": 100} for i in range(1, 55)]
    + [{"field": f"RP {i}", "width": 100} for i in range(39, -1, -1)]
)

dash.register_page(__name__, path="/individualPage")

layout = [
    dag.AgGrid(
        rowData=data,
        columnDefs=columnList,
        defaultColDef={"sortable": True, "filter": True}
    )
]
