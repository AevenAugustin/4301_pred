import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import os

# 🔹 Chemin du fichier CSV
file_path = r"C:\Users\Victor\AIC_4301\data_merged.csv"  # Assure-toi du bon chemin

# 🔹 Vérifier si le fichier existe
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} est introuvable. Vérifie le chemin.")

# 🔹 Lire le fichier CSV avec pandas
try:
    df = pd.read_csv(file_path, delimiter=';')  # Utilisation du bon délimiteur
except Exception as e:
    raise ValueError(f"Erreur lors de la lecture du fichier : {e}")

# 🔹 Vérifier que les colonnes nécessaires sont présentes
required_columns = {"Jour", "Heures", "PrévisionJ-1", "PrévisionJ", "Consommation"}
if not required_columns.issubset(df.columns):
    raise ValueError(f"Le fichier doit contenir les colonnes {required_columns}. Colonnes trouvées : {df.columns}")

# 🔹 Convertir la colonne Jour en datetime
df['Jour'] = pd.to_datetime(df['Jour'], format='%d/%m/%Y')

# 🔹 Fusionner Jour et Heures en une seule colonne datetime
df['DateTime'] = df['Jour'].astype(str) + ' ' + df['Heures'].astype(str)
df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y-%m-%d %H:%M')

# 🔹 Création de l’application Dash
app = dash.Dash(__name__)

# 🔹 Layout de l'application
app.layout = html.Div(children=[
    html.H1("Visualisation des Prévisions de Consommation"),

    # 🔸 Sélecteur de date
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=df['DateTime'].min().date(),  # Date minimale du dataset
        end_date=df['DateTime'].max().date(),  # Date maximale du dataset
        display_format='DD/MM/YYYY',  # Format d'affichage des dates
        style={'margin-bottom': '20px'}  # Un peu d'espace sous le sélecteur
    ),

    # 🔸 Graphique interactif
    dcc.Graph(
        id='graphique',
        figure=px.line(df, x="DateTime", y=["PrévisionJ-1", "PrévisionJ", "Consommation"],
                        markers=True, title="Comparaison des Prévisions et de la Consommation")
    ),
])

# 🔹 Callback pour mettre à jour le graphique en fonction de la période sélectionnée
@app.callback(
    dash.dependencies.Output('graphique', 'figure'),
    [dash.dependencies.Input('date-picker-range', 'start_date'),
     dash.dependencies.Input('date-picker-range', 'end_date')]
)
def update_graph(start_date, end_date):
    # Filtrer les données selon la période sélectionnée
    df_filtered = df[(df['DateTime'] >= start_date) & (df['DateTime'] <= end_date)]

    # Générer le graphique mis à jour
    fig = px.line(df_filtered, x="DateTime", y=["PrévisionJ-1", "PrévisionJ", "Consommation"],
                  markers=True, title="Comparaison des Prévisions et de la Consommation")
    return fig

# 🔹 Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
