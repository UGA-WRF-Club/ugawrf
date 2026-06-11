# This module generates our meteograms.

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from wrf import getvar, ll_to_xy, to_np
import numpy as np
import os


def plot_meteogram(wrf_file, airport, coords, output_path, forecast_times, wrfhours, run_time):
    x, y = ll_to_xy(wrf_file, coords[0], coords[1])
    hours = np.arange(1, wrfhours)
    times = [forecast_times[t].strftime('%H') for t in hours]
    u_wind = [to_np(getvar(wrf_file, "U10", timeidx=t)[y, x]) for t in hours]
    v_wind = [to_np(getvar(wrf_file, "V10", timeidx=t)[y, x]) for t in hours]
    temperatures = []
    dewpoints = []
    pressures = []
    for t in hours:
        t_data = getvar(wrf_file, "T2", timeidx=t)[y, x].values
        td_data = getvar(wrf_file, "td2", timeidx=t)[y, x].values
        pressure_data = getvar(wrf_file, "AFWA_MSLP", timeidx=t)[y, x].values
        t_f = (t_data - 273.15) * 9/5 + 32
        td_f = to_np(td_data) * 9/5 + 32
        pressure_mb = to_np(pressure_data) / 100
        temperatures.append(t_f)
        dewpoints.append(td_f)
        pressures.append(pressure_mb)
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(hours, temperatures, color='red', label='Temp (°F)')
    ax1.plot(hours, dewpoints, color='green', label='Dewp (°F)')
    if any(t <= 32 for t in temperatures):
        ax1.axhline(
            y=32,
            color='blue',
            linestyle='--',
            linewidth=1.5,
            label='Frz (32°F)'
        )
    ax1.barbs(hours, ax1.get_ylim()[0] * 1.07, u_wind, v_wind, length=6, barb_increments={'half': 2.57222, 'full': 5.14444, 'flag': 25.7222}) 
    ax1.set_ylabel('Temperature / Dewpoint (°F)')
    ax1.set_xlabel('Hour (UTC)') 
    ax1.set_xticks(hours)
    ax1.set_xticklabels(times, rotation=45)
    # will turn this into an actual function later, but just implementing first pass
    # holy cow this looks so bad
    start1, end1 = 1, 24
    maxtemp_x_24 = np.argmax(temperatures[start1:end1]) + start1
    mintemp_x_24 = np.argmin(temperatures[start1:end1]) + start1
    maxdew_x_24 = np.argmax(dewpoints[start1:end1]) + start1
    mindew_x_24 = np.argmin(dewpoints[start1:end1]) + start1
    max_temp_24 = temperatures[maxtemp_x_24]
    min_temp_24 = temperatures[mintemp_x_24]
    max_dew_24 = dewpoints[maxdew_x_24]
    min_dew_24 = dewpoints[mindew_x_24] 
    ax1.annotate(f"{max_temp_24:.1f} F", xy=(maxtemp_x_24, max_temp_24), xytext=(maxtemp_x_24 + 1, max_temp_24), color='red', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax1.annotate(f"{min_temp_24:.1f} F", xy=(mintemp_x_24, min_temp_24), xytext=(mintemp_x_24 + 1, min_temp_24), color='red', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax1.annotate(f"{max_dew_24:.1f} F", xy=(maxdew_x_24, max_dew_24), xytext=(maxdew_x_24 + 1, max_dew_24), color='green', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax1.annotate(f"{min_dew_24:.1f} F", xy=(mindew_x_24, min_dew_24), xytext=(mindew_x_24 + 1, min_dew_24), color='green', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    start2, end2 = 24, 48
    maxtemp_x_48 = np.argmax(temperatures[start2:end2]) + start2
    mintemp_x_48 = np.argmin(temperatures[start2:end2]) + start2 
    maxdew_x_48 = np.argmax(dewpoints[start2:end2]) + start2 
    mindew_x_48 = np.argmin(dewpoints[start2:end2]) + start2
    max_temp_48 = temperatures[maxtemp_x_48]
    min_temp_48 = temperatures[mintemp_x_48]
    max_dew_48 = dewpoints[maxdew_x_48]
    min_dew_48 = dewpoints[mindew_x_48]
    ax1.annotate(f"{max_temp_48:.1f} F", xy=(maxtemp_x_48, max_temp_48), xytext=(maxtemp_x_48 + 1, max_temp_48), color='red', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax1.annotate(f"{min_temp_48:.1f} F", xy=(mintemp_x_48, min_temp_48), xytext=(mintemp_x_48 + 1, min_temp_48), color='red', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax1.annotate(f"{max_dew_48:.1f} F", xy=(maxdew_x_48, max_dew_48), xytext=(maxdew_x_48 + 1, max_dew_48), color='green', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax1.annotate(f"{min_dew_48:.1f} F", xy=(mindew_x_48, min_dew_48), xytext=(mindew_x_48 + 1, min_dew_48), color='green', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax2 = ax1.twinx()
    ax2.plot(hours, pressures, color='blue', label='Pressure (mb)')
    ax2.set_ylabel('MSLP (mb)')
    maxpressure_x_24 = np.argmax(pressures[start1:end1]) + start1
    minpressure_x_24 = np.argmin(pressures[start1:end1]) + start1
    max_pressure_24 = pressures[maxpressure_x_24]
    min_pressure_24 = pressures[minpressure_x_24]
    ax2.annotate(f"{max_pressure_24:.1f} mb", xy=(maxpressure_x_24, max_pressure_24), xytext=(maxpressure_x_24 + 1, max_pressure_24), color='blue', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax2.annotate(f"{min_pressure_24:.1f} mb", xy=(minpressure_x_24, min_pressure_24), xytext=(minpressure_x_24 + 1, min_pressure_24), color='blue', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    maxpressure_x_48 = np.argmax(pressures[start2:end2]) + start2
    minpressure_x_48 = np.argmin(pressures[start2:end2]) + start2
    max_pressure_48 = pressures[maxpressure_x_48]
    min_pressure_48 = pressures[minpressure_x_48]
    ax2.annotate(f"{max_pressure_48:.1f} mb", xy=(maxpressure_x_48, max_pressure_48), xytext=(maxpressure_x_48 + 1, max_pressure_48), color='blue', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax2.annotate(f"{min_pressure_48:.1f} mb", xy=(minpressure_x_48, min_pressure_48), xytext=(minpressure_x_48 + 1, min_pressure_48), color='blue', fontsize=14, ha='center', path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],)
    ax2.axvline(x=24, color='black', linestyle='--', linewidth=0.5, label='FHR24')
    lines_ax1, labels_ax1 = ax1.get_legend_handles_labels()
    lines_ax2, labels_ax2 = ax2.get_legend_handles_labels()
    all_lines = lines_ax1 + lines_ax2
    all_labels = labels_ax1 + labels_ax2
    ax1.legend(all_lines, all_labels, loc="upper left", fancybox=True, framealpha=0.2, fontsize='small')
    ax2.legend(all_lines, all_labels, loc="upper left", fancybox=True, framealpha=0.2, fontsize='small')
    plt.title(f"UGA-WRF Meteogram - {airport.upper()} - Init: {forecast_times[0]}\nStarting at {forecast_times[1]} UTC", fontweight='bold', loc='left')
    plt.grid(True)
    plt.tight_layout()
    plt.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.01), xycoords='figure fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, "meteogram.png"))
    plt.close()
