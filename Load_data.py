import requests
import pandas as pd
from datetime import datetime, timedelta
import os

def fetch_all_thingspeak_data(channel_id, api_key=None, start_date=None, end_date=None, batch_days=7):
    all_data = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=batch_days), end_date)

        url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
        params = {
            'start': current_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'end': current_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'api_key': api_key,
            'timezone': 'Asia/Jakarta'
        }

        r = requests.get(url, params=params)
        r.raise_for_status()
        feeds = r.json().get('feeds', [])
        all_data.extend(feeds)

        print(f"Fetched: {current_start} → {current_end}, Rows: {len(feeds)}")
        current_start = current_end

    df = pd.DataFrame(all_data)
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Rename kolom field ke nama Polusi
    df = df.rename(columns={
        'field1': 'Temperature',
        'field2': 'Humidity',
        'field3': 'PM2.5',
        'field4': 'PM10',
        'field5': 'CO',
        'field6': 'CO2'
    })

    df.drop(columns=['entry_id'], inplace=True)

    # Simpan ke folder data/raw/
    os.makedirs("data/raw", exist_ok=True)
    filename = f"data/raw/ENV_data_{start_date.date()}_to_{end_date.date()}.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

    return df

# df_all = fetch_all_thingspeak_data(
#     channel_id=2990169,
#     api_key="LDXFP3LRNTBZCFMU",
#     start_date=datetime(2025, 6, 16),
#     end_date=datetime(2025, 6, 23)
# )
