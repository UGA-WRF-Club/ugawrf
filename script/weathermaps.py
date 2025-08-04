# This module plots our maps.

from wrf import getvar, to_np, latlon_coords, smooth2d, ll_to_xy, interplevel
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import datetime as dt
import cartopy.crs as ccrs
from metpy.plots import ctables, USCOUNTIES
import cartopy.feature as cfeature
from matplotlib import colors
import numpy as np

def plot_variable(product, variable, timestep, output_path, forecast_times, airports, loc, extent, run_time, wrf_file, level=None):
    data = getvar(wrf_file, variable, timeidx=timestep)
    data_copy = data.copy()
    if level:
        pressure = getvar(wrf_file, "pressure", timeidx=timestep)
        data_copy = to_np(interplevel(data, pressure, level))
    forecast_time = forecast_times[timestep].strftime("%Y-%m-%d %H:%M UTC")
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={"projection": ccrs.PlateCarree()})
    if extent is not None:
        ax.set_extent(extent, crs=ccrs.PlateCarree())
    lats, lons = latlon_coords(data)
    if product == 'temperature':
        data_copy = (data_copy - 273.15) * 9/5 + 32
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='nipy_spectral', levels=np.arange(-10, 110, 5), extend='both')
        ax.set_title(f"2m Temperature (°F) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Temp (°F)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif product == '1hr_temp_c':
        if timestep > 0:
            temp_now = getvar(wrf_file, "T2", timeidx=timestep)
            temp_prev = getvar(wrf_file, "T2", timeidx=timestep - 1)
            temp_change_1hr = (temp_now - temp_prev) * 9/5
            data_copy = temp_change_1hr.copy()
        else:
            ax.annotate("This product starts on hour 1.", xy=(0.5, 0.5), xycoords='figure fraction', fontsize=8, color='black', ha='right', va='bottom', bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'))
            temp_change_1hr = data_copy * 0
            data_copy = data_copy * 0
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(temp_change_1hr), cmap="coolwarm", vmin=-10, vmax=10, extend='both')
        ax.set_title(f"1 Hour 2m Temp Change (°F) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Temperature Change (°F)'
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif product == 'dewp':
        data_copy = data_copy * 9/5 + 32
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='BrBG', levels=np.arange(10, 85, 5), extend='both')
        ax.set_title(f"2m Dewpoint (°F) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Dewpoint (°F)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif product == '1hr_dewp_c':
        if timestep > 0:
            dewp_now = getvar(wrf_file, "td2", timeidx=timestep)
            dewp_prev = getvar(wrf_file, "td2", timeidx=timestep - 1)
            dewp_change_1hr = (dewp_now - dewp_prev) * 9/5
            data_copy = dewp_change_1hr.copy()
        else:
            ax.annotate("This product starts on hour 1.", xy=(0.5, 0.5), xycoords='figure fraction', fontsize=8, color='black', ha='right', va='bottom', bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'))
            dewp_change_1hr = data_copy * 0
            data_copy = data_copy * 0
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(dewp_change_1hr), cmap="BrBG", vmin=-20, vmax=20, extend='both')
        ax.set_title(f"1 Hour 2m Dewpoint Change (°F) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Dewpoint Change (°F)'
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif product == 'rh':
        levels = np.arange(0, 100, 5)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='BrBG', levels=levels, extend="max")
        ax.set_title(f"2m Relative Humidity (%) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Relative Humidity (%)"
    elif product == 'wind':
        data_copy = data[0].copy()
        data_copy = data_copy * 2.23694
        divnorm = colors.TwoSlopeNorm(vmin=0, vcenter=30, vmax=90)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='YlOrRd', norm=divnorm)
        ax.set_title(f"10m Wind Speed (mph) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = "Wind Speed (mph)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
        plot_streamlines(ax, wrf_file, timestep, lons, lats)
    elif product == 'wind_gust':
        data_copy = data_copy * 2.23694
        divnorm = colors.TwoSlopeNorm(vmin=0, vcenter=50, vmax=110)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='YlOrRd', norm=divnorm)
        ax.set_title(f"10m Wind Gust (mph) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Wind Max (mph)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
        plot_streamlines(ax, wrf_file, timestep, lons, lats)
    elif product == 'comp_reflectivity':
        refl_cmap = ctables.registry.get_colortable('NWSReflectivity')
        data_masked = np.ma.masked_less(data_copy, 2)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_masked), cmap=refl_cmap, levels=np.arange(0, 75, 5), extend='max')
        ax.set_title(f"Composite Reflectivity (dbZ) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Composite Reflectivity (dbZ)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif product == 'total_precip':
        data_copy = data_copy / 25.4
        precip_cmap = ctables.registry.get_colortable('precipitation')
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap=precip_cmap, levels=np.arange(0, 20, 0.25), extend='max')
        ax.set_title(f"Total Precipitation (in) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Precipitation (in)"
    elif product == '1hr_precip':
        rain_now = getvar(wrf_file, "AFWA_TOTPRECIP", timeidx=timestep)
        rain_prev = getvar(wrf_file, "AFWA_TOTPRECIP", timeidx=timestep - 1) if timestep > 0 else rain_now * 0
        precip_1hr = (rain_now - rain_prev) / 25.4
        data_copy = precip_1hr.copy()
        precip_cmap = ctables.registry.get_colortable('precipitation')
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(precip_1hr), cmap=precip_cmap, levels=np.arange(0, 5, 0.1), extend='max')
        ax.set_title(f"1 Hour Precipitation (in) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'1 Hour Rainfall (in)'
    elif product == 'snowfall':
        data_copy = data_copy / 25.4
        divnorm = colors.TwoSlopeNorm(vmin=0, vcenter=1, vmax=10)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='Blues', norm=divnorm, extend='max')
        ax.set_title(f"Total Accumulated Snowfall (in) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Accumulated Snowfall (in)"
    elif product == '1hr_snowfall':
        snow_now = getvar(wrf_file, "SNOWNC", timeidx=timestep)
        snow_prev = getvar(wrf_file, "SNOWNC", timeidx=timestep - 1) if timestep > 0 else snow_now * 0
        snow_1hr = (snow_now - snow_prev) / 25.4
        data_copy = snow_1hr.copy()
        divnorm = colors.TwoSlopeNorm(vmin=0, vcenter=0.3, vmax=3)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(snow_1hr), cmap='Blues', norm=divnorm, extend='max')
        ax.set_title(f"1 Hour Accumulated Snowfall (in) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Accumulated Snowfall'
    elif product == 'pressure':
        data_copy = data_copy / 100
        divnorm = colors.TwoSlopeNorm(vmin=970, vcenter=1013, vmax=1050)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='bwr_r', norm=divnorm, extend='both')
        smooth_slp = smooth2d(data_copy, 8, cenweight=6)
        ax.contour(to_np(lons), to_np(lats), to_np(smooth_slp), colors="black", transform=ccrs.PlateCarree(), levels=np.arange(960, 1060, 4))
        ax.set_title(f"MSLP (mb) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"MSLP (mb)"
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif product == 'echo_tops':
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data), cmap='cividis_r', vmin=0, vmax=50000, extend='max')
        ax.set_title(f"Echo Tops (m) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"Echo Tops (m)"
    elif product == 'helicity':
        helicity_sum = 0
        for t in range(timestep + 1):  
            helicity = getvar(wrf_file, "UP_HELI_MAX", timeidx=t)
            helicity_sum += to_np(helicity)
        reflectivity = getvar(wrf_file, "REFD_COM", timeidx=timestep)
        reflectivity_masked = np.ma.masked_less(reflectivity, 2)
        refl_cmap = ctables.registry.get_colortable("NWSReflectivity")
        ax.contourf(to_np(lons), to_np(lats), to_np(reflectivity_masked), cmap=refl_cmap, levels=np.arange(0, 75, 5), alpha=0.3)
        contour = ax.contourf(to_np(lons), to_np(lats), helicity_sum, levels=[50, 100, 200, 300, 400, 500], colors=['green', 'cyan', 'blue', 'purple', 'red', 'black'], alpha=0.7)
        ax.contour(to_np(lons), to_np(lats), helicity_sum, levels=[50, 100, 200, 300, 400, 500], colors=['green', 'cyan', 'blue', 'purple', 'red', 'black'], linestyles='dashed')
        ax.set_title(f"Helicity Tracks (m^2/s^2) + Comp. Reflectivity (dbZ, transparent) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Helicity m^2/s^2'
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats)
    elif product == 'cloudcover':
        low_cloud_frac = to_np(data_copy[0]) * 100 
        mid_cloud_frac = to_np(data_copy[1]) * 100
        high_cloud_frac = to_np(data_copy[2]) * 100
        total_cloud_frac = low_cloud_frac + mid_cloud_frac + high_cloud_frac
        data_copy = total_cloud_frac
        contour = ax.pcolormesh(to_np(lons), to_np(lats), total_cloud_frac, cmap="Blues_r", norm=plt.Normalize(0, 100), transform=ccrs.PlateCarree())
        ax.set_title(f"Cloud Cover - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Cloud Fraction (%)'
    elif product == 'mcape':
        data_copy = data[0].copy()
        label = f'CAPE (J/kg)'
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='magma_r', vmin=0, vmax=6000)
        ax.set_title(f"Max CAPE (MU 500m Parcel) (J/kg) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
    elif product == 'mcin':
        data_copy = data[1].copy()
        label = f'CIN (J/kg)'
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='magma_r', vmin=0, vmax=6000)
        ax.set_title(f"Max CIN (MU 500m Parcel) (J/kg) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
    elif product.startswith("temp") and level != None:
        cmax, cmin = None, None
        if level == 850:
            cmax, cmin = 40, -20
        elif level == 700:
            cmax, cmin = 30, -30
        elif level == 500:
            cmax, cmin = 20, -50
        elif level == 300:
            cmax, cmin = 0, -70
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='nipy_spectral', levels=np.arange(cmin, cmax, 2), extend='both')
        ax.set_title(f"{level}mb Temp (°C) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Temp (°C)'
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats, level)
    elif product.startswith("td") and level != None:
        cmax, cmin = None, None
        if level == 850:
            cmax, cmin = 30, -20
        elif level == 700:
            cmax, cmin = 10, -30
        elif level == 500:
            cmax, cmin = 0, -50
        elif level == 300:
            cmax, cmin = -30, -70
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='BrBG', levels=np.arange(cmin, cmax, 2), extend='both')
        ax.set_title(f"{level}mb Dew Point (°C) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Dew Point (°C)'
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats, level)
    elif product.startswith("rh") and level != None:
        levels = np.arange(0, 100, 5)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='BrBG', levels=levels, extend='max')
        ax.set_title(f"{level}mb Relative Humidity (%) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Relative Humidity (%)'
    elif product.startswith("te") and level != None:
        if level == 850:
            levels = np.arange(300, 371, 2)
        elif level == 700:
            levels = np.arange(290, 371, 2)
        else:
            levels = np.linspace(np.nanmin(data_copy), np.nanmax(data_copy), 20)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='turbo', levels=levels, extend='both')
        ax.set_title(f"{level}mb Theta E (K) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats, level)
        label = f'Theta E (K)'
    elif product.startswith("wind") and level != None:
        va = interplevel(getvar(wrf_file, "va", timeidx=timestep), pressure, level)
        ws = np.sqrt(to_np(data_copy)**2 + to_np(va)**2) * 1.94384  # Convert m/s to knots
        data_copy = ws
        cmax = None
        if level == 850:
            cmax = 75
        elif level == 700:
            cmax = 85
        elif level == 500:
            cmax = 105
        elif level == 300:
            cmax = 145
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(ws), cmap="plasma", vmax=cmax)
        ax.set_title(f"{level}mb Wind Speed (kt) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Wind Speed (kt)'
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats, level)
        plot_streamlines(ax, wrf_file, timestep, lons, lats, level)
    elif product.startswith("height") and level != None:
        cmax, cmin = None, None
        data_copy = data_copy / 10
        if level == 700:
            cmax, cmin = 350, 250
        elif level == 500:
            cmax, cmin = 600, 500
        smooth_z = smooth2d(data_copy, 40, cenweight=6)
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='coolwarm', vmax=cmax, vmin=cmin)
        ax.contour(to_np(lons), to_np(lats), to_np(smooth_z), colors="black", transform=ccrs.PlateCarree(), levels=np.arange(100, 1000, 5))
        ax.set_title(f"{level}mb Height (dam) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Height (dam)'
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats, level)
    elif product.startswith('1hr_temp_c') and level != None:
        if timestep > 0:
            temp_now = getvar(wrf_file, "tc", timeidx=timestep)
            temp_prev = getvar(wrf_file, "tc", timeidx=timestep - 1)
            upper_temp_now = interplevel(temp_now, pressure, level)
            upper_temp_prev = interplevel(temp_prev, pressure, level)
            temp_change_1hr = (upper_temp_now - upper_temp_prev)
            data_copy = temp_change_1hr.copy()
        else:
            ax.annotate("This product starts on hour 1.", xy=(0.5, 0.5), xycoords='figure fraction', fontsize=8, color='black', ha='right', va='bottom', bbox=dict(facecolor='white', alpha=0.9, edgecolor='none'))
            temp_change_1hr = data_copy * 0
            data_copy = data_copy * 0
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(temp_change_1hr), cmap="coolwarm", vmin=-15, vmax=15)
        ax.set_title(f"1-Hour {level}mb Temp Change (°C) - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f'Temperature Change (°C)'
        plot_wind_barbs(ax, wrf_file, timestep, lons, lats, level)
    else:
        contour = ax.contourf(to_np(lons), to_np(lats), to_np(data_copy), cmap='coolwarm')
        ax.set_title(f"Unconfigured product: {data.description} - Hour {timestep}\nValid: {forecast_time} - Init: {forecast_times[0]}")
        label = f"{data.description}"
    cbar = fig.colorbar(contour, ax=ax, orientation="vertical", fraction=0.035, pad=0.02)
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'))
    # counties are very intensive to process, so you should leave it off
    ax.add_feature(USCOUNTIES.with_scale('20m'), alpha=0.05)
    if product != ("cloudcover"):
        try:
            west, east, north, south = extent
            for airport, (lat, lon) in airports.items():
                if not (west <= lon <= east and south <= lat <= north):
                    continue
                idx_x, idx_y = ll_to_xy(wrf_file, lat, lon)
                value = to_np(data_copy)[idx_y, idx_x]
                ax.text(lon, lat, f"{value:.1f}",
                        color='black', fontsize=14,
                        ha='center', va='bottom')
        except:
            try:
                for airport, (lat, lon) in airports.items():
                    idx_x, idx_y = ll_to_xy(wrf_file, lat, lon)
                    value = to_np(data_copy)[idx_y, idx_x]
                    ax.text(lon, lat, f"{value:.1f}",
                            color='black', fontsize=12,
                            ha='center', va='bottom')
            except:
                pass
    if product != ("cloudcover"):
        maxmin = ""
        max_value = to_np(data_copy).max()
        min_value = to_np(data_copy).min()
        if max_value != 0:
            maxmin += f"Max: {max_value:.1f}"
            if min_value != 0:
                maxmin += f"\nMin: {min_value:.1f}"
        ax.annotate(maxmin, xy=(0.98, 0.03), xycoords='axes fraction', fontsize=12, color='black', ha='right', va='bottom', bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
    fig.tight_layout()
    ax.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.01), xycoords='figure fraction', fontsize=8, color='black')
    ax.annotate(f"{(forecast_times[timestep] - dt.timedelta(hours=5))} EST", xy=(0.25, 1), xycoords='axes fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    if loc is None:
        fig.savefig(os.path.join(output_path, f"hour_{timestep}.png"), bbox_inches='tight', pad_inches=0.1)
    else:
        fig.savefig(os.path.join(output_path, f"hour_{timestep}_{loc}.png"), bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    print(f'-> {product} hr {timestep} with {extent}')

def plot_wind_barbs(ax, wrf_file, timestep, lons, lats, pressure_level=None):
    if pressure_level:
        u = getvar(wrf_file, "ua", timeidx=timestep)
        v = getvar(wrf_file, "va", timeidx=timestep)
        pressure = getvar(wrf_file, "pressure", timeidx=timestep)
        u_interp = interplevel(u, pressure, pressure_level)
        v_interp = interplevel(v, pressure, pressure_level)
    else:
        u_interp = getvar(wrf_file, "U10", timeidx=timestep)
        v_interp = getvar(wrf_file, "V10", timeidx=timestep)
    stride = 50
    ax.barbs(to_np(lons[::stride, ::stride]), to_np(lats[::stride, ::stride]), 
             to_np(u_interp[::stride, ::stride]), to_np(v_interp[::stride, ::stride]),
             length=6, color='black', pivot='middle', 
             barb_increments={'half': 2.57222, 'full': 5.14444, 'flag': 25.7222})

def plot_streamlines(ax, wrf_file, timestep, lons, lats, pressure_level=None):
    if pressure_level:
        u = getvar(wrf_file, "ua", timeidx=timestep)
        v = getvar(wrf_file, "va", timeidx=timestep)
        pressure = getvar(wrf_file, "pressure", timeidx=timestep)
        u_interp = interplevel(u, pressure, pressure_level)
        v_interp = interplevel(v, pressure, pressure_level)
    else:
        u_interp = getvar(wrf_file, "U10", timeidx=timestep)
        v_interp = getvar(wrf_file, "V10", timeidx=timestep)
    ds = 4
    lon2 = to_np(lons)[::ds, ::ds]
    lat2 = to_np(lats)[::ds, ::ds]
    u2 = to_np(u_interp)[::ds, ::ds]
    v2 = to_np(v_interp)[::ds, ::ds]
    ax.streamplot(lon2, lat2, u2, v2, density=0.75, color='k', linewidth=1)