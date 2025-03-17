import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import colors
from netCDF4 import Dataset
from wrf import getvar, to_np, latlon_coords, extract_times, ll_to_xy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from datetime import datetime, timedelta
from metpy.plots import ctables, SkewT, Hodograph
import metpy.calc as mpcalc
from metpy.units import units

print("UGA-WRF Data Processing Program")
start_time = datetime.now()

airports = {
    "ahn": (33.95167820706025, -83.32489875559355),
    "cni": (34.30887599509864, -84.4273590802223),
    "atl": (33.6391621022899, -84.43061412634862),
    "ffc": (33.358755552804176, -84.5711101702346),
    "mcn": (32.70076950826015, -83.64790511895201),
    "rmg": (34.35267229676656, -85.16328449820841),
    "csg": (32.51571975545047, -84.9392150850212)
} # locations to plot skewts, text products
hours = 24 # set to however many hours this wrf runs out to

BASE_OUTPUT = "D:/ugawrf/site/runs"
WRF_FILE = "D:/ugawrf/image/wrfout_d01_2025-03-13_21_00_00"
PRODUCTS = {
    "temperature": "T2",
    "dewp": "Q2",
    "wind": "WSPD10MAX",
    "comp_reflectivity": "REFD_COM",
    "pressure": "AFWA_MSLP",
    "cape": "AFWA_CAPE",
    "cape_mu": "AFWA_CAPE_MU",
    "cin": "AFWA_CIN",
    "cin_mu": "AFWA_CIN_MU",
    "helicity": "UP_HELI_MAX",
    "total_precip": "AFWA_TOTPRECIP",
    "snowfall": "SNOWNC",
    "echo_tops": "ECHOTOP",
} # these are the products for the map only to output


wrf_file = Dataset(WRF_FILE)
run_time = str(wrf_file.START_DATE).replace(":", "_")

print(f"processing data for run {run_time}")

def convert_time(nc_time):
    return np.datetime64(nc_time).astype('datetime64[s]').astype(datetime)
forecast_times = [convert_time(t) for t in extract_times(wrf_file, timeidx=None)]
# processing starts here

# text data
def get_text_data(wrf_file, airport, coords):
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

text_start_time = datetime.now()
for airport, coords in airports.items():
    try:
        text_time = datetime.now()
        text_data = get_text_data(wrf_file, airport, coords)
        output_path = os.path.join(BASE_OUTPUT, run_time, "text", airport)
        os.makedirs(output_path, exist_ok=True)
        with open(os.path.join(output_path, "forecast.txt"), 'w') as f:
            for line in text_data:
                f.write(f"{line}\n")
        print(f"processed {airport} text data in {datetime.now() - text_time}")
    except Exception as e:
        print(f"error processing {airport} text: {e}!")
print(f'texts processed successfuly - took {datetime.now() - text_start_time}')

map_time = datetime.now()
def plot_variable(data, timestep, output_path):
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
    ax.annotate(f"{(forecast_times[timestep] - timedelta(hours=4))} EST", xy=(0.75, 1), xycoords='axes fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, f"hour_{timestep}.png"))
    plt.close()
for product, variable in PRODUCTS.items():
    try:
        product_time = datetime.now()
        output_path = os.path.join(BASE_OUTPUT, run_time, product)
        for t in range(0, hours + 1):
            data = getvar(wrf_file, variable, timeidx=t)
            plot_variable(data, t, output_path)
        print(f"processed {product} in {datetime.now() - product_time}")
    except Exception as e:
        print(f"error processing {product}: {e}! last timestep: {t}")
print(f"graphics processed successfully - took {datetime.now() - map_time}")

# upper air plots
skewt_plot_time = datetime.now()
def plot_skewt(data, x_y, timestep, airport, output_path):
    forecast_time = forecast_times[timestep].strftime("%Y-%m-%d %H:%M UTC")
    p1 = getvar(data,"pressure",timeidx=timestep)
    T1 = getvar(data,"tc",timeidx=timestep)
    Td1 = getvar(data,"td",timeidx=timestep)
    u1 = getvar(data,"ua",timeidx=timestep)
    v1 = getvar(data,"va",timeidx=timestep)
    p = p1[:,x_y[0],x_y[1]] * units.hPa
    T = T1[:,x_y[0],x_y[1]] * units.degC
    Td = Td1[:,x_y[0],x_y[1]] * units.degC
    u = u1[:,x_y[0],x_y[1]] * units('m/s')
    v = v1[:,x_y[0],x_y[1]] * units('m/s')
    fig = plt.figure(figsize=(7, 7))
    gs = gridspec.GridSpec(3, 3)
    skew = SkewT(fig, subplot=gs[:, :2])
    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    skew.plot_barbs(p, u, v)
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()
    skew.ax.set_xlim(-50, 40)
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlabel('Temperature ($^\circ$C)')
    skew.ax.set_ylabel('Pressure (hPa)')
    skew.ax.set_title(f"Skew-T Log-P")
    ax = fig.add_subplot(gs[0, 2])
    h = Hodograph(ax, component_range=80.)
    h.add_grid(increment=20)
    h.plot(u, v)
    ax.set_title('Hodograph')
    fig.suptitle(f"Upper Air Data for {airport.upper()} - Hour {timestep} - Valid: {forecast_time}")
    os.makedirs(output_path, exist_ok=True)
    plt.tight_layout()
    plt.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.01), xycoords='figure fraction', fontsize=8, color='black')
    plt.annotate(f"{(forecast_times[timestep] - timedelta(hours=4))} EST", xy=(0.75, 0.95), xycoords='figure fraction', fontsize=8, color='black')
    plt.savefig(os.path.join(output_path, f"hour_{timestep}.png"))
    plt.close()
for airport, coords in airports.items():
    try:
        skewt_time = datetime.now()
        x_y = ll_to_xy(wrf_file, coords[0], coords[1])
        output_path = os.path.join(BASE_OUTPUT, run_time, "skewt", airport)
        for t in range(0, hours + 1):
            plot_skewt(wrf_file, x_y, t, airport, output_path)
        print(f"processed {airport} skewt in {datetime.now() - skewt_time}")
    except Exception as e:
        print(f"error processing {airport} skewt: {e}! last timestep: {t}")
print(f"skewt processed successfully - took {datetime.now() - skewt_plot_time}")

process_time = datetime.now() - start_time
print(f"data processed successfully, this is run {run_time} - took {process_time}")
