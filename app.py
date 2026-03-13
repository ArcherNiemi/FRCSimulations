from dash import Dash, html, dcc
import dash

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("My Simulation App"),

    html.Div([
        dcc.Link("Full Page", href="/fullPage"),
        html.Br(),
        dcc.Link("Individual Page", href="/individualPage"),
    ]),

    html.Hr(),

    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True)