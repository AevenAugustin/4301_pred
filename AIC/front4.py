import dash
from dash import dcc, html
import plotly.express as px
from forecast.forecast import prepare_forecast  # Importer la fonction depuis le module forecast

# Chemin relatif vers le fichier CSV (placé à la racine du projet)
file_path = "data_merged_sansprévisions.csv"

# Charger et préparer les données
df_forecast = prepare_forecast(file_path)

# Créer l'application Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Prévision de Consommation Électrique"),
    
    # Sélecteur de dates pour filtrer l'affichage
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=df_forecast['DateTime'].min().date(),
        end_date=df_forecast['DateTime'].max().date(),
        display_format='DD/MM/YYYY',
        style={'margin-bottom': '20px'}
    ),
    
    # Graphique interactif affichant la consommation réelle et la prévision
    dcc.Graph(
        id='graphique',
        figure=px.line(
            df_forecast,
            x="DateTime",
            y=["Consommation", "Forecast"],
            markers=True,
            title="Consommation Réelle et Prévision"
        )
    )
])

@app.callback(
    dash.dependencies.Output('graphique', 'figure'),
    [dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date')]
)
def update_graph(start_date, end_date):
    df_filtered = df_forecast[(df_forecast['DateTime'] >= start_date) & (df_forecast['DateTime'] <= end_date)]
    fig = px.line(
        df_filtered,
        x="DateTime",
        y=["Consommation", "Forecast"],
        markers=True,
        title="Consommation Réelle et Prévision"
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
