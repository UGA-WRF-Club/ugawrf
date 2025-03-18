# This module plots our maps.

from wrf import getvar, to_np, latlon_coords
import matplotlib.pyplot as plt
from metpy.units import units
import os
import metpy.calc as mpcalc
import datetime as dt
import cartopy.crs as ccrs
from metpy.plots import ctables
import cartopy.feature as cfeature
from matplotlib import colors

def plot_variable(data, timestep, output_path, forecast_times, run_time, wrf_file):
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
    ax.annotate(f"{(forecast_times[timestep] - dt.timedelta(hours=4))} EST", xy=(0.75, 1), xycoords='axes fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, f"hour_{timestep}.png"))
    plt.close()