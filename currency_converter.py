import pandas as pd

gbp_USD_df = pd.read_csv('DEXUSUK_exchange_rates.csv')
gbp_USD_df.rename(columns={'DATE': 'date'}, inplace=True)
gbp_USD_df['date'] = pd.to_datetime(gbp_USD_df['date'], errors='coerce')

cad_USD_df = pd.read_csv('DEXCAUS_exchange_rates.csv')
cad_USD_df.rename(columns={'DATE': 'date'}, inplace=True)
cad_USD_df['date'] = pd.to_datetime(cad_USD_df['date'], errors='coerce')

aus_USD_df = pd.read_csv('DEXUSAL_exchange_rates.csv')
aus_USD_df.rename(columns={'DATE': 'date'}, inplace=True)
aus_USD_df['date'] = pd.to_datetime(aus_USD_df['date'], errors='coerce')

eur_USD_df = pd.read_csv('DEXUSEU_exchange_rates.csv')
eur_USD_df.rename(columns={'DATE': 'date'}, inplace=True)
eur_USD_df['date'] = pd.to_datetime(eur_USD_df['date'], errors='coerce')

chf_USD_df = pd.read_csv('DEXSZUS_exchange_rates.csv')
chf_USD_df.rename(columns={'DATE': 'date'}, inplace=True)
chf_USD_df['date'] = pd.to_datetime(chf_USD_df['date'], errors='coerce')

sgd_USD_df = pd.read_csv('DEXSIUS_exchange_rates.csv')
sgd_USD_df.rename(columns={'DATE': 'date'}, inplace=True)
sgd_USD_df['date'] = pd.to_datetime(sgd_USD_df['date'], errors='coerce')

df_payments = pd.read_json("https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-payments.json")
df_payments['date'] = pd.to_datetime(df_payments['date'], errors='coerce')
df_payments = df_payments.sort_values(by='date')

# Merge dataframes on the date column
df_merged = df_payments.merge(gbp_USD_df, on='date', how='left')
df_merged = df_merged.merge(cad_USD_df, on='date', how='left')
df_merged = df_merged.merge(aus_USD_df, on='date', how='left')
df_merged = df_merged.merge(eur_USD_df, on='date', how='left')
df_merged = df_merged.merge(chf_USD_df, on='date', how='left')
df_merged = df_merged.merge(sgd_USD_df, on='date', how='left')


# Convert currencies to USD
df_merged['amount_usd'] = df_merged.apply(
    lambda row: row['amount'] * row['DEXUSUK'] if row['currency'] == 'GBP' else
                row['amount'] / row['DEXCAUS'] if row['currency'] == 'CAD' else
                row['amount'] * row['DEXUSAL'] if row['currency'] == 'AUD' else
                row['amount'] * row['DEXUSEU'] if row['currency'] == 'EUR' else
                row['amount'] / row['DEXSIUS'] if row['currency'] == 'SGD' else
                row['amount'] / row['DEXSZUS'] if row['currency'] == 'CHF' else
                row['amount'], axis=1
)


# Create csv sheet to look over the updated dataframe and verify exchange rate conversions worked
df_merged.to_csv('merged_data.csv')

# remove the exchange rate columns from the dataframe
df_merged = df_merged.drop(['DEXUSUK', 'DEXCAUS', 'DEXUSAL', 'DEXUSEU', 'DEXSIUS', 'DEXSZUS'], axis=1)

