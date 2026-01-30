from wrf import getvar, to_np, ll_to_xy
import csv

def generate_model_stats(wrf_file, airport, coords, hours, forecast_times, run_time, output_path):
    x, y = ll_to_xy(wrf_file, coords[0], coords[1])
    stats_data = []
    for t in range(1, hours):
        t_data = getvar(wrf_file, "T2", timeidx=t)[y, x].values
        td_data = getvar(wrf_file, "td2", timeidx=t)[y, x].values
        wspd_data = getvar(wrf_file, "wspd_wdir10", timeidx=t, units="mph")
        pressure_data = getvar(wrf_file, "AFWA_MSLP", timeidx=t)[y, x].values
        t_f = (t_data - 273.15) * 9/5 + 32
        td = td_data * 9/5 + 32
        wspd = to_np(wspd_data[0][y, x])
        wdir = to_np(wspd_data[1][y, x])
        pressure_mb = to_np(pressure_data) / 100
        stats_data.append({
            'Init Time (UTC)': forecast_times[0].strftime('%Y-%m-%d %H:%M'),
            'Airport': airport.upper(),
            'Forecast Hour': t,
            'Valid Time (UTC)': forecast_times[t].strftime('%Y-%m-%d %H:%M'),
            'Temperature (F)': f"{t_f:.2f}",
            'Dew Point (F)': f"{td:.2f}",
            'Wind Speed (mph)': f"{wspd:.2f}",
            'Wind Direction (deg)': f"{wdir:.2f}",
            'Pressure (mb)': f"{pressure_mb:.2f}"
        })
    keys = stats_data[0].keys()
    with open(f"{output_path}/{airport}_model_stats_{run_time}.csv", 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(stats_data)