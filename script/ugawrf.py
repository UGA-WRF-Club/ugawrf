import os
import sys
from pathlib import Path
from netCDF4 import Dataset
from wrf import getvar, extract_times, ll_to_xy
import numpy as np
import datetime as dt
import json

# processing modules - located in the same folder as (module).py
# if you want to skip generating a certain product, just comment out the module
import textgen
import weathermaps
import meteogram
import skewt

print("UGA-WRF Data Processing Program")
start_time = dt.datetime.now()

# --- START CONFIG --- #

# whenever you add a new product, it will automatically make a new folder at BASE_OUTPUT/(runname)/(product).
# whenever you add a new airport, it will automatically make new folders at BASE_OUTPUT/(runname)/skewt/(airport) and BASE_OUTPUT/(runname)/text/(airport).
# BASE_OUTPUT is whatever you pass in arg2. If you pass nothing, it defaults to (parent folder)/site/runs
# you should not have to manually add new folders.
airports = {
    "ahn": (33.95167820706025, -83.32489875559355),
    "cni": (34.30887599509864, -84.4273590802223),
    "atl": (33.6391621022899, -84.43061412634862),
    "ffc": (33.358755552804176, -84.5711101702346),
    "mcn": (32.70076950826015, -83.64790511895201),
    "rmg": (34.35267229676656, -85.16328449820841),
    "csg": (32.51571975545047, -84.9392150850212),
    "bmx": (33.17895986702925, -86.7823825539515),
    "ohx": (36.24707362357824, -86.56312930475052),
    "gsp": (34.883261598428625, -82.22035185765819)
} # locations to plot numbers on map, skewts, text products, meteograms. meant for airports, you could put any location in domain here
# format is "folder_name": (lat, lon)
# !!! IMPORTANT !!! our current skewt plot function is considerably intensive, taking about ~50 seconds per airport to finish (on my hardware).
# this will scale up quick, so try not to add too many airports right now

PRODUCTS = {
    "temperature": "T2",
    "dewp": "Q2",
    "wind": "WSPD10MAX",
    "comp_reflectivity": "REFD_COM",
    "pressure": "AFWA_MSLP",
    "helicity": "UP_HELI_MAX",
    "total_precip": "AFWA_TOTPRECIP",
    "snowfall": "SNOWNC",
    "echo_tops": "ECHOTOP",
} # these are the products for the map only to output
# format is "folder_name": "variable_name"

# Specify your wrfout and output folder in the commandline. Arg1 is your wrfout, arg2 is where you plan to store the products created.
# If you do not specify one, it will try to use the defaults of (parent folder)/site/runs for your image output
# and (current folder)/wrfout_d01_2025-03-13_21_00_00 (the demo run) for your wrfout inputs.
# An example input: python.exe ugawrf.py "D:\ugawrf_fork\ugawrf\wrfout_d01_2025-03-13_21_00_00" "D:\ugawrf_fork\ugawrf\run"
try:
    WRF_FILE = sys.argv[1]
except:
    root_dir = Path(__file__).resolve().parent
    WRF_FILE = root_dir / "wrfout_d01_2025-03-13_21_00_00"
try:
    BASE_OUTPUT = sys.argv[2]
except:
    root_dir = Path(__file__).resolve().parent.parent
    BASE_OUTPUT = root_dir / "site" / "runs"

# --- END CONFIG --- #

wrf_file = Dataset(WRF_FILE)
run_time = str(wrf_file.START_DATE).replace(":", "_")

print(f"wrfout: {WRF_FILE}")
print(f'image output: {BASE_OUTPUT}')
print(f"let's go! processing data for run {run_time}")

times = extract_times(wrf_file, timeidx=None)
def convert_time(nc_time):
    return np.datetime64(nc_time).astype('datetime64[s]').astype(dt.datetime)
forecast_times = [convert_time(t) for t in times]
hours = len(times) -1

run_metadata = {
    "init_time": str(forecast_times[0]),  # Start time of the model run
    "forecast_hours": hours  # Total forecast length in hours
}
json_output_path = os.path.join(BASE_OUTPUT, run_time, "metadata.json")
os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
with open(json_output_path, "w") as json_file:
    json.dump(run_metadata, json_file, indent=4)
print(f"Metadata JSON saved: {json_output_path}")

# processing starts here

# text data
text_start_time = dt.datetime.now()
for airport, coords in airports.items():
    try:
        text_time = dt.datetime.now()
        text_data = textgen.get_text_data(wrf_file, airport, coords, hours, forecast_times, run_time)
        output_path = os.path.join(BASE_OUTPUT, run_time, "text", airport)
        os.makedirs(output_path, exist_ok=True)
        with open(os.path.join(output_path, "forecast.txt"), 'w') as f:
            for line in text_data:
                f.write(f"{line}\n")
        print(f"processed {airport} text data in {dt.datetime.now() - text_time}")
    except Exception as e:
        print(f"error processing {airport} text: {e}!")
print(f'texts processed successfuly - took {dt.datetime.now() - text_start_time}')

# weather maps
map_time = dt.datetime.now()

for product, variable in PRODUCTS.items():
    try:
        product_time = dt.datetime.now()
        output_path = os.path.join(BASE_OUTPUT, run_time, product)
        for t in range(0, hours + 1):
            data = getvar(wrf_file, variable, timeidx=t)
            weathermaps.plot_variable(data, t, output_path, forecast_times, airports, run_time, wrf_file)
        print(f"processed {product} in {dt.datetime.now() - product_time}")
    except Exception as e:
        print(f"error processing {product}: {e}! last timestep: {t}")
print(f"graphics processed successfully - took {dt.datetime.now() - map_time}")

# meteograms
meteogram_plot_time = dt.datetime.now()

for airport, coords in airports.items():
    try:
        meteogram_time = dt.datetime.now()
        output_path = os.path.join(BASE_OUTPUT, run_time, "meteogram", airport)
        meteogram.plot_meteogram(wrf_file, airport, coords, output_path, forecast_times, hours, run_time)
        print(f"processed {airport} meteogram in {dt.datetime.now() - meteogram_time}")
    except Exception as e:
        print(f"error processing {airport} meteogram: {e}!")
print(f"meteograms processed successfully - took {dt.datetime.now() - meteogram_plot_time}")

# upper air plots
skewt_plot_time = dt.datetime.now()

for airport, coords in airports.items():
    try:
        skewt_time = dt.datetime.now()
        x_y = ll_to_xy(wrf_file, coords[0], coords[1])
        output_path = os.path.join(BASE_OUTPUT, run_time, "skewt", airport)
        for t in range(0, hours + 1):
            skewt.plot_skewt(wrf_file, x_y, t, airport, output_path, forecast_times, run_time)
        print(f"processed {airport} skewt in {dt.datetime.now() - skewt_time}")
    except Exception as e:
        print(f"error processing {airport} upper air plot: {e}!")
print(f"skewt processed successfully - took {dt.datetime.now() - skewt_plot_time}")

process_time = dt.datetime.now() - start_time
print(f"data processed successfully, this is run {run_time} - took {process_time}")
