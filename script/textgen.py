# This module generates our text forecasts.

from wrf import getvar, to_np, ll_to_xy
import numpy as np

def get_text_data(wrf_file, airport, coords, hours, forecast_times, run_time):
    forecast_time = forecast_times[1].strftime("%Y-%m-%d %H:%M UTC")
    x, y = ll_to_xy(wrf_file, coords[0], coords[1])
    output_lines = []
    output_lines.append(f"UGA-WRF {run_time} - Init: {forecast_times[0]} - Text Forecast for {airport.upper()}")
    output_lines.append(f"Forecast Start Time: {forecast_time}")
    output_lines.append(f"UTC (Fcst) Hr | Temp | Dewp | Wind | Pressure")
    for t in range(1, hours + 1):
        t_data = getvar(wrf_file, "T2", timeidx=t)[y, x].values
        td_data = getvar(wrf_file, "td2", timeidx=t)[y, x].values
        u_data = getvar(wrf_file, "U10", timeidx=t)[y, x].values
        v_data = getvar(wrf_file, "V10", timeidx=t)[y, x].values
        wind_speed = np.sqrt(u_data**2 + v_data**2)
        wspd_data = to_np(wind_speed) * 2.23694
        pressure_data = getvar(wrf_file, "AFWA_MSLP", timeidx=t)[y, x].values
        t_f = (t_data - 273.15) * 9/5 + 32
        td = td_data * 9/5 + 32
        wspd = to_np(wspd_data)
        pressure_mb = to_np(pressure_data) / 100
        output_lines.append(f"{forecast_times[t].strftime('%H UTC')} ({str(t).zfill(2)}) | {t_f:.1f} F | {td:.1f} F | {wspd:.1f} mph | {pressure_mb:.1f} mb")
    return output_lines