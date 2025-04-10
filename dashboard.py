import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import datetime
import time
import subprocess  
import os  

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
DATA_FILE = "cac40_data.txt"

# Enregistrement du temps de démarrage pour le compte à rebours
start_time = int(time.time())
# Global pour mémoriser la dernière mise à jour (lorsque le compte à rebours atteint 0)
global_last_update = "N/A"
# Global pour stocker la dernière date de modification du fichier
last_file_mod_time = 0

def load_data():
    try:
        # Vérifier si le fichier existe et contient des données
        if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
            print(f"Le fichier {DATA_FILE} n'existe pas ou est vide")
            return pd.DataFrame(columns=[
                'timestamp', 'prix', 'variation', 'cloture', 'ouverture',
                'variation1an', 'volume', 'volumemoyen', 'ecartjour', 'ecart52', 'sentiment'
            ])
            
        # Debug: Afficher le contenu brut du fichier
        with open(DATA_FILE, 'r') as f:
            content = f.read()
            print("Contenu brut du fichier:")
            print(content[:500]) 
        
        df = pd.read_csv(
            DATA_FILE,
            sep=';',
            names=[
                'timestamp', 'prix', 'variation', 'cloture', 'ouverture',
                'variation1an', 'volume', 'volumemoyen', 'ecartjour', 'ecart52', 'sentiment'
            ],
            index_col=False
        )
        print("Données chargées :")
        print(df.head())
        
        # Debug: vérifier les types de colonnes
        print("Types de données:")
        print(df.dtypes)
        
    except Exception as e:
        print(f"Erreur de chargement des données : {e}")
        return pd.DataFrame(columns=[
            'timestamp', 'prix', 'variation', 'cloture', 'ouverture',
            'variation1an', 'volume', 'volumemoyen', 'ecartjour', 'ecart52', 'sentiment'
        ])
    
    # Conversion de la colonne timestamp en datetime
    df['timestamp'] = pd.to_datetime(
        df['timestamp'].str.strip(), 
        format='%Y-%m-%d %H:%M:%S', 
        errors='coerce'
    )
    
    # Conversion de la colonne prix :
    # Ajouter des logs pour le débogage
    print("Valeurs de prix avant conversion:")
    print(df['prix'].head())
    
    # S'assurer que prix est de type string avant d'appliquer des méthodes string
    df['prix'] = df['prix'].astype(str)
    df['prix'] = df['prix'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    
    print("Valeurs de prix après conversion des séparateurs:")
    print(df['prix'].head())
    
    df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
    
    print("Valeurs de prix après conversion numérique:")
    print(df['prix'].head())
    
    # Tri par date croissante
    df = df.sort_values('timestamp')
    return df

def check_file_updated():
    """Vérifie si le fichier de données a été mis à jour depuis la dernière lecture"""
    global last_file_mod_time
    try:
        current_mod_time = os.path.getmtime(DATA_FILE)
        if current_mod_time > last_file_mod_time:
            last_file_mod_time = current_mod_time
            return True
        return False
    except Exception as e:
        print(f"Erreur lors de la vérification du fichier: {e}")
        return False

def update_data_file():
    """Appelle le script de scraping pour mettre à jour le fichier de données"""
    try:
        print("Mise à jour des données CAC40...")
        result = subprocess.call(["bash", "scrape_cac40.sh"])
        return result == 0  # Retourne True si le script s'est exécuté avec succès
    except Exception as e:
        print(f"Erreur lors de l'appel au script de scraping: {e}")
        return False

def calculate_daily_report(df):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    daily_data = df[df['timestamp'].dt.strftime('%Y-%m-%d') == today]
    if daily_data.empty:
        return {'open': 'N/A', 'close': 'N/A', 'volatility': 'N/A', 'evolution': 'N/A'}
    daily_data = daily_data[pd.to_numeric(daily_data['prix'], errors='coerce').notna()]
    if daily_data.empty:
        return {'open': 'N/A', 'close': 'N/A', 'volatility': 'N/A', 'evolution': 'N/A'}
    daily_data['prix'] = daily_data['prix'].astype(float)
    open_price = daily_data['prix'].iloc[0]
    close_price = daily_data['prix'].iloc[-1]
    volatility = daily_data['prix'].max() - daily_data['prix'].min()
    evolution_pct = ((close_price - open_price) / open_price * 100) if open_price != 0 else 0
    return {
        'open': f"{open_price:.2f}",
        'close': f"{close_price:.2f}",
        'volatility': f"{volatility:.2f}",
        'evolution': f"{evolution_pct:.2f}%"
    }

def create_figure(df):
    # Filtrer uniquement les lignes avec un prix numérique
    df_filtered = df[pd.to_numeric(df['prix'], errors='coerce').notna()]
    if df_filtered.empty:
        fig = go.Figure()
    else:
        # Conversion du prix en float et tri par date pour garantir l'ordre
        df_filtered['prix'] = df_filtered['prix'].astype(float)
        df_filtered = df_filtered.sort_values('timestamp')
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=df_filtered['timestamp'],
                    y=df_filtered['prix'],
                    mode='markers+lines',  # Affichage des points et lignes de connexion
                    marker=dict(size=6),
                    line=dict(shape='linear', color='cyan'),
                    name='CAC 40'
                )
            ]
        )
    fig.update_layout(
        title={'text': "Évolution du CAC 40 (Temps Réel)", 'font': {'color': 'white'}},
        xaxis={
            'title': {'text': 'Date', 'font': {'color': 'white'}},
            'tickfont': {'color': 'white'},
            'gridcolor': 'gray',
            'tickformat': '%d/%m/%Y'
        },
        yaxis={
            'title': {'text': 'Valeur', 'font': {'color': 'white'}},
            'tickfont': {'color': 'white'},
            'gridcolor': 'gray'
        },
        paper_bgcolor='black',
        plot_bgcolor='black',
        font={'color': 'white'}
    )
    return fig

def style_percentage(value):
    try:
        # Remplacer la virgule par un point pour la conversion
        val_str = value.replace(',', '.')
        # Supprimer parenthèses et le signe %
        val_str = val_str.replace('(', '').replace(')', '').replace('%', '').strip()
        val_float = float(val_str)
        color = 'red' if val_float < 0 else 'green'
        display_value = f"{val_float:.2f}%"
    except:
        color = 'white'
        display_value = value
    return html.Span(display_value, style={"color": color})

# -- LAYOUT --

app.layout = html.Div([
    dbc.Container([
        # 1) Ligne de titre : Dashboard CAC 40 à gauche, heure à droite
        dbc.Row([
            dbc.Col(
                html.H1("Dashboard CAC 40", style={'color': 'white'}),
                md=8
            ),
            dbc.Col(
                html.Div(
                    html.Span(id="current-time", style={"fontSize": "20px"}),
                    style={"textAlign": "right", "color": "white", "marginTop": "10px"}
                ),
                md=4
            ),
        ], align="center"),
        
        # 2) Paragraphe explicatif
        html.Div([
            html.P(
                "Ce projet a été développé par LE et HEBRARD pour l'affichage en temps réel des valeurs du CAC 40. "
                "Il permet de visualiser l'évolution des indices boursiers, d'afficher les variations en temps réel et de fournir un rapport quotidien. "
                "L'application utilise Python, Dash, Plotly et Bootstrap pour offrir une interface esthétique et fonctionnelle, adaptée aux environnements Linux et Git.",
                style={'color': 'white', 'fontSize': '18px', 'textAlign': 'center', 'padding': '10px'}
            )
        ], style={"backgroundColor": "#333", "borderRadius": "8px", "marginTop": "10px"}),
        
        # 3) Section "Prochaine mise à jour"
        html.Div([
            html.H3("Prochaine mise à jour dans :", style={"fontWeight": "bold", "color": "white"}),
            html.Span(id="countdown", style={"fontSize": "22px", "fontWeight": "bold", "color": "white"})
        ], style={"textAlign": "center", "padding": "10px", "marginTop": "10px"}),
        
        # Bouton de mise à jour manuelle
        html.Div([
            html.Button("Mettre à jour maintenant", id="update-button", 
                        style={"backgroundColor": "#0077cc", "color": "white", 
                               "padding": "10px 20px", "border": "none", 
                               "borderRadius": "5px", "cursor": "pointer"}),
            html.Span(id="update-status", style={"marginLeft": "15px", "color": "white"})
        ], style={"textAlign": "center", "marginTop": "10px", "marginBottom": "10px"}),
        
        html.Hr(style={'borderColor': 'white'}),
        
        # 4) Contenu principal : Valeur actuelle, Variation et Dernière mise à jour
        dbc.Row([
            dbc.Col([
                html.H3("Valeur actuelle", style={'color': 'white'}),
                html.Div(id="live-prix", style={"fontSize": "24px", "fontWeight": "bold"})
            ], md=4),
            dbc.Col([
                html.H3("Variation", style={'color': 'white'}),
                html.Div(id="live-variation", style={"fontSize": "24px", "fontWeight": "bold"})
            ], md=4),
            dbc.Col([
                html.H3("Dernière mise à jour", style={'color': 'white'}),
                html.Div(id="live-timestamp", style={"fontSize": "24px", "fontWeight": "bold"})
            ], md=4),
        ]),
        
        dcc.Graph(id="live-graph"),
        html.Hr(style={'borderColor': 'white'}),
        
        # Rapport quotidien
        html.H2("Rapport quotidien (mis à jour à 20h)", className="text-center", style={'color': 'white'}),
        dbc.Row([
            dbc.Col([
                html.H4("Ouverture", style={'color': 'white'}),
                html.Div(id="daily-open", style={"fontSize": "20px"})
            ], md=3),
            dbc.Col([
                html.H4("Clôture", style={'color': 'white'}),
                html.Div(id="daily-close", style={"fontSize": "20px"})
            ], md=3),
            dbc.Col([
                html.H4("Volatilité", style={'color': 'white'}),
                html.Div(id="daily-volatility", style={"fontSize": "20px"})
            ], md=3),
            dbc.Col([
                html.H4("Évolution", style={'color': 'white'}),
                html.Div(id="daily-evolution", style={"fontSize": "20px"})
            ], md=3),
        ]),
        
        html.Hr(style={'borderColor': 'white'}),
        
        # Autres données
        html.H2("Autres données", className="text-center", style={'color': 'white'}),
        dbc.Row([
            dbc.Col([
                html.H4("Clôture précédente", style={'color': 'white'}),
                html.Div(id="live-cloture", style={"fontSize": "20px"})
            ], md=3),
            dbc.Col([
                html.H4("Ouverture", style={'color': 'white'}),
                html.Div(id="live-ouverture", style={"fontSize": "20px"})
            ], md=3),
            dbc.Col([
                html.H4("Variation sur 1 an", style={'color': 'white'}),
                html.Div(id="live-variation1an", style={"fontSize": "20px"})
            ], md=3),
            dbc.Col([
                html.H4("Volume", style={'color': 'white'}),
                html.Div(id="live-volume", style={"fontSize": "20px"})
            ], md=3),
        ]),
        dbc.Row([
            dbc.Col([
                html.H4("Volume moyen (3m)", style={'color': 'white'}),
                html.Div(id="live-volumemoyen", style={"fontSize": "20px"})
            ], md=3),
            dbc.Col([
                html.H4("Écart journalier", style={'color': 'white'}),
                html.Div(id="live-ecartjour", style={"fontSize": "20px"})
            ], md=3),
            dbc.Col([
                html.H4("Écart 52 sem.", style={'color': 'white'}),
                html.Div(id="live-ecart52", style={"fontSize": "20px"})
            ], md=3),
            dbc.Col([
                html.H4("Sentiment technique", style={'color': 'white'}),
                html.Div(id="live-sentiment", style={"fontSize": "20px"})
            ], md=3),
        ]),
        
        # Intervalles de mise à jour
        dcc.Interval(id="interval-component", interval=5*60*1000, n_intervals=0),
        dcc.Interval(id="interval-time", interval=1000, n_intervals=0),
        dcc.Interval(id="interval-countdown", interval=1000, n_intervals=0),
        
        # Status des mises à jour - pour stocker les résultats intermédiaires
        dcc.Store(id="file-check-store"),
    ], fluid=True)
], style={'backgroundColor': 'black', 'minHeight': '100vh', 'padding': '20px'})

# -- CALLBACKS --

@app.callback(
    Output("current-time", "children"),
    Input("interval-time", "n_intervals")
)
def update_current_time(n):
    """Met à jour l'heure (HH:MM:SS)."""
    return datetime.datetime.now().strftime("%H:%M:%S")

@app.callback(
    [Output("countdown", "children"),
     Output("file-check-store", "data")],
    [Input("interval-countdown", "n_intervals")]
)
def update_countdown(n):
    """
    Compte à rebours avant la prochaine mise à jour (5 minutes).
    Vérifie aussi si le fichier a été mis à jour entre temps.
    """
    now_sec = int(time.time())
    elapsed = now_sec - start_time
    time_left = (300 - (elapsed % 300)) % 300  # Temps restant pour atteindre 0
    minutes = time_left // 60
    seconds = time_left % 60
    
    # Vérifier si le fichier a été mis à jour
    file_updated = check_file_updated()
    
    return f"{minutes:02d}:{seconds:02d}", {"updated": file_updated}

@app.callback(
    Output("update-status", "children"),
    [Input("update-button", "n_clicks")],
    prevent_initial_call=True
)
def manual_update(n_clicks):
    """Gère la mise à jour manuelle des données en appelant le script bash"""
    if n_clicks:
        success = update_data_file()
        if success:
            return "Mise à jour réussie!"
        else:
            return "Échec de la mise à jour. Vérifiez les journaux."
    return ""

@app.callback(
    [
        Output("live-prix", "children"),
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
        Output("live-sentiment", "children")
    ],
    [Input("interval-component", "n_intervals"),
     Input("file-check-store", "data"),
     Input("update-status", "children")]
)
def update_dashboard(n_intervals, file_check_data, update_status):
    """
    Callback principal : se déclenche dans l'un de ces cas:
    1. Toutes les 5 minutes (interval-component)
    2. Quand le fichier de données est modifié (détecté par file-check-store)
    3. Après une mise à jour manuelle (update-status)
    """
    global global_last_update

    # Si c'est une mise à jour régulière et que le compte à rebours a atteint 0, appel du script bash
    now_sec = int(time.time())
    elapsed = now_sec - start_time
    time_left = (300 - (elapsed % 300)) % 300
    if time_left == 0:
        update_data_file()
        global_last_update = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Si le fichier a été mis à jour par un moyen externe, on met à jour le timestamp
    if file_check_data and file_check_data.get("updated", False):
        global_last_update = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Si mise à jour manuelle réussie, on met aussi à jour le timestamp
    if update_status == "Mise à jour réussie!":
        global_last_update = datetime.datetime.now().strftime("%H:%M:%S")

    df = load_data()
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            paper_bgcolor='black',
            plot_bgcolor='black',
            font={'color': 'white'}
        )
        return ("N/A", "N/A", "N/A", empty_fig,
                "N/A", "N/A", "N/A", "N/A",
                "N/A", "N/A", "N/A", "N/A",
                "N/A", "N/A", "N/A", "N/A")
    
    last_row = df.iloc[-1]
    # "Valeur actuelle" : donnée issue de 'prix'
    valeur_actuelle = str(last_row.get('prix', 'N/A'))
    # "Variation" : donnée issue de 'variation'
    variation_value = str(last_row.get('variation', 'N/A'))

    cloture = str(last_row.get('cloture', 'N/A'))
    ouverture = str(last_row.get('ouverture', 'N/A'))
    variation1an = str(last_row.get('variation1an', 'N/A'))
    volume = str(last_row.get('volume', 'N/A'))
    volumemoyen = str(last_row.get('volumemoyen', 'N/A'))
    ecartjour = str(last_row.get('ecartjour', 'N/A'))
    ecart52 = str(last_row.get('ecart52', 'N/A'))
    sentiment = str(last_row.get('sentiment', 'N/A'))

    fig = create_figure(df)
    now_dt = datetime.datetime.now()
    if now_dt.hour >= 20:
        report = calculate_daily_report(df)
    else:
        report = {
            'open': 'En attente (20h)', 
            'close': 'En attente (20h)', 
            'volatility': 'En attente (20h)', 
            'evolution': 'En attente (20h)'
        }
    
    daily_open = report['open']
    daily_close = report['close']
    daily_volatility = report['volatility']
    daily_evolution = report['evolution']

    styled_variation = style_percentage(variation_value)

    return (
        html.Span(valeur_actuelle, style={"color": "white"}),
        styled_variation,
        html.Span(global_last_update, style={"color": "white"}),
        fig,
        html.Span(daily_open, style={"color": "white"}),
        html.Span(daily_close, style={"color": "white"}),
        html.Span(daily_volatility, style={"color": "white"}),
        html.Span(daily_evolution, style={"color": "white"}),
        html.Span(cloture, style={"color": "white"}),
        html.Span(ouverture, style={"color": "white"}),
        html.Span(variation1an, style={"color": "white"}),
        html.Span(volume, style={"color": "white"}),
        html.Span(volumemoyen, style={"color": "white"}),
        html.Span(ecartjour, style={"color": "white"}),
        html.Span(ecart52, style={"color": "white"}),
        html.Span(sentiment, style={"color": "white"})
    )

if __name__ == "__main__":
    if os.path.exists(DATA_FILE):
        last_file_mod_time = os.path.getmtime(DATA_FILE)
    
    app.run(debug=True, host="0.0.0.0", port=8050)
