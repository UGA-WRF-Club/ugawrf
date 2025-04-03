# This module is intended for special operations that require one-time code - such as 4-panel cloud cover.

from wrf import getvar, to_np, latlon_coords
import matplotlib.pyplot as plt
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def generate_cloud_cover(t, output_path, forecast_times, run_time, wrf_file):
    forecast_time = forecast_times[t].strftime("%Y-%m-%d %H:%M UTC")
    cloud_fracs = getvar(wrf_file, "cloudfrac", timeidx=t)
    low_cloud_frac = to_np(cloud_fracs[0]) * 100 
    mid_cloud_frac = to_np(cloud_fracs[1]) * 100
    high_cloud_frac = to_np(cloud_fracs[2]) * 100
    total_cloud_frac = low_cloud_frac + mid_cloud_frac + high_cloud_frac
    lats, lons = latlon_coords(cloud_fracs)
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10), subplot_kw={'projection': ccrs.PlateCarree()})
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
    plt.savefig(os.path.join(output_path, f"hour_{t}.png"))
    plt.close(fig)