import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
from datetime import datetime

app = dash.Dash(__name__)
server = app.server  # Pour le déploiement

# Fonction pour charger les données depuis data.txt
def load_data():
    if not os.path.exists("data.txt"):
        return pd.DataFrame(columns=["timestamp", "price"])
    try:
        df = pd.read_csv("data.txt", names=["timestamp", "price"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = df['price'].str.replace('$','', regex=False).astype(float)
        df.sort_values("timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except:
        return pd.DataFrame(columns=["timestamp", "price"])

# Fonction pour charger le rapport journalier depuis daily_report.txt
def load_daily_report():
    if os.path.exists("daily_report.txt"):
        with open("daily_report.txt", "r") as f:
            return f.read()
    else:
        return "Aucun rapport disponible"

# Fonction pour calculer l'agrégation journalière (OHLC et moyenne)
def compute_daily_ohlc(df):
    if df.empty:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "mean"])
    df["date"] = df["timestamp"].dt.date
    grouped = df.groupby("date")["price"]
    daily = pd.DataFrame({
        "open": grouped.first(),
        "high": grouped.max(),
        "low": grouped.min(),
        "close": grouped.last(),
        "mean": grouped.mean()
    })
    daily.reset_index(inplace=True)
    return daily

# Calcul de la moyenne mobile sur 10 jours (rolling mean)
def compute_rolling_mean(daily, window=10):
    daily["rolling_mean"] = daily["close"].rolling(window=window).mean()
    return daily

# Charger et préparer les données journalières
def prepare_daily_data():
    df = load_data()
    daily = compute_daily_ohlc(df)
    daily = compute_rolling_mean(daily, window=10)
    return df, daily

# Définition du style global pour un affichage moderne
global_style = {
    "textAlign": "center",
    "fontFamily": "'Roboto', sans-serif",
    "backgroundColor": "#1e1e2f",
    "color": "#f0f0f5",
    "padding": "20px"
}

tab_style = {
    "padding": "10px",
    "backgroundColor": "#2e2e42",
    "border": "none",
    "outline": "none",
    "cursor": "pointer"
}
tab_selected_style = {
    "padding": "10px",
    "backgroundColor": "#3a3a57",
    "borderBottom": "3px solid #00d1b2",
    "fontWeight": "bold"
}

# Layout de l'application avec deux onglets
app.layout = html.Div(style=global_style, children=[
    html.H1("Dashboard XRP Avancé", style={"marginBottom": "30px", "color": "#00d1b2"}),
    dcc.Tabs(id="tabs", value="tab-overview", children=[
        dcc.Tab(label="Présentation", value="tab-overview", style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label="Dashboard", value="tab-dashboard", style=tab_style, selected_style=tab_selected_style)
    ], style={"marginBottom": "30px"}),
    html.Div(id="tabs-content"),
    dcc.Interval(id="interval-component", interval=300000, n_intervals=0)  # Actualisation toutes les 5 minutes
])

@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"),
     Input("interval-component", "n_intervals")]
)
def render_content(tab, n):
    df, daily = prepare_daily_data()
    
    if tab == "tab-overview":
        return html.Div([
            html.H2("Présentation du Projet", style={"color": "#00d1b2"}),
            html.P("Ce projet scrappe en continu le cours de la crypto XRP depuis crypto.com, génère un rapport journalier détaillé, et permet un suivi en temps réel via ce dashboard.", style={"fontSize": "18px"}),
            html.P("Le dashboard inclut un graphique principal avec la courbe du prix, une moyenne mobile sur 10 jours affichée en ligne pointillée, ainsi qu'un graphique en chandeliers pour les données OHLC agrégées par jour.", style={"fontSize": "16px"})
        ], style={"padding": "20px"})
    
    elif tab == "tab-dashboard":
        if df.empty:
            return html.Div([
                html.H2("Aucune donnée disponible", style={"color": "#ff3860"}),
                html.P("Exécutez le script de scraping pour générer des données.", style={"fontSize": "18px"})
            ])
        
        # Graphique 1 : Prix détaillé, moyenne mobile sur 10 jours et ligne horizontale de la moyenne journalière (dernier jour)
        trace_price = go.Scatter(
            x=df["timestamp"],
            y=df["price"],
            mode="lines+markers",
            name="Prix en temps réel",
            line=dict(color="#00d1b2", width=2)
        )
        trace_ma = go.Scatter(
            x=daily["date"],
            y=daily["rolling_mean"],
            mode="lines",
            name="Moyenne mobile 10j",
            line=dict(color="#ffdd57", dash="dash", width=2)
        )
        if not daily.empty:
            last_day = daily.iloc[-1]
            trace_daily_mean = go.Scatter(
                x=[last_day["date"], last_day["date"]],
                y=[last_day["mean"], last_day["mean"]],
                mode="lines",
                name=f"Moyenne du jour ({last_day['date']})",
                line=dict(color="#ff3860", dash="dot", width=2)
            )
        else:
            trace_daily_mean = go.Scatter(x=[], y=[])
        
        layout1 = go.Layout(
            title="Prix XRP, Moyenne Mobile et Moyenne Journalière",
            xaxis=dict(title="Date/Heure", gridcolor="#444"),
            yaxis=dict(title="Prix ($)", gridcolor="#444"),
            paper_bgcolor="#1e1e2f",
            plot_bgcolor="#2e2e42",
            font=dict(color="#f0f0f5")
        )
        fig1 = go.Figure(data=[trace_price, trace_ma, trace_daily_mean], layout=layout1)
        
        # Graphique 2 : Candlestick pour les données OHLC journalières
        if len(daily) > 1:
            candlestick = go.Candlestick(
                x=daily["date"],
                open=daily["open"],
                high=daily["high"],
                low=daily["low"],
                close=daily["close"],
                name="OHLC Quotidien"
            )
            layout2 = go.Layout(
                title="Chandeliers Quotidiens (OHLC)",
                xaxis=dict(title="Date", gridcolor="#444"),
                yaxis=dict(title="Prix ($)", gridcolor="#444"),
                paper_bgcolor="#1e1e2f",
                plot_bgcolor="#2e2e42",
                font=dict(color="#f0f0f5")
            )
            fig2 = go.Figure(data=[candlestick], layout=layout2)
        else:
            fig2 = go.Figure()
            fig2.update_layout(
                title="Chandeliers Quotidiens (OHLC)",
                paper_bgcolor="#1e1e2f",
                plot_bgcolor="#2e2e42",
                font=dict(color="#f0f0f5")
            )
            fig2.add_annotation(
                text="Pas assez de données pour afficher le chandelier",
                showarrow=False,
                font=dict(color="#ff3860")
            )
        
        # Tableau des données journalières
        if not daily.empty:
            daily_table = daily[["date", "open", "high", "low", "close", "mean", "rolling_mean"]].copy()
            daily_table.columns = ["Date", "Open", "High", "Low", "Close", "Mean", "MA10"]
        else:
            daily_table = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Mean", "MA10"])
        
        table_rows = []
        for _, row in daily_table.iterrows():
            table_rows.append(html.Tr([
                html.Td(str(row["Date"]), style={"padding": "8px", "border": "1px solid #444"}),
                html.Td(f"{row['Open']:.4f}", style={"padding": "8px", "border": "1px solid #444"}),
                html.Td(f"{row['High']:.4f}", style={"padding": "8px", "border": "1px solid #444"}),
                html.Td(f"{row['Low']:.4f}", style={"padding": "8px", "border": "1px solid #444"}),
                html.Td(f"{row['Close']:.4f}", style={"padding": "8px", "border": "1px solid #444"}),
                html.Td(f"{row['Mean']:.4f}", style={"padding": "8px", "border": "1px solid #444"}),
                html.Td(f"{row['MA10']:.4f}" if not pd.isna(row["MA10"]) else "N/A", style={"padding": "8px", "border": "1px solid #444"})
            ]))
        
        table_header = html.Tr([
            html.Th("Date", style={"padding": "8px", "border": "1px solid #444"}),
            html.Th("Open", style={"padding": "8px", "border": "1px solid #444"}),
            html.Th("High", style={"padding": "8px", "border": "1px solid #444"}),
            html.Th("Low", style={"padding": "8px", "border": "1px solid #444"}),
            html.Th("Close", style={"padding": "8px", "border": "1px solid #444"}),
            html.Th("Mean", style={"padding": "8px", "border": "1px solid #444"}),
            html.Th("MA10", style={"padding": "8px", "border": "1px solid #444"})
        ])
        
        daily_table_html = html.Table([
            html.Thead(table_header),
            html.Tbody(table_rows)
        ], style={"margin": "auto", "borderCollapse": "collapse", "marginBottom": "40px"})
        
        daily_report = load_daily_report()
        
        return html.Div([
            dcc.Graph(figure=fig1, style={"marginBottom": "40px"}),
            dcc.Graph(figure=fig2, style={"marginBottom": "40px"}),
            html.H3("Tableau des données journalières", style={"color": "#00d1b2", "marginBottom": "20px"}),
            daily_table_html,
            html.H3("Rapport Journalier", style={"color": "#00d1b2"}),
            html.Pre(daily_report, style={
                "backgroundColor": "#2e2e42",
                "padding": "15px",
                "borderRadius": "5px",
                "textAlign": "left",
                "display": "inline-block",
                "maxWidth": "900px",
                "marginTop": "20px",
                "color": "#f0f0f5"
            })
        ], style={"padding": "20px"})
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
