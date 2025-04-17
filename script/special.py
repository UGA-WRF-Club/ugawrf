# This module is intended for special operations that require one-time code - such as 4-panel cloud cover.

from wrf import getvar, to_np, latlon_coords, ll_to_xy
import matplotlib.pyplot as plt
import datetime as dt
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def hr24_change(output_path, airports, hours, forecast_times, run_time, wrf_file):
    temp_24 = getvar(wrf_file, "T2", timeidx=hours)
    temp_now = getvar(wrf_file, "T2", timeidx=0)
    hr24_change = (temp_24 - temp_now) * 9/5
    plt.figure(figsize=(8, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    lats, lons = latlon_coords(hr24_change)
    contour = plt.contourf(to_np(lons), to_np(lats), to_np(hr24_change), cmap="coolwarm", vmin=-35, vmax=35)
    try:
        for airport, coords in airports.items():
                lat, lon = coords
                idx_x, idx_y = ll_to_xy(wrf_file, lat, lon)
                value = to_np(hr24_change)[idx_y, idx_x]
                ax.text(lon, lat, f"{value:.2f}", color='black', fontsize=8, ha='center', va='bottom')
    except:
        pass
    maxmin = ""
    max_value = to_np(hr24_change).max()
    min_value = to_np(hr24_change).min()
    if max_value != 0:
        maxmin += f"Max: {max_value:.2f}"
        if min_value != 0:
            maxmin += f"\nMin: {min_value:.2f}"
    ax.annotate(maxmin, xy=(0.98, 0.03), xycoords='axes fraction', fontsize=8, color='black', ha='right', va='bottom', bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
    ax.set_title(f"{hours} Hour 2m Temp Change (°F) - Hour {hours}\nValid: {forecast_times[hours]} - Init: {forecast_times[0]}")
    plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.05, label='Temperature Change (°F)')
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale('50m'))
    plt.tight_layout()
    ax.annotate(f"{(forecast_times[hours] - dt.timedelta(hours=5))} EST", xy=(0.25, 1), xycoords='axes fraction', fontsize=8, color='black')
    ax.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.02), xycoords='figure fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, f"24hr_change.png"))
    plt.close()
    
def generate_cloud_cover(t, output_path, forecast_times, run_time, wrf_file):
    forecast_time = forecast_times[t].strftime("%Y-%m-%d %H:%M UTC")
    cloud_fracs = getvar(wrf_file, "cloudfrac", timeidx=t)
    low_cloud_frac = to_np(cloud_fracs[0]) * 100 
    mid_cloud_frac = to_np(cloud_fracs[1]) * 100
    high_cloud_frac = to_np(cloud_fracs[2]) * 100
    total_cloud_frac = low_cloud_frac + mid_cloud_frac + high_cloud_frac
    lats, lons = latlon_coords(cloud_fracs)
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    cloud_data = [total_cloud_frac, low_cloud_frac, mid_cloud_frac, high_cloud_frac]
    titles = ["Total Cloud Cover (%)", "Low (%)", "Mid (%)", "High (%)"]
    for ax, data, title in zip(axes.flat, cloud_data, titles):
        ax.set_title(title)
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linewidth=0.5)
        ax.add_feature(cfeature.STATES, linewidth=0.5)
        cf = ax.pcolormesh(to_np(lons), to_np(lats), data, cmap="Blues_r", norm=plt.Normalize(0, 100), transform=ccrs.PlateCarree())
    cbar = plt.colorbar(cf, ax=axes[:,:], orientation='horizontal', pad=0.05)
    cbar.set_label("Cloud Cover (%)")
    plt.suptitle(f"Cloud Cover - Hour {t}\nValid: {forecast_time} - Init: {forecast_times[0]}")
    plt.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.01), xycoords='figure fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, f"hour_{t}.png"))
    plt.close(fig)