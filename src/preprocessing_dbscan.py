# preprocessing_dbscan.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import DBSCAN
import os
from Load_data import fetch_all_thingspeak_data
from datetime import datetime, timedelta

# === Tanggal otomatis: ambil hari kemarin ===
end_date = datetime.now().date() - timedelta(days=1)
start_date = end_date

# === Load Data dari ThingSpeak ===
df = fetch_all_thingspeak_data(
    channel_id=2990169,
    api_key="LDXFP3LRNTBZCFMU",
    start_date=start_date,
    end_date=end_date
)

# === Konversi waktu ===
df['created_at'] = pd.to_datetime(df['created_at'])
df.set_index('created_at', inplace=True)

# === Fitur yang digunakan ===
features = ['Temperature', 'Humidity', 'PM2.5', 'PM10', 'CO', 'CO2']
X = df[features].copy()

# === Scaling ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === Clustering dengan DBSCAN (tanpa tuning) ===
dbscan = DBSCAN(eps=0.4, min_samples=6)
dbscan_labels = dbscan.fit_predict(X_scaled)

df['dbscan_cluster'] = dbscan_labels
df['dbscan_outlier'] = dbscan_labels == -1

# Cek jika bisa hitung silhouette score
n_clusters_dbscan = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
if n_clusters_dbscan > 1:
    dbscan_silhouette = silhouette_score(X_scaled, dbscan_labels)
else:
    dbscan_silhouette = None

print("DBSCAN - Jumlah cluster:", n_clusters_dbscan)
print("DBSCAN - Jumlah outlier:", df['dbscan_outlier'].sum())
print("DBSCAN Silhouette Score:", round(dbscan_silhouette, 3) if dbscan_silhouette else "Tidak dapat dihitung")

# === Drop outlier dan kolom clustering ===
df_clean = df[df['dbscan_cluster'] != -1].copy()
df_clean.drop(columns=['dbscan_cluster', 'dbscan_outlier'], inplace=True)

# === Simpan hasil bersih ===
start_str = start_date.strftime('%Y-%m-%d')
end_str = end_date.strftime('%Y-%m-%d')
filename = f"clean_data_{start_str}_to_{end_str}.csv"

os.makedirs("../data/processed", exist_ok=True)
df_clean.to_csv(f"../data/processed/{filename}", index=False)

print(f"\n✅ Preprocessing dan fault detection selesai. File disimpan di: ../data/processed/{filename}")
