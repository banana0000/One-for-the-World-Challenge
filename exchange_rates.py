import pandas_datareader.data as web
import datetime
import pandas as pd


def get_historical_exchange_rates(start_date="2020-01-01", end_date=None):
    """Fetch historical GBP to USD exchange rates from FRED."""
    if end_date is None:
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")

    try:
        for currency in ['DEXUSUK', 'DEXCAUS', 'DEXUSAL', 'DEXUSEU', 'DEXSIUS', 'DEXSZUS']:
            df = web.DataReader(currency, "fred", start_date, end_date)

            # Create a new DataFrame with all dates in the range
            date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')

            df_filled = df.reindex(date_range).bfill()
            df_filled.reset_index(inplace=True)
            df_filled.rename(columns={'index': 'DATE'}, inplace=True)

            # save df as a csv sheet
            df_filled.to_csv(f"{currency}_exchange_rates.csv", index=False)


    except Exception as e:
        print("Error fetching data:", e)

get_historical_exchange_rates("2014-03-01", "2025-02-28")