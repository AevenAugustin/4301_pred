from flask import Flask, request, jsonify
import pandas as pd
from prophet import Prophet
from datetime import timedelta

app = Flask(__name__)

# Chemin du CSV dans le container
file_path = '/app/backend/data/data_merged.csv'
df = pd.read_csv(file_path, delimiter=';')

# Vérification des colonnes
required_columns = {"Jour", "Heures", "PrévisionJ-1", "PrévisionJ", "Consommation"}
if not required_columns.issubset(df.columns):
    raise ValueError(f"Colonnes manquantes dans le CSV. Attendu: {required_columns}. Trouvé: {df.columns}")

# Conversion de la colonne Jour en datetime
df['Jour'] = pd.to_datetime(df['Jour'], format='%d/%m/%Y', errors='coerce')

# Fusionner Jour et Heures pour créer la colonne ds
df['ds'] = pd.to_datetime(df['Jour'].astype(str) + ' ' + df['Heures'].astype(str), format='%Y-%m-%d %H:%M', errors='coerce')
df['y'] = df['Consommation']
df.sort_values('ds', inplace=True)

df_daily = df.resample('D', on='ds').sum(numeric_only=True).reset_index()

# On utilise les données agrégées pour l'entraînement/prévision
df_model = df_daily.copy()

@app.route('/forecast', methods=['GET'])
def forecast():
    """
    Si test_mode=true, effectue un découpage train/test (80% train / 20% test)
    et prédit sur la partie test (données quotidiennes).
    Sinon, effectue une prévision future sur des dates choisies.
    """
    test_mode = request.args.get("test_mode", "false").lower() == "true"
    
    if test_mode:
        # --- Mode évaluation avec découpage train/test ---
        df_sorted = df_model.sort_values("ds")
        n = len(df_sorted)
        train_size = int(n * 0.8)
        df_train = df_sorted.iloc[:train_size]
        df_test = df_sorted.iloc[train_size:]
        
        model = Prophet()
        model.fit(df_train[['ds', 'y']])
        
        last_train_date = df_train['ds'].max()
        forecast_start = last_train_date + timedelta(days=1)  
        test_end = df_test['ds'].max()
        
        periods = (test_end - forecast_start).days + 1
        if periods <= 0:
            return jsonify([])
        
        future = model.make_future_dataframe(periods=periods, freq='D', include_history=False)
        future = future[(future['ds'] >= forecast_start) & (future['ds'] <= test_end)]
        forecast_result = model.predict(future)
        result = forecast_result[['ds', 'yhat']].rename(columns={'ds': 'DateTime', 'yhat': 'Forecast'})
        return result.to_json(orient='records')
    
    else:
        # --- Mode forecasting futur ---
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if not start_date_str or not end_date_str:
            return jsonify({"error": "Les paramètres start_date et end_date sont requis."}), 400

        try:
            start_date = pd.to_datetime(start_date_str)
            end_date = pd.to_datetime(end_date_str)
        except Exception as e:
            return jsonify({"error": f"Format de date invalide: {e}"}), 400

        last_date = df_model['ds'].max()
        forecast_start = last_date + timedelta(days=1)  
        periods = (end_date - forecast_start).days + 1
        if periods <= 0:
            return jsonify([])

        model = Prophet()
        model.fit(df_model[['ds', 'y']])
        future = model.make_future_dataframe(periods=periods, freq='D', include_history=False)
        future = future[(future['ds'] >= forecast_start) & (future['ds'] <= end_date)]
        forecast_result = model.predict(future)
        result = forecast_result[['ds', 'yhat']].rename(columns={'ds': 'DateTime', 'yhat': 'Forecast'})
        return result.to_json(orient='records')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

