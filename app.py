import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
from datetime import datetime

app = dash.Dash(__name__)
server = app.server  # Utile pour le déploiement

def load_data():
    """
    Charge les données depuis data.txt (timestamp, price)
    Format : YYYY-MM-DD HH:MM:SS,$prix
    """
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

def compute_daily_ohlc(df):
    """
    Regroupe les données par jour pour calculer un open, high, low, close par date,
    et la moyenne du jour.
    Retourne un DataFrame avec columns = [date, open, high, low, close, mean].
    """
    if df.empty:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "mean"])
    
    df["date"] = df["timestamp"].dt.date  # Extraire la date
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

def compute_rolling_mean(daily, window=10):
    """
    Calcule la moyenne mobile sur 'window' jours sur la base du 'close' journalier.
    Ajoute une colonne 'rolling_mean' au DataFrame daily.
    """
    daily["rolling_mean"] = daily["close"].rolling(window=window).mean()
    return daily

def load_daily_report():
    """
    Charge le rapport journalier depuis daily_report.txt
    """
    if os.path.exists("daily_report.txt"):
        with open("daily_report.txt", "r") as f:
            return f.read()
    else:
        return "Aucun rapport disponible"

app.layout = html.Div(style={
    "textAlign": "center",
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#f2f2f2",
    "padding": "20px"
}, children=[
    html.H1("Dashboard XRP Avancé"),
    
    dcc.Tabs(id="tabs", value="tab-overview", children=[
        dcc.Tab(label="Présentation", value="tab-overview", style={"padding": "10px"}, 
                selected_style={"backgroundColor": "#d9d9d9"}),
        dcc.Tab(label="Dashboard", value="tab-dashboard", style={"padding": "10px"}, 
                selected_style={"backgroundColor": "#d9d9d9"})
    ]),
    
    html.Div(id="tabs-content"),

    dcc.Interval(id="interval-component", interval=300000, n_intervals=0)  # actualisation toutes les 5 minutes
])

@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"),
     Input("interval-component", "n_intervals")]
)
def render_content(tab, n):
    df = load_data()
    daily = compute_daily_ohlc(df)  # DataFrame avec columns=[date, open, high, low, close, mean]
    daily = compute_rolling_mean(daily, window=10)  # Ajout de la colonne rolling_mean
    
    if tab == "tab-overview":
        return html.Div([
            html.H2("Présentation du Projet"),
            html.P("Ce projet scrappe en continu le cours de la crypto XRP depuis crypto.com, "
                   "génère un rapport journalier et propose un dashboard avancé."),
            html.P("Le dashboard affiche un graphique principal avec la courbe du prix, une moyenne mobile sur 10 jours, "
                   "et une ligne pointillée représentant la moyenne du jour. Un second graphique en chandeliers (candlesticks) "
                   "présente les données open/high/low/close agrégées par jour. Enfin, un tableau récapitule les stats journalières.")
        ], style={"padding": "20px"})
    
    elif tab == "tab-dashboard":
        if df.empty:
            return html.Div([
                html.H2("Aucune donnée disponible"),
                html.P("Exécutez le script de scraping pour générer des données.")
            ])
        
        # ----- GRAPH 1 : Prix + moyenne mobile + ligne pointillée moyenne du jour -----
        # On utilise daily pour la moyenne mobile, 
        # On utilise df pour la courbe de prix détaillée,
        # On ajoute une ligne horizontale pointillée représentant la moyenne du jour (si on est sur la dernière date).
        
        # Graph 1 traces
        trace_price = go.Scatter(
            x=df["timestamp"],
            y=df["price"],
            mode="lines+markers",
            name="Prix (détaillé)",
            line=dict(color="blue")
        )
        
        # On superpose la rolling_mean sur la base daily
        trace_ma = go.Scatter(
            x=daily["date"],
            y=daily["rolling_mean"],
            mode="lines",
            name="Moyenne mobile 10j",
            line=dict(color="orange", dash="dash")
        )
        
        # Ligne pointillée pour la moyenne du jour (dernière date)
        if not daily.empty:
            last_date = daily["date"].iloc[-1]
            last_mean = daily["mean"].iloc[-1]
        else:
            last_date = None
            last_mean = None
        
        if last_date is not None:
            trace_daily_mean = go.Scatter(
                x=[last_date, last_date],
                y=[last_mean, last_mean],
                mode="lines",
                name=f"Moyenne du {last_date}",
                line=dict(color="red", dash="dot")
            )
        else:
            trace_daily_mean = go.Scatter(x=[], y=[])
        
        layout1 = go.Layout(
            title="Prix XRP + Moyenne Mobile 10 jours + Moyenne du jour",
            xaxis={"title": "Date/Heure"},
            yaxis={"title": "Prix ($)"},
            paper_bgcolor="#f2f2f2",
            plot_bgcolor="#ffffff"
        )
        
        fig1 = go.Figure(data=[trace_price, trace_ma, trace_daily_mean], layout=layout1)
        
        # ----- GRAPH 2 : Candlestick -----
        # On utilise daily pour générer un candlestick
        # columns = [date, open, high, low, close, mean, rolling_mean]
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
                xaxis={"title": "Date"},
                yaxis={"title": "Prix ($)"},
                paper_bgcolor="#f2f2f2",
                plot_bgcolor="#ffffff"
            )
            fig2 = go.Figure(data=[candlestick], layout=layout2)
        else:
            # Si on n'a pas assez de données, on affiche un message
            fig2 = go.Figure()
            fig2.update_layout(
                title="Chandeliers Quotidiens (OHLC)",
                paper_bgcolor="#f2f2f2",
                plot_bgcolor="#ffffff"
            )
            fig2.add_annotation(
                text="Pas assez de données pour afficher le chandlier",
                showarrow=False
            )
        
        # ----- Tableau des données journalières -----
        # On affiche open, high, low, close, mean, rolling_mean
        # On convertit daily en un format plus lisible
        if not daily.empty:
            daily_table = daily[["date", "open", "high", "low", "close", "mean", "rolling_mean"]].copy()
            daily_table.columns = ["Date", "Open", "High", "Low", "Close", "Mean", "MA10"]
        else:
            daily_table = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Mean", "MA10"])
        
        # On crée un dash DataTable ou un simple HTML
        table_rows = []
        for _, row in daily_table.iterrows():
            table_rows.append(html.Tr([
                html.Td(str(row["Date"])),
                html.Td(f"{row['Open']:.4f}"),
                html.Td(f"{row['High']:.4f}"),
                html.Td(f"{row['Low']:.4f}"),
                html.Td(f"{row['Close']:.4f}"),
                html.Td(f"{row['Mean']:.4f}"),
                html.Td(f"{row['MA10']:.4f}" if not pd.isna(row["MA10"]) else "N/A")
            ]))
        
        table_header = html.Tr([
            html.Th("Date"), html.Th("Open"), html.Th("High"), html.Th("Low"),
            html.Th("Close"), html.Th("Mean"), html.Th("MA10")
        ])
        
        daily_table_html = html.Table([
            html.Thead(table_header),
            html.Tbody(table_rows)
        ], style={"margin": "auto", "border": "1px solid #ccc"})
        
        # ----- Rapport Journalier -----
        daily_report = load_daily_report()
        
        return html.Div([
            # Graph 1
            dcc.Graph(figure=fig1, style={"marginBottom": "40px"}),
            
            # Graph 2
            dcc.Graph(figure=fig2, style={"marginBottom": "40px"}),
            
            # Tableau
            html.H3("Tableau des données journalières"),
            daily_table_html,
            
            # Rapport Journalier
            html.H3("Rapport Journalier"),
            html.Pre(daily_report, style={
                "backgroundColor": "#e6e6e6",
                "padding": "15px",
                "borderRadius": "5px",
                "textAlign": "left",
                "display": "inline-block",
                "maxWidth": "800px",
                "marginTop": "20px"
            })
        ], style={"padding": "20px"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
