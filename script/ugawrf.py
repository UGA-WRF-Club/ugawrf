import os
import sys
from pathlib import Path
from netCDF4 import Dataset
from wrf import extract_times, ll_to_xy
import numpy as np
import datetime as dt
import json

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
    if sys.argv[2] == "default":
        BASE_OUTPUT = Path(__file__).resolve().parent.parent / "site" / "runs"
    else:
        BASE_OUTPUT = sys.argv[2]
except:
    root_dir = Path(__file__).resolve().parent.parent
    BASE_OUTPUT = root_dir / "site" / "runs"

# use run flags, arg3 to specify if you want to disable a certain product or not. This is useful for debugging/concurrent running.
# 1 - textgen
# 2 - weathermaps
# 3 - special
# 4 - meteogram
# 5 - skewt
# ex: python.exe ugawrf.py "D:\ugawrf_fork\ugawrf\wrfout_d01_2025-03-13_21_00_00" default "245"
# this will run all modules except for meteogram and skewt
try:
    run_flags = sys.argv[3]
except:
    run_flags = "0"

# processing modules - located in the same folder as (module).py
# if you want to skip generating a certain product, just comment out the module
modules_enabled = []
if "1" not in run_flags:
    import textgen
    modules_enabled.append("textgen")
if "2" not in run_flags:
    import weathermaps
    modules_enabled.append("weathermaps")
if "3" not in run_flags:
    import special
    modules_enabled.append("special")
if "4" not in run_flags:
    import meteogram
    modules_enabled.append("meteogram")
if "5" not in run_flags:
    import skewt
    modules_enabled.append("skewt")

print("UGA-WRF Data Processing Program")
print(f'Modules: {modules_enabled}')
start_time = dt.datetime.now()

# --- START CONFIG --- #

# whenever you add a new product, it will automatically make a new folder at BASE_OUTPUT/(runname)/(product).
# whenever you add a new airport, it will automatically make new folders at BASE_OUTPUT/(runname)/skewt/(airport) and BASE_OUTPUT/(runname)/text/(airport).
# BASE_OUTPUT is whatever you pass in arg2. If you pass nothing, it defaults to (parent folder)/site/runs
# you should not have to manually add new folders.
high_prio_airports ={
    "ahn": (33.95167820706025, -83.32489875559355),
    "cni": (34.30887599509864, -84.4273590802223),
    "ffc": (33.358755552804176, -84.5711101702346),
    "mcn": (32.70076950826015, -83.64790511895201),
    "csg": (32.51571975545047, -84.9392150850212),
    "bmx": (33.17895986702925, -86.7823825539515),
    "gsp": (34.883261598428625, -82.22035185765819),
    "hun": (34.72526357496368, -86.64485933237611),
    "tae": (30.394458005924445, -84.3398597480267),
    "sav": (32.128213416567114, -81.19987457392587),
    "ags": (33.369475015594105, -81.96517834789427),
    "tys": (35.807073917260894, -83.99815749815394),
} # locations to plot numbers on map, text products, meteograms. meant for airports, you could put any location in domain here
# !!! IMPORTANT !!! our current skewt plot function is considerably intensive, taking about ~50 seconds per airport to finish (on my hardware).
# this will scale up quick, so try not to add too many airports to this one right now
other_airports = {
    "atl": (33.6391621022899, -84.43061412634862),
    "rmg": (34.35267229676656, -85.16328449820841),
    "aby": (31.53370678927006, -84.18738548637639),
    "vdi": (32.19211787190395, -82.36896971377632),
    "avl": (35.437208530161925, -82.53944681688363),
    "jax": (30.492570769985885, -81.68571176177561),
    "ohx": (36.24707362357824, -86.56312930475052),
} # same as above minus generating a skewt (time saving) - more ok to plot many here
# format is "folder_name": (lat, lon)

PRODUCTS = {
    "temperature": "T2",
    "1hr_temp_c": "T2",
    "dewp": "td2",
    '1hr_dewp_c': 'td2',
    "rh": "rh2",
    "pressure": "AFWA_MSLP",
    "wind": "wspd_wdir10",
    "wind_gust": "WSPD10MAX",
    "comp_reflectivity": "REFD_COM",
    "helicity": "UP_HELI_MAX",
    "mcape": "cape_2d",
    "mcin": "cape_2d",
    "1hr_precip": "AFWA_TOTPRECIP",
    "total_precip": "AFWA_TOTPRECIP",
    "1hr_snowfall": "SNOWNC",
    "snowfall": "SNOWNC",
    "cloudcover": "cloudfrac",
    "echo_tops": "ECHOTOP",
    

    # upper level vars are very taxing to process: feel free to comment some/all of them out while you're working locally!
    "temp_850mb": "tc",
    "temp_700mb": "tc",
    "temp_500mb": "tc",
    "temp_300mb": "tc",
    "1hr_temp_c_850mb": "tc",
    "1hr_temp_c_700mb": "tc",
    "1hr_temp_c_500mb": "tc",
    "1hr_temp_c_300mb": "tc",
    "td_850mb": "td",
    "td_700mb": "td",
    "td_500mb": "td",
    "td_300mb": "td",
    "rh_850mb": "rh",
    "rh_700mb": "rh",
    "rh_500mb": "rh",
    "rh_300mb": "rh",
    "wind_850mb": "ua",
    "wind_700mb": "ua",
    "wind_500mb": "ua",
    "wind_300mb": "ua",
    "heights_700mb": "z",
    "heights_500mb": "z",
    
} # these are the products for the map only to output
# format is "folder_name": "variable_name"
# if you're plotting upper air, appending _(level)mb to the end of your folder name interps your pressure level to (level)

# --- END CONFIG --- #

airports = {**high_prio_airports, **other_airports}

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
    "init_time": str(forecast_times[0]),
    "forecast_hours": hours,
    "products": list(PRODUCTS.keys())
}
json_output_path = os.path.join(BASE_OUTPUT, run_time, "metadata.json")
os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
with open(json_output_path, "w") as json_file:
    json.dump(run_metadata, json_file, indent=4)
print(f"Metadata JSON saved: {json_output_path}")

# processing starts here

# text data
if "textgen" in modules_enabled:
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

# weathermaps
if "weathermaps" in modules_enabled:
   
    map_time = dt.datetime.now()

    for product, variable in PRODUCTS.items():
        try:
            product_time = dt.datetime.now()
            output_path = os.path.join(BASE_OUTPUT, run_time, product)
            level = None
            if "_" in product and "mb" in product:
                level = int(product.split("_")[-1].replace("mb", ""))
            for t in range(0, hours + 1):
                weathermaps.plot_variable(product, variable, t, output_path, forecast_times, airports, run_time, wrf_file, level)
            print(f"processed {product} in {dt.datetime.now() - product_time}")
        except Exception as e:
            print(f"error processing {product}: {e}! last timestep: {t}")
    print(f"graphics processed successfully - took {dt.datetime.now() - map_time}")

# special plots
if "special" in modules_enabled:
    special_plot_time = dt.datetime.now()
    try:
        output_path = os.path.join(BASE_OUTPUT, run_time)
        for t in range(0, hours + 1):
            special.generate_cloud_cover(t, os.path.join(output_path, "4panel_cloudcover"), forecast_times, run_time, wrf_file)
        special.hr24_change(os.path.join(output_path, "24hr_change"), airports, forecast_times, run_time, wrf_file)
        print(f"processed special plots in {dt.datetime.now() - special_plot_time}")
    except Exception as e:
        print(f"error processing special plots: {e}!")
    print(f"special plots processed successfully - took {dt.datetime.now() - special_plot_time}")

# meteograms
if "meteogram" in modules_enabled:
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
if "skewt" in modules_enabled:
    skewt_plot_time = dt.datetime.now()

    for airport, coords in high_prio_airports.items():
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
print(f"modules {modules_enabled} processed successfully, this is run {run_time} - took {process_time}")
