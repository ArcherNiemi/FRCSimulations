from dash import html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import dash
import ast

# ------------------------
# LOAD robotMatchSim.csv
# ------------------------
df = pd.read_csv("robotMatchSim.csv")

# Parse RpChances
df["RpChances"] = df["RpChances"].apply(lambda x: ast.literal_eval(x))
rp_df = pd.json_normalize(df["RpChances"]).add_prefix("Rp_")
df = pd.concat([df.drop(columns=["RpChances"]), rp_df], axis=1)

# ------------------------
# SPLIT teams into columns
# ------------------------
df["teams"] = df["teams"].apply(lambda x: ast.literal_eval(x))

df["team1"] = df["teams"].apply(lambda x: x[0] if len(x) > 0 else None)
df["team2"] = df["teams"].apply(lambda x: x[1] if len(x) > 1 else None)
df["team3"] = df["teams"].apply(lambda x: x[2] if len(x) > 2 else None)

df = df.drop(columns=["teams"])

# ------------------------
# LOAD matchSim.csv (comparison data)
# ------------------------
compare_df = pd.read_csv("matchSim.csv")

compare_df = compare_df[
    ["match", "alliance", "Rp", "WinChance"]
].rename(columns={
    "Rp": "compare_Rp",
    "WinChance": "compare_WinChance"
})

# ------------------------
# MERGE + DIFFERENCES
# ------------------------
df = pd.merge(df, compare_df, on=["match", "alliance"], how="left")

df["Rp_diff"] = df["Rp"] - df["compare_Rp"]
df["WinChance_diff"] = df["WinChance"] - df["compare_WinChance"]

# ------------------------
# REGISTER PAGE
# ------------------------
dash.register_page(__name__, path="/robotMatchSimPage")

# ------------------------
# COLUMN ORDER
# ------------------------
base_cols = [
    "team", "rank", "alliance",
    "team1", "team2", "team3",
    "Rp", "compare_Rp", "Rp_diff",
    "WinChance", "compare_WinChance", "WinChance_diff","match"
]

columnDefs = []

ordered_cols = base_cols + [c for c in df.columns if c not in base_cols]

for col in ordered_cols:
    if col == "match":
        colDef = {
            "field": "match",
            "pinned": "left",
            "lockPinned": True,
            "width": 90
        }
    else:
        colDef = {"field": col}

    colDef["cellStyle"] = {
        "styleConditions": [
            # 🔴 too LOW
            {
                "condition": "params.data.Rp_diff <= -0.5",
                "style": {"backgroundColor": "#ff9999","textAlign": "center"},
            },
            # 🟢 too HIGH
            {
                "condition": "params.data.Rp_diff >= 0.5",
                "style": {"backgroundColor": "#99ff99","textAlign": "center"}
            },
            # 🔴 red alliance text
            {
                "condition": "params.data.alliance === 'red'",
                "style": {"color": "red", "textAlign": "center"}
            },
            # 🔵 blue alliance text
            {
                "condition": "params.data.alliance === 'blue'",
                "style": {"color": "blue", "textAlign": "center"}
            }
        ],
        "defaultStyle": {"textAlign": "center"}
    }

    columnDefs.append(colDef)

# ------------------------
# LAYOUT
# ------------------------
layout = html.Div([
    html.Div([
        dcc.Input(
            id="teamInput",
            type="number",
            placeholder="Team",
            style={"marginRight": "10px", "fontSize": "12px"}
        ),
        dcc.Input(
            id="rankInput",
            type="number",
            placeholder="Rank",
            style={"fontSize": "12px"}
        ),
    ], style={"marginBottom": "8px"}),
    html.Div([
        dag.AgGrid(
            id="table",
            columnDefs=columnDefs,
            rowData=df.to_dict("records"),

            defaultColDef={
                "sortable": True,
                "filter": True,
                "resizable": True,
            },

            style={
                "height": "100%",
                "width": "100%",
            },

            className="ag-theme-alpine",
        )], style={"height": "65vh", "overflow": "hidden"})
])

# ------------------------
# CALLBACK
# ------------------------
@callback(
    Output("table", "rowData"),
    Input("teamInput", "value"),
    Input("rankInput", "value"),
)
def update_grid(team, rank):
    filtered = df.copy()

    if team is not None:
        filtered = filtered[filtered["team"] == team]

    if rank is not None:
        filtered = filtered[filtered["rank"] == rank]

    return filtered.to_dict("records")