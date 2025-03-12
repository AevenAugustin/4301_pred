import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import os

# 🔹 Chemin du fichier Excel
file_path = r"C:\Users\Victor\AIC_4301\fichier.xlsx"  # Assure-toi du bon chemin

# 🔹 Vérifier si le fichier existe
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} est introuvable. Vérifie le chemin.")

# 🔹 Lire le fichier Excel avec openpyxl
try:
    df = pd.read_excel(file_path, engine='openpyxl')
except Exception as e:
    raise ValueError(f"Erreur lors de la lecture du fichier : {e}")

# 🔹 Vérifier que les colonnes nécessaires sont présentes
required_columns = {"Heures", "PrévisionJ-1", "PrévisionJ", "Consommation"}
if not required_columns.issubset(df.columns):
    raise ValueError(f"Le fichier doit contenir les colonnes {required_columns}. Colonnes trouvées : {df.columns}")

# 🔹 Création de l’application Dash
app = dash.Dash(__name__)

# 🔹 Layout de l'application
app.layout = html.Div(children=[
    html.H1("Visualisation des Prévisions de Consommation"),

    # 🔸 Slider pour sélectionner une heure
    dcc.Slider(
        id='slider-heure',
        min=0,
        max=len(df) - 1,
        step=1,
        marks={i: str(df['Heures'][i]) for i in range(len(df))},  # Convertir les heures en str
        value=0,  # Valeur initiale
    ),

    # 🔸 Graphique interactif
    dcc.Graph(id='graphique'),
])

# 🔹 Callback pour mettre à jour le graphique en fonction du slider
@app.callback(
    dash.dependencies.Output('graphique', 'figure'),
    [dash.dependencies.Input('slider-heure', 'value')]
)
def update_graph(selected_hour_index):
    # Filtrer les données jusqu'à l'heure sélectionnée
    df_filtered = df.iloc[:selected_hour_index + 1]

    # Générer le graphique mis à jour
    fig = px.line(df_filtered, x="Heures", y=["PrévisionJ-1", "PrévisionJ", "Consommation"],
                  markers=True, title="Comparaison des Prévisions et de la Consommation")

    return fig

# 🔹 Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
