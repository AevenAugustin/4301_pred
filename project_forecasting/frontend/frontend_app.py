import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os
import requests

# Chemin local vers le CSV (données originales)
file_path = r"C:\Users\brice\esiee\project_forecasting\backend\data\data_merged.csv"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")

df = pd.read_csv(file_path, delimiter=';')

required_columns = {"Jour", "Heures", "PrévisionJ-1", "PrévisionJ", "Consommation"}
if not required_columns.issubset(df.columns):
    raise ValueError(f"Colonnes manquantes dans le CSV. Attendu: {required_columns}. Trouvé: {df.columns}")

df['Jour'] = pd.to_datetime(df['Jour'], format='%d/%m/%Y', errors='coerce')
df['DateTime'] = pd.to_datetime(df['Jour'].astype(str) + ' ' + df['Heures'].astype(str), format='%Y-%m-%d %H:%M', errors='coerce')
df.sort_values('DateTime', inplace=True)


df_daily = df.resample('D', on='DateTime').sum(numeric_only=True).reset_index()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Comparaison Réel vs Prévisions (Agrégation Quotidienne)"),
    
    dcc.Checklist(
        id='evaluation-mode',
        options=[{'label': 'Mode évaluation (train/test 80/20)', 'value': 'eval'}],
        value=['eval'],  
        style={'margin-bottom': '20px'}
    ),
    
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=df_daily['DateTime'].min().date(),
        end_date=df_daily['DateTime'].max().date(),
        display_format='DD/MM/YYYY',
        style={'margin-bottom': '20px'}
    ),
    
    dcc.Graph(id='graphique')
])

@app.callback(
    Output('graphique', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('evaluation-mode', 'value')]
)
def update_graph(start_date, end_date, eval_mode):
    if 'eval' in eval_mode:
        # Mode évaluation : utilisation des données test (20% des dernières données)
        n = len(df_daily)
        train_size = int(n * 0.8)
        test_df = df_daily.iloc[train_size:]
        real_data = test_df
    else:
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        real_data = df_daily[(df_daily['DateTime'] >= start_dt) & (df_daily['DateTime'] <= end_dt)]
    
    fig = px.line(
        real_data,
        x="DateTime",
        y=["PrévisionJ-1", "PrévisionJ", "Consommation"],
        markers=True,
        title="Données Réelles Agrégées (quotidiennes)"
    )
    
    # Appel à l'API backend pour récupérer les prévisions journalières
    if 'eval' in eval_mode:
        params = {"test_mode": "true"}
    else:
        params = {"start_date": str(start_date), "end_date": str(end_date)}
    
    response = requests.get("http://localhost:5000/forecast", params=params)
    if response.status_code == 200:
        forecast_data = pd.read_json(response.text, orient='records')
        if not forecast_data.empty:
            forecast_data['DateTime'] = pd.to_datetime(forecast_data['DateTime'], errors='coerce')
            fig.add_scatter(
                x=forecast_data['DateTime'],
                y=forecast_data['Forecast'],
                mode='lines+markers',
                name='Prévisions',
                line=dict(dash='dash')
            )
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)
