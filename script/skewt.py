# This module generates our upper air charts.

from wrf import getvar
from metpy.plots import SkewT, Hodograph
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from metpy.units import units
import matplotlib.gridspec as gridspec
import os
import metpy.calc as mpcalc
import numpy as np
import datetime as dt

def plot_skewt(data, x_y, timestep, airport, output_path, forecast_times, run_time):
    forecast_time = forecast_times[timestep].strftime("%Y-%m-%d %H:%M UTC")
    p1 = getvar(data,"pressure",timeidx=timestep)
    T1 = getvar(data,"tc",timeidx=timestep)
    Td1 = getvar(data,"td",timeidx=timestep)
    u1 = getvar(data,"ua",timeidx=timestep)
    v1 = getvar(data,"va",timeidx=timestep)
    p = p1[:, x_y[0], x_y[1]] * units.hPa
    T = T1[:, x_y[0], x_y[1]] * units.degC
    Td = Td1[:, x_y[0], x_y[1]] * units.degC
    u = u1[:,x_y[0],x_y[1]] * units.knots
    v = v1[:,x_y[0],x_y[1]] * units.knots
    p_q  = p.metpy.unit_array
    T_q  = T.metpy.unit_array
    Td_q = Td.metpy.unit_array
    u_q  = u.metpy.unit_array
    v_q  = v.metpy.unit_array
    fig = plt.figure(figsize=(10, 8))
    gs = gridspec.GridSpec(3, 3)
    skew = SkewT(fig, subplot=gs[:, :2])
    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    T_surf = T[0]
    Td_surf = Td[0]
    p_surf = p[0]
    Ts_val = T_surf.values
    Tds_val = Td_surf.values
    ps_val = p_surf.values
    skew.ax.scatter([Ts_val, Tds_val], [ps_val, ps_val], marker='o', s=30, color=['r','g'], zorder=10)
    skew.ax.text(Ts_val + 10, ps_val, f"{Ts_val:.1f}°C", color='r', fontsize=10, fontweight="bold", path_effects=[path_effects.withStroke(linewidth=3, foreground="black")], ha='right', va='bottom')
    skew.ax.text(Tds_val - 10, ps_val, f"{Tds_val:.1f}°C", color='g', fontsize=10, fontweight="bold", path_effects=[path_effects.withStroke(linewidth=3, foreground="black")], ha='left', va='bottom')
    skew.plot_barbs(p, u, v)
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()
    skew.ax.axvline(0, color='k', ls='--')
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')
    prof = (mpcalc.parcel_profile(p, T[0], Td[0])).metpy.convert_units('degC')
    skew.plot(p_q, T_q, 'r')
    skew.plot(p_q, Td_q, 'g')
    skew.plot_barbs(p_q, u_q, v_q)
    skew.shade_cape(p_q, T_q, Td_q)
    lcl_p, lcl_T = mpcalc.lcl(p_q[0], T_q[0], Td_q[0])
    lfc_p, lfc_T = mpcalc.lfc(p_q, T_q, Td_q)
    skew.plot(lcl_p, lcl_T, marker='o', color='k', markerfacecolor='k', label='LCL')
    skew.plot(lfc_p, lfc_T, marker='o', color='k', markerfacecolor='white', label='LFC')
    skew.ax.text(lcl_T.magnitude + 1, lcl_p.magnitude, "LCL", ha="left", va="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))
    skew.ax.text(lfc_T.magnitude + 1, lfc_p.magnitude, "LFC", ha="left", va="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))
    skew.plot(p, prof, 'k', linewidth=2)
    skew.ax.set_xlim(-50, 40)
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlabel('Temperature ($^\circ$C)')
    skew.ax.set_ylabel('Pressure (hPa)')
    skew.ax.set_title(f"Skew-T Log-P")
    ax = fig.add_subplot(gs[0, 2])
    # this hodograph was adapted from the one on https://unidata.github.io/MetPy/latest/examples/Advanced_Sounding_With_Complex_Layout.html
    z1 = getvar(data, "z", timeidx=timestep)
    z = z1[:, x_y[0], x_y[1]] / 1000 
    h = Hodograph(ax, component_range=80.)
    h.add_grid(increment=20, ls='-', lw=1.5, alpha=0.5)
    h.add_grid(increment=10, ls='--', lw=1, alpha=0.2)
    h.ax.set_box_aspect(1)
    h.ax.set_yticklabels([])
    h.ax.set_xticklabels([])
    h.ax.set_xticks([])
    h.ax.set_yticks([])
    h.ax.set_xlabel(' ')
    h.ax.set_ylabel(' ')
    plt.xticks(np.arange(0, 0, 1))
    plt.yticks(np.arange(0, 0, 1))
    for i in range(10, 120, 20):
        h.ax.annotate(str(i), (i, 0), xytext=(0, 2), textcoords='offset pixels',
                    clip_on=True, fontsize=10, weight='bold', alpha=0.3, zorder=0)
    for i in range(10, 120, 20):
        h.ax.annotate(str(i), (0, i), xytext=(0, 2), textcoords='offset pixels',
                    clip_on=True, fontsize=10, weight='bold', alpha=0.3, zorder=0)
    for i in range(1, 13):
        idx = (np.abs(z - i)).argmin().item()
        u_km = u[idx].values
        v_km = v[idx].values
        h.ax.text(u_km, v_km, f"{i}", color="w", fontsize=8, path_effects=[path_effects.withStroke(linewidth=1, foreground="black")], ha='center', va='center', zorder=10)
    h.plot(u, v)
    h.plot_colormapped(u, v, c=p, label='0-12km WIND')
    ax.set_title('Hodograph')
    fig.suptitle(f"Upper Air Data for {airport.upper()} - Hour {timestep} - Valid: {forecast_time} - Init: {forecast_times[0]}")
    gs.tight_layout(fig)
    plt.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.01), xycoords='figure fraction', fontsize=8, color='black')
    plt.annotate(f"{(forecast_times[timestep] - dt.timedelta(hours=5))} EST", xy=(0.5, 0.95), xycoords='figure fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, f"hour_{timestep}.png"), bbox_inches='tight')
    plt.close()