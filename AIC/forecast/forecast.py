import os
import pandas as pd
from prophet import Prophet

def prepare_forecast(file_path, sample_size=None):
    """
    Charge le fichier CSV, prépare les données et réalise des prévisions en captant 
    les variations journalières, hebdomadaires et annuelles.
    
    Args:
        file_path (str): Chemin vers le fichier CSV.
        sample_size (int, optionnel): Nombre de lignes à utiliser pour accélérer les tests.
    
    Returns:
        DataFrame: Fusion des données d'entraînement et de validation avec la colonne 'Forecast' ajoutée.
    """
    # Vérifier que le fichier existe
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")
    
    # Lire le CSV avec le délimiteur ';'
    try:
        df = pd.read_csv(file_path, delimiter=';')
    except Exception as e:
        raise ValueError(f"Erreur lors de la lecture du fichier : {e}")
    
    # Limiter les données pour accélérer les tests si sample_size est défini
    if sample_size is not None:
        df = df.head(sample_size)
    
    # Vérifier que les colonnes indispensables sont présentes
    required_columns = {"Jour", "Heures", "Consommation"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Le fichier doit contenir les colonnes {required_columns}. Colonnes trouvées : {df.columns}")
    
    # Convertir 'Jour' en datetime (format 'dd/mm/YYYY')
    df['Jour'] = pd.to_datetime(df['Jour'], format='%d/%m/%Y', errors='coerce')
    
    # Créer une colonne 'DateTime' en combinant 'Jour' et 'Heures'
    # On suppose que 'Heures' est au format 'HH:MM:SS'
    df['DateTime'] = pd.to_datetime(
        df['Jour'].dt.strftime('%Y-%m-%d') + ' ' + df['Heures'],
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce'
    )
    
    if df['DateTime'].isnull().any():
        raise ValueError("Erreur lors de la conversion des dates. Vérifiez les formats des colonnes 'Jour' et 'Heures'.")
    
    # Trier le DataFrame par ordre chronologique
    df = df.sort_values('DateTime')
    
    # Découper en 80% d'entraînement et 20% de validation
    split_idx = int(len(df) * 0.8)
    train = df.iloc[:split_idx].copy()
    valid = df.iloc[split_idx:].copy()
    
    # Préparer les données pour Prophet (colonnes ds et y)
    train_prophet = train[['DateTime', 'Consommation']].rename(columns={'DateTime': 'ds', 'Consommation': 'y'})
    
    # Instancier le modèle Prophet avec vos paramètres optimisés
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=False,
        yearly_seasonality=False,
        changepoint_prior_scale=0.5,
        n_changepoints=10
    )
    
    # Ajouter la saisonnalité journalière (captant le cycle jour/nuit)
    model.add_seasonality(name='daily', period=1, fourier_order=10)
    # Ajouter la saisonnalité hebdomadaire (effet weekend)
    model.add_seasonality(name='weekly', period=7, fourier_order=3)
    # Ajouter la saisonnalité annuelle (variations saisonnières, ex : consommation plus élevée en hiver)
    model.add_seasonality(name='yearly', period=365.25, fourier_order=12)
    
    # Entraîner le modèle sur les données d'entraînement
    model.fit(train_prophet)
    
    # Prédire sur la période de validation
    future = valid[['DateTime']].rename(columns={'DateTime': 'ds'})
    forecast = model.predict(future)
    valid['Forecast'] = forecast['yhat'].values
    
    # Fusionner les données d'entraînement et de validation pour la visualisation
    df_forecast = pd.concat([train, valid])
    return df_forecast

# Exemple de test (à utiliser uniquement en mode debug ou via Colab)
if __name__ == '__main__':
    file_path = "data_merged_sansprévisions.csv"  # Le fichier CSV doit se trouver à la racine du projet
    df_result = prepare_forecast(file_path, sample_size=2000)
    print(f"Prévisions générées pour {len(df_result)} enregistrements.")
