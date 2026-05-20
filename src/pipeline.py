import os
import requests
import pandas as pd

def extract_and_transform():
    api_url = "https://api.openaq.org/v3/sensors/7773515"
    header = {"x-api-key": os.environ['OPENAQ_KEY']}
    params = {"limit": 1000}
    try:
        response = requests.get(api_url, params=params, headers=header, timeout=120)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            output = pd.json_normalize(data['results'])
            df = pd.DataFrame(output)
            if df.empty:
                return None
            df['latest.datetime.utc'] = pd.to_datetime(df['latest.datetime.utc'], errors='coerce')
            df['latest.datetime.local'] = pd.to_datetime(df['latest.datetime.local'], errors='coerce').dt.tz_convert('Europe/Madrid')
            return df
    except requests.exceptions.RequestException:
        return None

if __name__ == "__main__":
    df = extract_and_transform()
    if df is not None:
        data_directory = os.path.join(os.getcwd(), "data")
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        data_file = os.path.join(data_directory, "air_data.csv")
        if not os.path.exists(data_file):
            df.to_csv(data_file, index=False)
        else:
            df.to_csv(data_file, mode='a', header=False, index=False)
