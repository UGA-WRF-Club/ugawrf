# This module plots our maps.

from wrf import getvar, to_np, latlon_coords, smooth2d
import matplotlib.pyplot as plt
from metpy.units import units
import os
import metpy.calc as mpcalc
import datetime as dt
import cartopy.crs as ccrs
from metpy.plots import ctables
import cartopy.feature as cfeature
from matplotlib import colors

def plot_variable(data, timestep, output_path, forecast_times, airports, run_time, wrf_file):
    forecast_time = forecast_times[timestep].strftime("%Y-%m-%d %H:%M UTC")
    plt.figure(figsize=(8, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    lats, lons = latlon_coords(data)
    data_copy = data.copy()
    if data.name == 'T2':
        data_copy = (data_copy - 273.15) * 9/5 + 32
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='nipy_spectral', vmin=-5, vmax=105)
        ax.set_title(f"2m Temperature (°F) - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Temp (°F)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif data.name == 'Q2':
        # this was such a PITA you have no clue
        sfc_pressure = getvar(wrf_file, 'PSFC', timeidx=timestep)
        e = mpcalc.vapor_pressure(sfc_pressure / 100 * units.mbar, data)
        td = mpcalc.dewpoint(e)
        td = to_np(td) * 9/5 + 32
        data_copy = to_np(td)
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(td), cmap='BrBG', vmin=10, vmax=90)
        ax.set_title(f"2m Dewpoint (°F) - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Dewpoint (°F)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif data.name == 'WSPD10MAX':
        data_copy = data_copy * 2.23694
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='YlOrRd', vmin=0, vmax=80)
        ax.set_title(f"10m Wind Max Speed (mph) - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Wind Max Speed (mph)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif data.name == 'REFD_COM':
        refl_cmap = ctables.registry.get_colortable('NWSReflectivity')
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap=refl_cmap, vmin=2, vmax=70)
        ax.set_title(f"Composite Reflectivity (dbZ) - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Composite Reflectivity (dbZ)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif data.name == 'AFWA_TOTPRECIP':
        data_copy = data_copy / 25.4
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data_copy), 20, cmap='magma_r', vmin=0, vmax=20)
        ax.set_title(f"Total Precipitation (in) - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Precipitation (in)"
    elif data.name == 'SNOWNC':
        data_copy = data_copy / 25.4
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='BuPu', vmin=0, vmax=10)
        ax.set_title(f"Total Accumulated Snowfall (in) - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Accumulated Snowfall (in)"
    elif data.name == 'AFWA_MSLP':
        data_copy = data_copy / 100
        divnorm = colors.TwoSlopeNorm(vmin=970, vcenter=1013, vmax=1050)
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='bwr_r', norm=divnorm)
        smooth_slp = smooth2d(data_copy, 8, cenweight=6)
        plt.contour(to_np(lons), to_np(lats), to_np(smooth_slp), colors="black", transform=ccrs.PlateCarree())
        ax.set_title(f"MSLP (mb) - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"MSLP (mb)"
    elif data.name == 'ECHOTOP':
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='cividis_r', vmin=0, vmax=50000)
        ax.set_title(f"Echo Tops (m) - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Echo Tops (m)"
    else:
        contour = plt.contourf(to_np(lons), to_np(lats), to_np(data), cmap='coolwarm')
        ax.set_title(f"{data.description} - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"{data.description}"
    plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.05, label=label)
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'))
    plt.tight_layout()
    maxmin = ""
    max_value = to_np(data_copy).max()
    min_value = to_np(data_copy).min()
    if max_value != 0:
        maxmin += f"Max: {max_value:.2f}"
        if min_value != 0:
            maxmin += f"\nMin: {min_value:.2f}"
    ax.annotate(maxmin, xy=(0.98, 0.03), xycoords='axes fraction', fontsize=8, color='black', ha='right', va='bottom', bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
    ax.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.02), xycoords='figure fraction', fontsize=8, color='black')
    ax.annotate(f"{(forecast_times[timestep] - dt.timedelta(hours=4))} EST", xy=(0.5, 1), xycoords='axes fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, f"hour_{timestep}.png"))
    plt.close()

def plot_wind_barbs(ax, wrf_file, timestep, lons, lats):
    u10 = getvar(wrf_file, "U10", timeidx=timestep)
    v10 = getvar(wrf_file, "V10", timeidx=timestep)
    stride = 50
    ax.barbs(to_np(lons[::stride, ::stride]), to_np(lats[::stride, ::stride]), to_np(u10[::stride, ::stride]), to_np(v10[::stride, ::stride]), length=6,color='black', pivot='middle', barb_increments={'half': 2.57222, 'full': 5.14444, 'flag': 25.7222})