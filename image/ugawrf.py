import os
import matplotlib.pyplot as plt
from matplotlib import colors
from netCDF4 import Dataset
from wrf import getvar, to_np, latlon_coords, extract_times
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from datetime import datetime

print("ugawrf data processing script")
start_time = datetime.now()

BASE_OUTPUT = "D:/ugawrf/site/runs"
WRF_FILE = "D:/ugawrf/image/wrfout_d01_2025-03-13_21_00_00"
PRODUCTS = {
    "temperature": "T2",
    "wind": "WSPD10MAX",
    "comp_reflectivity": "REFD_COM",
    "pressure": "AFWA_MSLP",
    "cape": "AFWA_CAPE",
    "cape_mu": "AFWA_CAPE_MU",
    "helicity": "UP_HELI_MAX",
    "total_precip": "AFWA_TOTPRECIP",
    "snowfall": "SNOWNC"
}


wrf_file = Dataset(WRF_FILE)
run_time = str(wrf_file.START_DATE).replace(":", "_")

print(f"processing data for run {run_time}")

def convert_time(nc_time):
    return np.datetime64(nc_time).astype('datetime64[s]').astype(datetime)
forecast_times = [convert_time(t) for t in extract_times(wrf_file, timeidx=None)]

def plot_variable(data, timestep, output_path):
    forecast_time = forecast_times[timestep].strftime("%Y-%m-%d %H:%M UTC")
    plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    lats, lons = latlon_coords(data)
    if data.name == 'T2':
        data_copy = data.copy()
        data_copy = (data_copy - 273.15) * 9/5 + 32
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='nipy_spectral', vmin=10, vmax=100)
        ax.set_title(f"2 Meter Temperature (°F) - Hour {timestep} - Valid: {forecast_time}")
        label = f"2M Temp (°F)"
    elif data.name == 'REFD_COM':
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='plasma', vmin=0, vmax=85)
        ax.set_title(f"Composite Reflectivity (dBZ) - Hour {timestep} - Valid: {forecast_time}")
        label = f"Composite Reflectivity (dBZ)"
    elif data.name == 'AFWA_TOTPRECIP':
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='magma_r', vmin=0, vmax=100)
        ax.set_title(f"Total Precipitation (mm) - Hour {timestep} - Valid: {forecast_time}")
        label = f"Total Precipitation (mm)"
    elif data.name == 'SNOWNC':
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='BuPu')
        ax.set_title(f"Accumulated Snowfall - Hour {timestep} - Valid: {forecast_time}")
        label = f"Accumulated Snowfall"
    elif data.name == 'AFWA_MSLP':
        data_copy = data.copy(e)
        data_copy = data_copy / 100
        divnorm = colors.TwoSlopeNorm(vmin=970, vcenter=1013, vmax=1050)
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='bwr_r', norm=divnorm)
        ax.set_title(f"Mean Sea Level Pressure (mb) - Hour {timestep} - Valid: {forecast_time}")
        label = f"MSLP (mb)"
    else:
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='coolwarm')
        ax.set_title(f"{data.description} - Hour {timestep} - Valid: {forecast_time}")
        label = f"{data.description}"
    plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.05, label=label)
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'))
    ax.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.01), xycoords='figure fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, f"hour_{timestep}.png"))
    plt.close()
for product, variable in PRODUCTS.items():
    try:
        product_time = datetime.now()
        output_path = os.path.join(BASE_OUTPUT, run_time, product)
        for t in range(0, 25):
            data = getvar(wrf_file, variable, timeidx=t)
            plot_variable(data, t, output_path)
        product_end_time = datetime.now()
        print(f"processed {product} in {product_end_time - product_time}")
    except Exception as e:
        print(f"error processing {product}: {e}! last timestep: {t}")

end_time = datetime.now()
process_time = end_time - start_time
print(f"data processed successfully, this is run {run_time} - took {process_time}")