from dash import html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import dash
import ast

# ------------------------
# LOAD matchSim.csv
# ------------------------
df = pd.read_csv("matchSim.csv")

# ------------------------
# Parse RpChances
# ------------------------
df["RpChances"] = df["RpChances"].apply(lambda x: ast.literal_eval(x))
rp_df = pd.json_normalize(df["RpChances"]).add_prefix("Rp_")
df = pd.concat([df.drop(columns=["RpChances"]), rp_df], axis=1)

# ------------------------
# Split teams column into Team 1/2/3
# ------------------------
df["teams"] = df["teams"].apply(lambda x: ast.literal_eval(x))

df["team1"] = df["teams"].apply(lambda x: x[0] if len(x) > 0 else None)
df["team2"] = df["teams"].apply(lambda x: x[1] if len(x) > 1 else None)
df["team3"] = df["teams"].apply(lambda x: x[2] if len(x) > 2 else None)

df = df.drop(columns=["teams"])

# ------------------------
# Sort so red always first
# ------------------------
df["alliance_order"] = df["alliance"].map({"red": 0, "blue": 1})
df = df.sort_values(["match", "alliance_order"]).drop(columns=["alliance_order"])

# ------------------------
# Register page
# ------------------------
dash.register_page(__name__, path="/matchSimPage")

# ------------------------
# Column order (IMPORTANT)
# ------------------------
ordered_cols = ["match", "team1", "team2", "team3"]

# add remaining columns after
for col in df.columns:
    if col not in ordered_cols:
        ordered_cols.append(col)

columnDefs = []

for col in ordered_cols:
    colDef = {"field": col}

    # Color rows by alliance
    colDef["cellStyle"] = {
        "styleConditions": [
            {
                "condition": "params.data.alliance === 'red'",
                "style": {"color": "red", "textAlign": "center"}
            },
            {
                "condition": "params.data.alliance === 'blue'",
                "style": {"color": "blue", "textAlign": "center"}
            }
        ],
        "defaultStyle": {"textAlign": "center"}
    }

    columnDefs.append(colDef)
# ------------------------
# Layout
# ------------------------
layout = html.Div([
    dag.AgGrid(
        id="table",
        columnDefs=columnDefs,
        rowData=df.to_dict("records"),
        defaultColDef={
            "flex": 1,
            "sortable": True,
            "filter": True,
            "resizable": True,
            "minWidth": 60,
        },
        style={"height": "700px", "width": "100%", "fontSize": "11px"},
    ),html.Hr(),html.Hr(),html.Hr(),html.Hr(),html.Hr()
])