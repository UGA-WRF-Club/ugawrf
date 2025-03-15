import os
import matplotlib.pyplot as plt
from matplotlib import colors
from netCDF4 import Dataset
from wrf import getvar, to_np, latlon_coords, extract_times
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from datetime import datetime
from metpy.plots import ctables
import metpy.calc as mpcalc
from metpy.units import units

print("ugawrf data processing script")
start_time = datetime.now()

BASE_OUTPUT = "D:/ugawrf/site/runs"
WRF_FILE = "D:/ugawrf/image/wrfout_d01_2025-03-13_21_00_00"
PRODUCTS = {
    "temperature": "T2",
    "dewp": "Q2",
    "wind": "WSPD10MAX",
    "comp_reflectivity": "REFD_COM",
    "pressure": "AFWA_MSLP",
    "cape": "AFWA_CAPE",
    "cape_mu": "AFWA_CAPE_MU",
    "helicity": "UP_HELI_MAX",
    "total_precip": "AFWA_TOTPRECIP",
    "snowfall": "SNOWNC",
    "echo_tops": "ECHOTOP",
}


wrf_file = Dataset(WRF_FILE)
run_time = str(wrf_file.START_DATE).replace(":", "_")

print(f"processing data for run {run_time}")

def convert_time(nc_time):
    return np.datetime64(nc_time).astype('datetime64[s]').astype(datetime)
forecast_times = [convert_time(t) for t in extract_times(wrf_file, timeidx=None)]

def plot_variable(data, timestep, output_path):
    forecast_time = forecast_times[timestep].strftime("%Y-%m-%d %H:%M UTC")
    plt.figure(figsize=(8, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    lats, lons = latlon_coords(data)
    if data.name == 'T2':
        data_copy = data.copy()
        data_copy = (data_copy - 273.15) * 9/5 + 32
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='nipy_spectral', vmin=-5, vmax=105)
        ax.set_title(f"2 Meter Temperature (°F) - Hour {timestep} - Valid: {forecast_time}")
        label = f"2M Temp (°F)"
    elif data.name == 'Q2':
        # this was such a PITA you have no clue
        sfc_pressure = getvar(wrf_file, 'PSFC', timeidx=timestep)
        e = mpcalc.vapor_pressure(sfc_pressure / 100 * units.mbar, data)
        td = mpcalc.dewpoint(e)
        td = to_np(td) * 9/5 + 32
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(td), cmap='BrBG', vmin=10, vmax=90)
        ax.set_title(f"2 Meter Dewpoint (°F) - Hour {timestep} - Valid: {forecast_time}")
        label = f"2M Dewpoint (°F)"
    elif data.name == 'WSPD10MAX':
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='YlOrRd', vmin=0, vmax=50)
        ax.set_title(f"10 Meter Wind Speed (m/s) - Hour {timestep} - Valid: {forecast_time}")
        label = f"10M Wind Speed (m/s)"
    elif data.name == 'REFD_COM':
        refl_cmap = ctables.registry.get_colortable('NWSReflectivity')
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap=refl_cmap, vmin=2, vmax=70)
        ax.set_title(f"Composite Reflectivity (dbZ) - Hour {timestep} - Valid: {forecast_time}")
        label = f"Composite Reflectivity (dbZ)"
    elif data.name == 'AFWA_TOTPRECIP':
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='magma_r', vmin=0, vmax=100)
        ax.set_title(f"Total Precipitation (mm) - Hour {timestep} - Valid: {forecast_time}")
        label = f"Total Precipitation (mm)"
    elif data.name == 'SNOWNC':
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='BuPu')
        ax.set_title(f"Accumulated Snowfall (mm) - Hour {timestep} - Valid: {forecast_time}")
        label = f"Accumulated Snowfall (mm)"
    elif data.name == 'AFWA_MSLP':
        data_copy = data.copy()
        data_copy = data_copy / 100
        divnorm = colors.TwoSlopeNorm(vmin=970, vcenter=1013, vmax=1050)
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='bwr_r', norm=divnorm)
        ax.set_title(f"Mean Sea Level Pressure (mb) - Hour {timestep} - Valid: {forecast_time}")
        label = f"MSLP (mb)"
    elif data.name == 'ECHOTOP':
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='cividis_r', vmin=0, vmax=50000)
        ax.set_title(f"Echo Tops (m) - Hour {timestep} - Valid: {forecast_time}")
        label = f"Echo Tops (m)"
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
        print(f"processed {product} in {datetime.now() - product_time}")
    except Exception as e:
        print(f"error processing {product}: {e}! last timestep: {t}")

process_time = datetime.now() - start_time
print(f"data processed successfully, this is run {run_time} - took {process_time}")