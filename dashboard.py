import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objs as go
import pandas as pd
import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

DATA_FILE = "cac40_data.txt"

def load_data():
    try:
        # Charger les données en temps réel depuis cac40_data.txt
        df = pd.read_csv(DATA_FILE, names=['timestamp', 'prix', 'variation', 'cloture', 'ouverture', 'variation1an', 'volume', 'volumemoyen', 'ecartjour', 'ecart52', 'sentiment'])
    except Exception as e:
        print(f"Erreur de chargement des données : {e}")
        df = pd.DataFrame(columns=['timestamp', 'prix', 'variation', 'cloture', 'ouverture', 'variation1an', 'volume', 'volumemoyen', 'ecartjour', 'ecart52', 'sentiment'])

    # Convertir la colonne 'timestamp' en datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Trier par date
    df = df.sort_values('timestamp')

    return df

def calculate_daily_report(df):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    daily_data = df[df['timestamp'].dt.strftime('%Y-%m-%d') == today]
    
    if daily_data.empty:
        return {
            'open': 'N/A',
            'close': 'N/A',
            'volatility': 'N/A',
            'evolution': 'N/A'
        }
    
    # Filtrer les lignes où 'prix' est numérique
    daily_data = daily_data[pd.to_numeric(daily_data['prix'], errors='coerce').notna()]
    if daily_data.empty:
        return {
            'open': 'N/A',
            'close': 'N/A',
            'volatility': 'N/A',
            'evolution': 'N/A'
        }
    
    daily_data['prix'] = daily_data['prix'].astype(float)
    
    open_price = daily_data['prix'].iloc[0]
    close_price = daily_data['prix'].iloc[-1]
    volatility = daily_data['prix'].max() - daily_data['prix'].min()
    evolution = ((close_price - open_price) / open_price * 100) if open_price != 0 else 0
    
    return {
        'open': f"{open_price:.2f}",
        'close': f"{close_price:.2f}",
        'volatility': f"{volatility:.2f}",
        'evolution': f"{evolution:.2f}%"
    }

app.layout = html.Div([
    dbc.Container([
        html.H1("Dashboard CAC 40", className="text-center my-4"),
        dbc.Row([
            dbc.Col([
                html.H3("Valeur actuelle"),
                html.Div(id="live-prix", style={"fontSize": "24px", "fontWeight": "bold"})
            ], width=4),
            dbc.Col([
                html.H3("Variation"),
                html.Div(id="live-variation", style={"fontSize": "24px", "fontWeight": "bold"})
            ], width=4),
            dbc.Col([
                html.H3("Dernière mise à jour"),
                html.Div(id="live-timestamp", style={"fontSize": "24px", "fontWeight": "bold"})
            ], width=4),
        ]),
        dcc.Graph(id="live-graph"),
        html.Hr(),
        html.H2("Rapport quotidien (mis à jour à 20h)", className="text-center"),
        dbc.Row([
            dbc.Col([
                html.H4("Ouverture"),
                html.Div(id="daily-open", style={"fontSize": "20px"})
            ], width=3),
            dbc.Col([
                html.H4("Clôture"),
                html.Div(id="daily-close", style={"fontSize": "20px"})
            ], width=3),
            dbc.Col([
                html.H4("Volatilité"),
                html.Div(id="daily-volatility", style={"fontSize": "20px"})
            ], width=3),
            dbc.Col([
                html.H4("Évolution"),
                html.Div(id="daily-evolution", style={"fontSize": "20px"})
            ], width=3),
        ]),
        html.Hr(),
        html.H2("Autres données", className="text-center"),
        dbc.Row([
            dbc.Col([
                html.H4("Clôture précédente"),
                html.Div(id="live-cloture", style={"fontSize": "20px"})
            ], width=3),
            dbc.Col([
                html.H4("Ouverture"),
                html.Div(id="live-ouverture", style={"fontSize": "20px"})
            ], width=3),
            dbc.Col([
                html.H4("Variation sur 1 an"),
                html.Div(id="live-variation1an", style={"fontSize": "20px"})
            ], width=3),
            dbc.Col([
                html.H4("Volume"),
                html.Div(id="live-volume", style={"fontSize": "20px"})
            ], width=3),
        ]),
        dbc.Row([
            dbc.Col([
                html.H4("Volume moyen (3m)"),
                html.Div(id="live-volumemoyen", style={"fontSize": "20px"})
            ], width=3),
            dbc.Col([
                html.H4("Écart journalier"),
                html.Div(id="live-ecartjour", style={"fontSize": "20px"})
            ], width=3),
            dbc.Col([
                html.H4("Écart 52 sem."),
                html.Div(id="live-ecart52", style={"fontSize": "20px"})
            ], width=3),
            dbc.Col([
                html.H4("Sentiment technique"),
                html.Div(id="live-sentiment", style={"fontSize": "20px"})
            ], width=3),
        ]),
        dcc.Interval(id="interval-component", interval=5*60*1000, n_intervals=0)
    ])
])

@app.callback(
    [Output("live-prix", "children"),
     Output("live-variation", "children"),
     Output("live-timestamp", "children"),
     Output("live-graph", "figure"),
     Output("daily-open", "children"),
     Output("daily-close", "children"),
     Output("daily-volatility", "children"),
     Output("daily-evolution", "children"),
     Output("live-cloture", "children"),
     Output("live-ouverture", "children"),
     Output("live-variation1an", "children"),
     Output("live-volume", "children"),
     Output("live-volumemoyen", "children"),
     Output("live-ecartjour", "children"),
     Output("live-ecart52", "children"),
     Output("live-sentiment", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(n):
    df = load_data()
    
    if df.empty:
        return "N/A", "N/A", "N/A", {}, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
    
    last_row = df.iloc[-1]
    prix = last_row['prix']
    variation = last_row['variation']
    timestamp = last_row['timestamp']
    cloture = last_row.get('cloture', 'N/A')
    ouverture = last_row.get('ouverture', 'N/A')
    variation1an = last_row.get('variation1an', 'N/A')
    volume = last_row.get('volume', 'N/A')
    volumemoyen = last_row.get('volumemoyen', 'N/A')
    ecartjour = last_row.get('ecartjour', 'N/A')
    ecart52 = last_row.get('ecart52', 'N/A')
    sentiment = last_row.get('sentiment', 'N/A')
    
    # Filtrer les lignes où 'prix' est numérique
    df = df[pd.to_numeric(df['prix'], errors='coerce').notna()]
    
    # Si le DataFrame est vide après filtrage, retourner un graphique vide
    if df.empty:
        figure = {
            'data': [],
            'layout': go.Layout(
                title="Évolution du CAC 40 (Temps Réel)",
                xaxis={'title': 'Temps'},
                yaxis={'title': 'Valeur'},
                template="plotly_white"
            )
        }
    else:
        # Convertir 'prix' en float après filtrage
        df['prix'] = df['prix'].astype(float)
        figure = {
            'data': [
                go.Scatter(
                    x=df['timestamp'],
                    y=df['prix'],
                    mode='lines+markers',
                    name='CAC 40'
                )
            ],
            'layout': go.Layout(
                title="Évolution du CAC 40 (Temps Réel)",
                xaxis={'title': 'Temps'},
                yaxis={'title': 'Valeur'},
                template="plotly_white"
            )
        }
    
    # Calculer le rapport quotidien
    now = datetime.datetime.now()
    if now.hour >= 20:
        report = calculate_daily_report(df)
    else:
        report = {'open': 'En attente (20h)', 'close': 'En attente (20h)', 'volatility': 'En attente (20h)', 'evolution': 'En attente (20h)'}
    
    return (prix, variation, timestamp, figure,
            report['open'], report['close'], report['volatility'], report['evolution'],
            cloture, ouverture, variation1an, volume, volumemoyen, ecartjour, ecart52, sentiment)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)