import pandas as pd
import argparse
import requests
import io
import os
from datetime import timedelta

parser = argparse.ArgumentParser(description='A helper tool to automate verification of UGA-WRF output CSVs')
parser.add_argument('csv_file', type=str, help='Path to the Model Output CSV')
parser.add_argument('--output', type=str, default=None, help='Output filename.')
args = parser.parse_args()

def main():
    if not os.path.exists(args.csv_file):
        print(f"{args.csv_file} not found.")
        return
    print(f"reading model data from {args.csv_file}...")
    df_model = pd.read_csv(args.csv_file)
    df_model['Valid Time (UTC)'] = pd.to_datetime(df_model['Valid Time (UTC)'])
    min_time = df_model['Valid Time (UTC)'].min() - timedelta(hours=2)
    max_time = df_model['Valid Time (UTC)'].max() + timedelta(days=1)
    station = df_model['Airport'].iloc[0] 
    print(f"Fetching observations for {station}...")
    try:
        response = requests.get("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py", params={"station": station, "data": ["tmpf", "dwpf", "sknt", "mslp"], "year1": min_time.year, "month1": min_time.month, "day1": min_time.day, "year2": max_time.year, "month2": max_time.month, "day2": max_time.day, "tz": "Etc/UTC", "format": "onlycomma", "latlon": "no", "missing": "M", "report_type": "3"})
        df_obs = pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
    for col in ['tmpf', 'dwpf', 'sknt', 'mslp']:
        if col in df_obs.columns:
            df_obs[col] = pd.to_numeric(df_obs[col], errors='coerce')
    df_obs['valid'] = pd.to_datetime(df_obs['valid'])
    df_obs['valid_round'] = df_obs['valid'].dt.round('h')
    df_obs['obs_wind_mph'] = df_obs['sknt'] * 1.15078
    merged = pd.merge(df_model, df_obs, left_on='Valid Time (UTC)', right_on='valid_round', how='inner')
    merged['METAR_OBS'] = df_obs['valid']
    merged['Error_Temp'] = merged['Temperature (F)'] - merged['tmpf']
    merged['Error_Dew'] = merged['Dew Point (F)'] - merged['dwpf']
    merged['Error_Wind'] = merged['Wind Speed (mph)'] - merged['obs_wind_mph']
    merged['Error_MSLP'] = merged['Pressure (mb)'] - merged['mslp']
    merged.rename(columns={'valid': 'Obs Time (UTC)'}, inplace=True)
    if args.output:
        out_file = args.output
    else:
        out_file = f"verified_{os.path.basename(args.csv_file)}"
    final_cols = ['Init Time (UTC)', 'Airport', 'Forecast Hour','Valid Time (UTC)', 'Obs Time (UTC)', 'Temperature (F)', 'tmpf', 'Error_Temp', 'Wind Speed (mph)', 'obs_wind_mph', 'Error_Wind', 'Pressure (mb)', 'mslp', 'Error_MSLP']
    merged[final_cols].to_csv(out_file, index=False)
    print(f"verified {len(merged)} forecast times to obs. saved to {out_file}")
if __name__ == "__main__":
    main()