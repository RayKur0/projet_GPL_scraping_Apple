import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
from datetime import datetime

# Initialisation de l'application Dash
app = dash.Dash(__name__)
server = app.server  # utile pour le déploiement

# Fonction pour charger les données depuis data.txt
def load_data():
    try:
        # Lecture du fichier et conversion du prix en float après suppression du symbole '$'
        df = pd.read_csv("data.txt", names=["timestamp", "price"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = df['price'].str.replace('$','', regex=False).astype(float)
        return df
    except Exception as e:
        return pd.DataFrame(columns=["timestamp", "price"])

# Fonction pour charger le rapport quotidien depuis daily_report.txt
def load_daily_report():
    if os.path.exists("daily_report.txt"):
        with open("daily_report.txt", "r") as f:
            return f.read()
    else:
        return "Aucun rapport disponible"

# Layout de l'application avec deux onglets et un style centré et moderne
app.layout = html.Div(style={
    "textAlign": "center",
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#f2f2f2",
    "padding": "20px"
}, children=[
    dcc.Tabs(id="tabs", value="tab-presentation", children=[
        dcc.Tab(label="Présentation", value="tab-presentation", style={"padding": "10px"}, selected_style={"backgroundColor": "#d9d9d9"}),
        dcc.Tab(label="Dashboard", value="tab-dashboard", style={"padding": "10px"}, selected_style={"backgroundColor": "#d9d9d9"})
    ]),
    html.Div(id="tabs-content"),
    dcc.Interval(id="interval-component", interval=300000, n_intervals=0)  # actualisation toutes les 5 minutes
])

# Callback pour mettre à jour le contenu selon l'onglet sélectionné et l'intervalle
@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"), Input("interval-component", "n_intervals")]
)
def render_content(tab, n):
    if tab == "tab-presentation":
        return html.Div([
            html.H1("Présentation du Projet"),
            html.P("Ce projet a pour objectif de scraper en continu le prix de l'action Apple (AAPL) depuis Google Finance, "
                   "de générer un rapport quotidien détaillé, et de permettre un suivi en temps réel via ce dashboard."),
            html.P("L'onglet 'Dashboard' affiche le prix actualisé, un graphique d'évolution, ainsi que le rapport quotidien.")
        ], style={"padding": "20px"})
    
    elif tab == "tab-dashboard":
        df = load_data()
        if not df.empty:
            last_row = df.iloc[-1]
            current_price = last_row["price"]
            last_update_str = last_row["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
        else:
            current_price = "N/D"
            last_update_str = "N/D"

        # Création du graphique d'évolution du prix
        graph = {
            "data": [go.Scatter(x=df["timestamp"], y=df["price"], mode="lines+markers", name="Prix d'Apple")] if not df.empty else [],
            "layout": go.Layout(
                title="Evolution du prix d'Apple",
                xaxis={"title": "Temps"},
                yaxis={"title": "Prix ($)"},
                paper_bgcolor="#f2f2f2",
                plot_bgcolor="#ffffff"
            )
        }
        
        daily_report = load_daily_report()
        
        return html.Div([
            html.H1("Dashboard"),
            html.Div([
                html.H3(f"Prix actualisé : {current_price} $"),
                html.P(f"Dernière mise à jour : {last_update_str}")
            ], style={"marginBottom": "20px", "fontSize": "18px"}),
            dcc.Graph(figure=graph),
            html.H3("Rapport quotidien"),
            html.Pre(daily_report, style={
                "backgroundColor": "#e6e6e6",
                "padding": "15px",
                "borderRadius": "5px",
                "textAlign": "left",
                "display": "inline-block",
                "maxWidth": "800px"
            })
... (5lignes restantes)
Réduire
message.txt
5 Ko
http://13.53.143.232:8050/
RayKur0 — 23:10
tien push ca dans le app.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
from datetime import datetime

# Initialisation de l'application Dash
app = dash.Dash(__name__)
server = app.server  # utile pour le déploiement

# Fonction pour charger les données depuis data.txt
def load_data():
    try:
        df = pd.read_csv("data.txt", names=["timestamp", "price"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = df['price'].str.replace('$','', regex=False).astype(float)
        return df
    except Exception as e:
        return pd.DataFrame(columns=["timestamp", "price"])

# Fonction pour charger le rapport journalier depuis daily_report.txt
def load_daily_report():
    if os.path.exists("daily_report.txt"):
        with open("daily_report.txt", "r") as f:
            return f.read()
    else:
        return "Aucun rapport disponible"

# Layout de l'application avec deux onglets et un style moderne et centré
app.layout = html.Div(style={
    "textAlign": "center",
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#f2f2f2",
    "padding": "20px"
}, children=[
    dcc.Tabs(id="tabs", value="tab-presentation", children=[
        dcc.Tab(label="Présentation", value="tab-presentation", style={"padding": "10px"}, selected_style={"backgroundColor": "#d9d9d9"}),
        dcc.Tab(label="Dashboard", value="tab-dashboard", style={"padding": "10px"}, selected_style={"backgroundColor": "#d9d9d9"})
    ]),
    html.Div(id="tabs-content"),
    dcc.Interval(id="interval-component", interval=300000, n_intervals=0)  # actualisation toutes les 5 minutes
])

# Callback pour mettre à jour le contenu selon l'onglet sélectionné et l'intervalle
@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"), Input("interval-component", "n_intervals")]
)
def render_content(tab, n):
    if tab == "tab-presentation":
        return html.Div([
            html.H1("Présentation du Projet"),
            html.P("Ce projet a pour objectif de scraper en continu le cours de la crypto XRP depuis Cryptoast, "
                   "de générer un rapport journalier détaillé, et de permettre un suivi en temps réel via ce dashboard."),
            html.P("L'onglet 'Dashboard' affiche le prix actualisé, un graphique d'évolution, ainsi que le rapport journalier.")
        ], style={"padding": "20px"})
    
    elif tab == "tab-dashboard":
        df = load_data()
        if not df.empty:
            last_row = df.iloc[-1]
            current_price = last_row["price"]
            last_update_str = last_row["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
        else:
            current_price = "N/D"
            last_update_str = "N/D"
        
        # Création du graphique d'évolution du prix
        graph = {
            "data": [go.Scatter(x=df["timestamp"], y=df["price"], mode="lines+markers", name="Prix XRP")] if not df.empty else [],
            "layout": go.Layout(
                title="Evolution du prix d'XRP",
                xaxis={"title": "Temps"},
                yaxis={"title": "Prix ($)"},
                paper_bgcolor="#f2f2f2",
                plot_bgcolor="#ffffff"
            )
        }
        
        daily_report = load_daily_report()
        
        return html.Div([
            html.H1("Dashboard"),
            html.Div([
                html.H3(f"Prix actualisé : {current_price} $"),
                html.P(f"Dernière mise à jour : {last_update_str}")
            ], style={"marginBottom": "20px", "fontSize": "18px"}),
            dcc.Graph(figure=graph),
            html.H3("Rapport journalier"),
            html.Pre(daily_report, style={
                "backgroundColor": "#e6e6e6",
                "padding": "15px",
                "borderRadius": "5px",
                "textAlign": "left",
                "display": "inline-block",
                "maxWidth": "800px"
            })
        ], style={"padding": "20px"})
... (4lignes restantes)
Réduire
message.txt
5 Ko
Tu as manqué un appel de RayKur0 qui a duré quelques secondes. — 23:10
DariusMercury a commencé un appel. — 23:16
﻿
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
from datetime import datetime

# Initialisation de l'application Dash
app = dash.Dash(__name__)
server = app.server  # utile pour le déploiement

# Fonction pour charger les données depuis data.txt
def load_data():
    try:
        df = pd.read_csv("data.txt", names=["timestamp", "price"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = df['price'].str.replace('$','', regex=False).astype(float)
        return df
    except Exception as e:
        return pd.DataFrame(columns=["timestamp", "price"])

# Fonction pour charger le rapport journalier depuis daily_report.txt
def load_daily_report():
    if os.path.exists("daily_report.txt"):
        with open("daily_report.txt", "r") as f:
            return f.read()
    else:
        return "Aucun rapport disponible"

# Layout de l'application avec deux onglets et un style moderne et centré
app.layout = html.Div(style={
    "textAlign": "center",
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#f2f2f2",
    "padding": "20px"
}, children=[
    dcc.Tabs(id="tabs", value="tab-presentation", children=[
        dcc.Tab(label="Présentation", value="tab-presentation", style={"padding": "10px"}, selected_style={"backgroundColor": "#d9d9d9"}),
        dcc.Tab(label="Dashboard", value="tab-dashboard", style={"padding": "10px"}, selected_style={"backgroundColor": "#d9d9d9"})
    ]),
    html.Div(id="tabs-content"),
    dcc.Interval(id="interval-component", interval=300000, n_intervals=0)  # actualisation toutes les 5 minutes
])

# Callback pour mettre à jour le contenu selon l'onglet sélectionné et l'intervalle
@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"), Input("interval-component", "n_intervals")]
)
def render_content(tab, n):
    if tab == "tab-presentation":
        return html.Div([
            html.H1("Présentation du Projet"),
            html.P("Ce projet a pour objectif de scraper en continu le cours de la crypto XRP depuis Cryptoast, "
                   "de générer un rapport journalier détaillé, et de permettre un suivi en temps réel via ce dashboard."),
            html.P("L'onglet 'Dashboard' affiche le prix actualisé, un graphique d'évolution, ainsi que le rapport journalier.")
        ], style={"padding": "20px"})
    
    elif tab == "tab-dashboard":
        df = load_data()
        if not df.empty:
            last_row = df.iloc[-1]
            current_price = last_row["price"]
            last_update_str = last_row["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
        else:
            current_price = "N/D"
            last_update_str = "N/D"
        
        # Création du graphique d'évolution du prix
        graph = {
            "data": [go.Scatter(x=df["timestamp"], y=df["price"], mode="lines+markers", name="Prix XRP")] if not df.empty else [],
            "layout": go.Layout(
                title="Evolution du prix d'XRP",
                xaxis={"title": "Temps"},
                yaxis={"title": "Prix ($)"},
                paper_bgcolor="#f2f2f2",
                plot_bgcolor="#ffffff"
            )
        }
        
        daily_report = load_daily_report()
        
        return html.Div([
            html.H1("Dashboard"),
            html.Div([
                html.H3(f"Prix actualisé : {current_price} $"),
                html.P(f"Dernière mise à jour : {last_update_str}")
            ], style={"marginBottom": "20px", "fontSize": "18px"}),
            dcc.Graph(figure=graph),
            html.H3("Rapport journalier"),
            html.Pre(daily_report, style={
                "backgroundColor": "#e6e6e6",
                "padding": "15px",
                "borderRadius": "5px",
                "textAlign": "left",
                "display": "inline-block",
                "maxWidth": "800px"
            })
        ], style={"padding": "20px"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
message.txt
5 Ko
