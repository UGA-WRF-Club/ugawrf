# This module generates our text forecasts.

from wrf import getvar, to_np, ll_to_xy
from metpy.units import units
import metpy.calc as mpcalc

def get_text_data(wrf_file, airport, coords, hours, forecast_times, run_time):
    forecast_time = forecast_times[0].strftime("%Y-%m-%d %H:%M UTC")
    x, y = ll_to_xy(wrf_file, coords[0], coords[1])
    output_lines = []
    output_lines.append(f"UGA-WRF Run {run_time} - Text Forecast for {airport.upper()}")
    output_lines.append(f"Forecast Start Time: {forecast_time}")
    output_lines.append(f"UTC (Fcst) Hr | Temp | Dewp | Wind | Pressure")
    for t in range(1, hours + 1):
        t_data = getvar(wrf_file, "T2", timeidx=t)[y, x].values
        q_data = getvar(wrf_file, "Q2", timeidx=t)[y, x].values
        wspd_data = getvar(wrf_file, "WSPD10MAX", timeidx=t)[y, x].values
        pressure_data = getvar(wrf_file, "AFWA_MSLP", timeidx=t)[y, x].values
        t_f = (t_data - 273.15) * 9/5 + 32
        e = mpcalc.vapor_pressure(pressure_data / 100 * units.mbar, q_data)
        td = (mpcalc.dewpoint(e).to(units.degF)).magnitude
        wspd = to_np(wspd_data) * 2.23694
        pressure_mb = to_np(pressure_data) / 100

        output_lines.append(f"{forecast_times[t].strftime('%H UTC')} ({str(t).zfill(2)}) | {t_f:.1f} F | {td:.1f} F | {wspd:.1f} mph | {pressure_mb:.1f} mb")
    return output_lines