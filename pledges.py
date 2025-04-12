import pandas as pd
import requests

# JSON adat letöltése
json_url = "https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-pledges.json"
response = requests.get(json_url)
json_data = response.json()

# JSON átalakítása DataFrame formátumba
df_json = pd.DataFrame(json_data)

# DataFrame mentése CSV fájlba
csv_file_path = "one-for-the-world-pledges.csv"
df_json.to_csv(csv_file_path, index=False)

print(f"CSV fájl elmentve: {csv_file_path}")
