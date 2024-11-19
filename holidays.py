import json
import pandas as pd
import logging
from nsepython import nse_holidays

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_and_save_holidays():
    try:
        logging.info("Fetching holidays from NSE")
        holidays = nse_holidays().get('FO', [])
        if not holidays:
            raise ValueError("No 'FO' key found in the response")

        holidays_df = pd.DataFrame(holidays)
        holidays_df = holidays_df[['tradingDate']]
        holidays_df.to_csv("holidays.csv", index=False)
        logging.info("Holidays saved to holidays.csv successfully")

    except ValueError as e:
        logging.error(f"Value error: {e}")
    except json.decoder.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    fetch_and_save_holidays()
