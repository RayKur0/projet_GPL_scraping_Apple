import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import os
from datetime import datetime, timedelta
import re

app = dash.Dash(__name__)
server = app.server

BACKGROUND_COLOR = "#1e1e2f"
TEXT_COLOR = "#f0f0f5"
PLOT_BG = "#2e2e42"
ACCENT_COLOR = "#00d1b2"
DANGER_COLOR = "#ff3860"
GRID_COLOR = "#444"


def load_data_from_log():
    """
    Lit cron_scrape.log et extrait:
    [YYYY-MM-DD HH:MM:SS] Prix XRP: $<prix>
    """
    log_path = "/home/ec2-user/projet_GPL_scraping_Apple/cron_scrape.log"
    if not os.path.exists(log_path):
        return pd.DataFrame(columns=["timestamp", "price"])

    data = []
    pattern = re.compile(r'\[(.*?)\]\s+Prix XRP:\s+\$(\d+(?:[.,]\d+)?)')
    with open(log_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                ts_str = match.group(1)
                price_str = match.group(2).replace(',', '.')
                try:
                    ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                    price = float(price_str)
                    data.append((ts, price))
                except:
                    pass
    df = pd.DataFrame(data, columns=["timestamp", "price"])
    if not df.empty:
        df.sort_values("timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df

def compute_daily_ohlc(df):
    """
    Agrège df en daily (open, high, low, close, mean).
    """
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

def compute_rolling_mean(daily, window=10):
    """
    Calcule la MA10 sur la colonne close.
    """
    daily["rolling_mean"] = daily["close"].rolling(window=window).mean()
    return daily

def compute_rsi(df, period=14):
    """
    Calcule RSI sur la colonne price, sur 'period' points.
    """
    if df.empty or len(df) < period:
        df["rsi"] = None
        return df

    df = df.copy()
    df["change"] = df["price"].diff(1)
    df["gain"] = df["change"].apply(lambda x: x if x > 0 else 0)
    df["loss"] = df["change"].apply(lambda x: -x if x < 0 else 0)
    df["avg_gain"] = df["gain"].rolling(period).mean()
    df["avg_loss"] = df["loss"].rolling(period).mean()
    df["avg_loss"].replace(0, 0.0000001, inplace=True)
    rs = df["avg_gain"] / df["avg_loss"]
    df["rsi"] = 100 - (100 / (1 + rs))
    return df

def load_daily_report():
    """
    Lit daily_report.txt (rapport journalier).
    """
    report_path = "/home/ec2-user/projet_GPL_scraping_Apple/daily_report.txt"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            return f.read()
    return "Aucun rapport disponible"

def load_data():
    """
    Charge df depuis cron_scrape.log, calcule RSI.
    """
    df = load_data_from_log()
    df = compute_rsi(df, period=14)
    return df


app.layout = html.Div(style={
    "textAlign": "center",
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": BACKGROUND_COLOR,
    "color": TEXT_COLOR,
    "padding": "20px"
}, children=[
    html.H1("Dashboard XRP", style={"color": ACCENT_COLOR, "marginBottom": "30px"}),

    # Dropdown: période (1D, 3D, 7D)
    html.Div([
        html.Label("Période :", style={"marginRight": "10px", "fontSize": "16px"}),
        dcc.Dropdown(
            id="period-dropdown",
            options=[
                {"label": "1 Jour", "value": "1D"},
                {"label": "3 Jours", "value": "3D"},
                {"label": "1 Semaine", "value": "7D"}
            ],
            value="1D",
            clearable=False,
            style={"width": "200px", "color": "#000"}
        )
    ], style={"display": "inline-block", "marginBottom": "30px"}),

    dcc.Tabs(id="tabs", value="tab-dashboard", children=[
        dcc.Tab(label="Présentation", value="tab-overview",
                style={"padding": "10px", "backgroundColor": PLOT_BG},
                selected_style={"backgroundColor": PLOT_BG, "borderBottom": f"3px solid {ACCENT_COLOR}"}),
        dcc.Tab(label="Dashboard", value="tab-dashboard",
                style={"padding": "10px", "backgroundColor": PLOT_BG},
                selected_style={"backgroundColor": PLOT_BG, "borderBottom": f"3px solid {ACCENT_COLOR}"})
    ], style={"marginTop": "20px"}),

    html.Div(id="tabs-content", style={"marginTop": "20px"}),

    dcc.Interval(id="interval-component", interval=300000, n_intervals=0)
])

@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"),
     Input("period-dropdown", "value"),
     Input("interval-component", "n_intervals")]
)
def render_content(tab, period, n):
    df = load_data()
    if df.empty:
        daily = pd.DataFrame(columns=["date", "open", "high", "low", "close", "mean", "rolling_mean"])
    else:
        daily = compute_daily_ohlc(df)
        daily = compute_rolling_mean(daily, window=10)

    if tab == "tab-overview":
        return html.Div([
            html.H2("Présentation du Projet", style={"color": ACCENT_COLOR}),
            html.P(
                "Ce projet scrappe en continu le cours de la crypto XRP depuis crypto.com, "
                "génère un rapport journalier, et permet un suivi via ce dashboard.",
                style={"fontSize": "18px"}
            ),
            html.P(
                "Le dashboard affiche : un graphique linéaire (prix + MA10 + moyenne journalière), "
                "un graphique en bougie (candlestick) sur la période, un graphique bougie agrégé daily, un RSI, "
                "un tableau agrégé (OHLC) et un rapport journalier.",
                style={"fontSize": "16px"}
            )
        ], style={"padding": "20px"})

    else:
        if df.empty:
            return html.Div([
                html.H2("Aucune donnée disponible", style={"color": DANGER_COLOR}),
                html.P("Exécutez le script de scraping pour générer des données.", style={"fontSize": "18px"})
            ])

        now = datetime.now()
        if period == "1D":
            start_time = now - timedelta(days=1)
        elif period == "3D":
            start_time = now - timedelta(days=3)
        elif period == "7D":
            start_time = now - timedelta(days=7)
        else:
            start_time = df["timestamp"].min()

        df_filtered = df[df["timestamp"] >= start_time].copy()

        # 1) Graphique 1 (linéaire)
        trace_price = go.Scatter(
            x=df_filtered["timestamp"],
            y=df_filtered["price"],
            mode="lines+markers",
            name="Prix en temps réel",
            line=dict(color=ACCENT_COLOR, width=2)
        )
        if not daily.empty:
            last_day = daily.iloc[-1]
            trace_ma = go.Scatter(
                x=daily["date"],
                y=daily["rolling_mean"],
                mode="lines",
                name="MA10 (Close)",
                line=dict(color="#ffdd57", dash="dash", width=2)
            )
            trace_daily_mean = go.Scatter(
                x=[last_day["date"], last_day["date"]],
                y=[last_day["mean"], last_day["mean"]],
                mode="lines",
                name=f"Moyenne du jour ({last_day['date']})",
                line=dict(color=DANGER_COLOR, dash="dot", width=2)
            )
            data_fig1 = [trace_price, trace_ma, trace_daily_mean]
        else:
            data_fig1 = [trace_price]

        layout1 = go.Layout(
            title=f"Graphique Linéaire (filtré sur {period}) + MA10 + Moyenne Journalière",
            xaxis=dict(title="Date/Heure", gridcolor=GRID_COLOR),
            yaxis=dict(title="Prix ($)", gridcolor=GRID_COLOR),
            paper_bgcolor=BACKGROUND_COLOR,
            plot_bgcolor=PLOT_BG,
            font=dict(color=TEXT_COLOR)
        )
        fig1 = go.Figure(data=data_fig1, layout=layout1)

        # 2) Graphique bougie sur la période
        if len(df_filtered) > 1:
            df_filtered["datehour"] = df_filtered["timestamp"].dt.floor("H")  # arrondi à l'heure
            groupedH = df_filtered.groupby("datehour")["price"]
            df_candle = pd.DataFrame({
                "open": groupedH.first(),
                "high": groupedH.max(),
                "low": groupedH.min(),
                "close": groupedH.last()
            })
            df_candle.reset_index(inplace=True)

            candlestick_period = go.Candlestick(
                x=df_candle["datehour"],
                open=df_candle["open"],
                high=df_candle["high"],
                low=df_candle["low"],
                close=df_candle["close"],
                name="Bougie (filtré)"
            )
            layout2 = go.Layout(
                title=f"Bougie sur la période {period}",
                xaxis=dict(title="Date/Heure", gridcolor=GRID_COLOR),
                yaxis=dict(title="Prix ($)", gridcolor=GRID_COLOR),
                paper_bgcolor=BACKGROUND_COLOR,
                plot_bgcolor=PLOT_BG,
                font=dict(color=TEXT_COLOR)
            )
            fig2 = go.Figure(data=[candlestick_period], layout=layout2)
        else:
            fig2 = go.Figure()
            fig2.update_layout(
                title=f"Bougie sur la période {period}",
                paper_bgcolor=BACKGROUND_COLOR,
                plot_bgcolor=PLOT_BG,
                font=dict(color=TEXT_COLOR)
            )
            fig2.add_annotation(
                text="Pas assez de points pour afficher un candlestick",
                showarrow=False,
                font=dict(color=DANGER_COLOR)
            )

        # 3) Bougie daily (agrégation journalière)
        if len(daily) > 1:
            candlestick_daily = go.Candlestick(
                x=daily["date"],
                open=daily["open"],
                high=daily["high"],
                low=daily["low"],
                close=daily["close"],
                name="Bougie (Daily)"
            )
            layout3 = go.Layout(
                title="Bougie (Daily) - Agrégation Journalière",
                xaxis=dict(title="Date", gridcolor=GRID_COLOR),
                yaxis=dict(title="Prix ($)", gridcolor=GRID_COLOR),
                paper_bgcolor=BACKGROUND_COLOR,
                plot_bgcolor=PLOT_BG,
                font=dict(color=TEXT_COLOR)
            )
            fig3 = go.Figure(data=[candlestick_daily], layout=layout3)
        else:
            fig3 = go.Figure()
            fig3.update_layout(
                title="Bougie (Daily)",
                paper_bgcolor=BACKGROUND_COLOR,
                plot_bgcolor=PLOT_BG,
                font=dict(color=TEXT_COLOR)
            )
            fig3.add_annotation(
                text="Pas assez de données daily",
                showarrow=False,
                font=dict(color=DANGER_COLOR)
            )

        # 4) Graphique RSI
        if "rsi" in df_filtered.columns and not df_filtered["rsi"].isnull().all():
            trace_rsi = go.Scatter(
                x=df_filtered["timestamp"], y=df_filtered["rsi"],
                mode="lines", name="RSI (14)",
                line=dict(color="#ffdd57", width=2)
            )
            line_rsi_30 = go.Scatter(
                x=[df_filtered["timestamp"].min(), df_filtered["timestamp"].max()],
                y=[30, 30], mode="lines",
                name="RSI 30",
                line=dict(color=DANGER_COLOR, dash="dot", width=1)
            )
            line_rsi_70 = go.Scatter(
                x=[df_filtered["timestamp"].min(), df_filtered["timestamp"].max()],
                y=[70, 70], mode="lines",
                name="RSI 70",
                line=dict(color=ACCENT_COLOR, dash="dot", width=1)
            )
            layout4 = go.Layout(
                title="RSI (14)",
                xaxis=dict(title="Date/Heure", gridcolor=GRID_COLOR),
                yaxis=dict(title="RSI", range=[0, 100], gridcolor=GRID_COLOR),
                paper_bgcolor=BACKGROUND_COLOR,
                plot_bgcolor=PLOT_BG,
                font=dict(color=TEXT_COLOR)
            )
            fig4 = go.Figure(data=[trace_rsi, line_rsi_30, line_rsi_70], layout=layout4)
        else:
            fig4 = go.Figure()
            fig4.update_layout(
                title="RSI (14)",
                paper_bgcolor=BACKGROUND_COLOR,
                plot_bgcolor=PLOT_BG,
                font=dict(color=TEXT_COLOR)
            )
            fig4.add_annotation(
                text="Pas assez de données pour RSI",
                showarrow=False,
                font=dict(color=DANGER_COLOR)
            )

        # Tableau agrégé (OHLC)
        if not daily.empty:
            daily_table = daily[["date", "open", "high", "low", "close", "mean", "rolling_mean"]].copy()
            daily_table.columns = ["Date", "Open", "High", "Low", "Close", "Mean", "MA10"]
        else:
            daily_table = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Mean", "MA10"])

        table_rows = []
        for _, row in daily_table.iterrows():
            table_rows.append(html.Tr([
                html.Td(str(row["Date"]), style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
                html.Td(f"{row['Open']:.4f}", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
                html.Td(f"{row['High']:.4f}", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
                html.Td(f"{row['Low']:.4f}", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
                html.Td(f"{row['Close']:.4f}", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
                html.Td(f"{row['Mean']:.4f}", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
                html.Td(f"{row['MA10']:.4f}" if pd.notna(row["MA10"]) else "N/A",
                        style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"})
            ]))

        table_header = html.Tr([
            html.Th("Date", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
            html.Th("Open", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
            html.Th("High", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
            html.Th("Low", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
            html.Th("Close", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
            html.Th("Mean", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"}),
            html.Th("MA10", style={"padding": "8px", "border": f"1px solid {GRID_COLOR}"})
        ])
        daily_table_html = html.Table([
            html.Thead(table_header),
            html.Tbody(table_rows)
        ], style={"borderCollapse": "collapse", "marginBottom": "40px"})

        # Rapport Journalier
        daily_report = load_daily_report()

        # Container flex : rapport left, tableau right
        container_style = {
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "flex-start",
            "gap": "50px",
            "marginTop": "30px"
        }
        left_style = {
            "flex": "0 0 auto",
            "border": f"1px solid {GRID_COLOR}",
            "borderRadius": "5px",
            "backgroundColor": PLOT_BG,
            "padding": "15px",
            "maxWidth": "300px"
        }
        right_style = {
            "flex": "0 0 auto",
            "textAlign": "center"
        }

        left_div = html.Div([
            html.H3("Rapport Journalier", style={"color": ACCENT_COLOR, "marginBottom": "20px"}),
            html.Pre(daily_report, style={
                "backgroundColor": BACKGROUND_COLOR,
                "padding": "15px",
                "borderRadius": "5px",
                "color": TEXT_COLOR,
                "whiteSpace": "pre-wrap"
            })
        ], style=left_style)

        right_div = html.Div([
            html.H3("Tableau agrégé par jour (OHLC)", style={"color": ACCENT_COLOR, "marginBottom": "20px"}),
            daily_table_html
        ], style=right_style)

        return html.Div([
            # Graph 1 : linéaire
            dcc.Graph(figure=fig1, style={"marginBottom": "40px"}),

            # Graph 2 : bougie sur la période
            dcc.Graph(figure=fig2, style={"marginBottom": "40px"}),

            # Graph 3 : bougie daily
            dcc.Graph(figure=fig3, style={"marginBottom": "40px"}),

            # Graph 4 : RSI
            dcc.Graph(figure=fig4, style={"marginBottom": "40px"}),

            # Container flex (rapport à gauche, tableau à droite)
            html.Div([left_div, right_div], style=container_style)

        ], style={"padding": "20px"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
