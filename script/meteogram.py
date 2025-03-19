import matplotlib.pyplot as plt
from wrf import getvar, ll_to_xy, to_np
import numpy as np
import metpy.calc as mpcalc
from metpy.units import units
import os

def plot_meteogram(wrf_file, airport, coords, output_path, forecast_times, wrfhours, run_time):
    x, y = ll_to_xy(wrf_file, coords[0], coords[1])
    hours = np.arange(1, wrfhours + 1)
    times = [forecast_times[t].strftime('%H UTC') for t in hours]
    u_wind = [to_np(getvar(wrf_file, "U10", timeidx=t)[y, x]) for t in hours]
    v_wind = [to_np(getvar(wrf_file, "V10", timeidx=t)[y, x]) for t in hours]
    temperatures = []
    dewpoints = []
    wind_speeds = []
    pressures = []
    precipitations = []
    for t in hours:
        t_data = getvar(wrf_file, "T2", timeidx=t)[y, x].values
        q_data = getvar(wrf_file, "Q2", timeidx=t)[y, x].values
        wspd_data = getvar(wrf_file, "WSPD10MAX", timeidx=t)[y, x].values
        pressure_data = getvar(wrf_file, "AFWA_MSLP", timeidx=t)[y, x].values
        precip_data = getvar(wrf_file, "RAINC", timeidx=t)[y, x].values
        t_f = (t_data - 273.15) * 9/5 + 32
        td = mpcalc.dewpoint(mpcalc.vapor_pressure(getvar(wrf_file, 'PSFC', timeidx=t) / 100 * units.mbar, q_data))
        td_f = to_np(td)[y, x].magnitude * 9/5 + 32
        wspd = to_np(wspd_data) * 2.23694
        pressure_mb = to_np(pressure_data) / 100
        precip = to_np(precip_data) * 0.0393701 
        temperatures.append(t_f)
        dewpoints.append(td_f)
        wind_speeds.append(wspd)
        pressures.append(pressure_mb)
        precipitations.append(precip)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(hours, temperatures, color='red', label='Temperature (°F)')
    ax1.plot(hours, dewpoints, color='green', label='Dewpoint (°F)')
    ax1.barbs(hours, 10, u_wind, v_wind, length=6)
    ax1.set_ylabel('Temperature / Dewpoint (°F)')
    ax1.set_xlabel('Forecast Hour')
    ax1.set_xticks(hours)
    ax1.set_xticklabels(times, rotation=45)
    ax2 = ax1.twinx()
    ax2.plot(hours, pressures, color='blue', label='Pressure (mb)')
    ax2.set_ylabel('Pressure (mb)')
    ax3 = ax1.twinx()
    ax3.bar(hours, precipitations, color='dodgerblue', alpha=0.4, label='Precipitation (in)')
    ax3.set_ylabel('Precipitation (in)')
    ax3.spines['right'].set_position(('outward', 60))
    fig.legend(loc="lower right")
    plt.title(f"UGA-WRF Meteogram for {airport.upper()} starting at {forecast_times[1]} UTC")
    plt.grid(True)
    plt.tight_layout()
    plt.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.01), xycoords='figure fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, "meteogram.png"))
    plt.close()