import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os

# Initialisation de l'application Dash
app = dash.Dash(__name__)
server = app.server  # utile pour le déploiement ultérieur

# Fonction pour charger les données du cours depuis data.txt
def load_data():
    try:
        df = pd.read_csv("data.txt", names=["timestamp", "price"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        return df
    except Exception as e:
        return pd.DataFrame(columns=["timestamp", "price"])

# Fonction pour charger le rapport quotidien
def load_daily_report():
    if os.path.exists("daily_report.txt"):
        with open("daily_report.txt", "r") as f:
            report = f.read()
        return report
    else:
        return "Aucun rapport disponible"

# Layout de l'application avec deux onglets : Présentation et Dashboard
app.layout = html.Div([
    dcc.Tabs(id="tabs", value="tab-presentation", children=[
        dcc.Tab(label="Présentation", value="tab-presentation"),
        dcc.Tab(label="Dashboard", value="tab-dashboard")
    ]),
    html.Div(id="tabs-content"),
    # Intervalle de mise à jour : toutes les 5 minutes (300000 ms)
    dcc.Interval(
        id="interval-component",
        interval=300000,
        n_intervals=0
    )
])

# Callback pour mettre à jour le contenu selon l'onglet sélectionné et l'intervalle
@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"),
     Input("interval-component", "n_intervals")]
)
def render_content(tab, n):
    if tab == "tab-presentation":
        return html.Div([
            html.H1("Présentation du Projet"),
            html.P("Ce projet scrape en continu le prix de l'action Apple (AAPL) depuis Google Finance, "
                   "génère un rapport quotidien détaillé, et permet un suivi en temps réel via ce dashboard."),
            html.P("L'onglet 'Dashboard' affiche le prix actuel, un graphique d'évolution et le rapport quotidien.")
        ], style={"padding": "20px"})
    elif tab == "tab-dashboard":
        df = load_data()
        if not df.empty:
            last_row = df.iloc[-1]
            current_price = last_row["price"]
            last_update = last_row["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
        else:
            current_price = "N/D"
            last_update = "N/D"

        # Création du graphique à partir des données
        graph = {
            "data": [go.Scatter(x=df["timestamp"], y=df["price"], mode="lines+markers", name="Prix AAPL")] if not df.empty else [],
            "layout": go.Layout(
                title="Évolution du prix d'AAPL",
                xaxis={"title": "Temps"},
                yaxis={"title": "Prix ($)"}
            )
        }

        # Charger le rapport quotidien
        daily_report = load_daily_report()

        return html.Div([
            html.H1("Dashboard"),
            html.Div([
                html.H3(f"Prix actuel : {current_price} $"),
                html.P(f"Dernière mise à jour : {last_update}")
            ], style={"marginBottom": "20px"}),
            dcc.Graph(figure=graph),
            html.H3("Rapport quotidien"),
            html.Pre(daily_report, style={"backgroundColor": "#f9f9f9", "padding": "10px"})
        ], style={"padding": "20px"})

if __name__ == '__main__':
    app.run_server(debug=True)
