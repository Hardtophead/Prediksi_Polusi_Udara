import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
import joblib

def preprocess_data(input_csv_path, output_csv_path, scaler_path):
    # Load data
    df = pd.read_csv(input_csv_path, parse_dates=['created_at'])

    # Pilih kolom yang digunakan untuk prediksi
    selected_columns = ['Temperature', 'Humidity', 'PM2.5', 'PM10', 'CO', 'CO2']
    df = df[['created_at'] + selected_columns]

    # Buang baris dengan nilai kosong (jika ada)
    df.dropna(subset=selected_columns, inplace=True)

    # Inisialisasi scaler dan lakukan scaling
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(df[selected_columns])

    # Buat dataframe hasil scaling
    df_scaled = pd.DataFrame(scaled_values, columns=[f"{col}_scaled" for col in selected_columns])
    df_final = pd.concat([df[['created_at']], df_scaled], axis=1)

    # Simpan hasil preprocessing
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df_final.to_csv(output_csv_path, index=False)

    # Simpan scaler ke file
    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
    joblib.dump(scaler, scaler_path)

    print(f"Preprocessing selesai. Data disimpan di: {output_csv_path}")
    print(f"Scaler disimpan di: {scaler_path}")

# Contoh penggunaan
if __name__ == "__main__":
    preprocess_data(
        input_csv_path="data/raw/ENV_data_2025-06-15_to_2025-06-22.csv",
        output_csv_path="data/processed/preprocessed_data.csv",
        scaler_path="models/scaler.pkl"
    )
