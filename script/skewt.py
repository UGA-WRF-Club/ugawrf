# This module generates our upper air charts.

from wrf import getvar
from metpy.plots import SkewT, Hodograph
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from metpy.units import units
import matplotlib.gridspec as gridspec
import os
import metpy.calc as mpcalc
import numpy as np
import datetime as dt
from adjustText import adjust_text


def plot_skewt_dep(data, x_y, timestep, airport, output_path, forecast_times, init_dt, init_str, run_time):
    # old skewt code, to be removed in future push
    valid_time = forecast_times[timestep]
    f_hour = int(round((valid_time - init_dt).total_seconds() / 3600))
    valid_time_str = valid_time.strftime("%Y-%m-%d %H:%M UTC")
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
    gs = gridspec.GridSpec(3, 3, figure=fig, wspace=0, hspace=0)
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
    skew.ax.text(Ts_val + 15, ps_val, f"{Ts_val:.1f}°C", color='r', fontsize=16, fontweight="bold", path_effects=[path_effects.withStroke(linewidth=3, foreground="black")], ha='right', va='bottom')
    skew.ax.text(Tds_val - 15, ps_val, f"{Tds_val:.1f}°C", color='g', fontsize=16, fontweight="bold", path_effects=[path_effects.withStroke(linewidth=3, foreground="black")], ha='left', va='bottom')
    skew.plot_barbs(p, u, v)
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()
    skew.ax.axvline(0, color='k', ls='--')
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')
    prof = (mpcalc.parcel_profile(p, T[0], Td[0])).metpy.convert_units('degC')
    prof_q = prof.metpy.unit_array
    skew.plot(p_q, T_q, 'r')
    skew.plot(p_q, Td_q, 'g')
    skew.plot_barbs(p_q, u_q, v_q)
    skew.shade_cape(p_q, T_q, prof_q)
    lcl_p, lcl_T = mpcalc.lcl(p_q[0], T_q[0], Td_q[0])
    lfc_p, lfc_T = mpcalc.lfc(p_q, T_q, Td_q)
    skew.plot(lcl_p, lcl_T, marker='o', color='k', markerfacecolor='k', label='LCL')
    skew.plot(lfc_p, lfc_T, marker='o', color='k', markerfacecolor='white', label='LFC')
    skew.ax.text(lcl_T.magnitude + 1, lcl_p.magnitude, "LCL", ha="left", va="center", fontsize=14, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))
    skew.ax.text(lfc_T.magnitude + 1, lfc_p.magnitude, "LFC", ha="left", va="center", fontsize=14, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))
    skew.plot(p, prof, 'k', linewidth=2)
    skew.ax.set_xlim(-40, 40)
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
    texts = []
    for i in range(1, 13):
        idx = (np.abs(z - i)).argmin().item()
        u_km = u[idx].values
        v_km = v[idx].values
        texts.append(h.ax.text(u_km, v_km, f"{i}", color="w", fontsize=8,path_effects=[path_effects.withStroke(linewidth=1, foreground="black")], ha='center', va='center', zorder=10, alpha=0.4))
    h.plot(u, v)
    h.plot_colormapped(u, v, c=p, label='0-12km WIND')
    ax.set_title('Hodograph')
    ax.set_xlabel('U (knots)')
    ax.set_ylabel('V (knots)')
    mlcape, mlcin = mpcalc.mixed_layer_cape_cin(p_q, T_q, prof_q, depth=50 * units.hPa)
    mucape, mucin = mpcalc.most_unstable_cape_cin(p_q, T_q, Td_q, depth=50 * units.hPa)
    sbcape, sbcin = mpcalc.surface_based_cape_cin(p_q, T_q, Td_q)
    k_index = mpcalc.k_index(p_q, T_q, Td_q)
    total_totals = mpcalc.total_totals_index(p_q, T_q, Td_q)
    plt.figtext(0.83, 0.56, f"(parameters are work in progress)", ha="center", va="top", fontsize=10, color='red')
    plt.figtext(0.83, 0.50, f"MUCAPE: {mucape.magnitude:.1f} J/kg", ha="center", va="top", fontsize=12, color='black')
    plt.figtext(0.83, 0.48, f"MUCIN: {mucin.magnitude:.1f} J/kg", ha="center", va="top", fontsize=12, color='black')
    plt.figtext(0.83, 0.46, f"SBCAPE: {sbcape.magnitude:.1f} J/kg", ha="center", va="top", fontsize=12, color='black')
    plt.figtext(0.83, 0.44, f"SBCIN: {sbcin.magnitude:.1f} J/kg", ha="center", va="top", fontsize=12, color='black')
    plt.figtext(0.83, 0.42, f"K Index: {k_index.magnitude:.1f}", ha="center", va="top", fontsize=12, color='black')
    plt.figtext(0.83, 0.40, f"Total Totals: {total_totals.magnitude:.1f}", ha="center", va="top", fontsize=12, color='black')
    fig.subplots_adjust(top=0.9, right=1, left=0, bottom=0, wspace=0, hspace=0)
    fig.suptitle(f"Upper Air Data for {airport.upper()} - Hour {f_hour}\nValid: {valid_time_str} - Init: {init_str}", x=0.4, ha="center", va="top")
    plt.annotate(f"UGA-WRF Run {run_time}", xy=(0.01, 0.01), xycoords='figure fraction', fontsize=8, color='black')
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, f"hour_{f_hour}.png"), bbox_inches='tight')
    plt.close()
    fig_hod = plt.figure(figsize=(6, 6))
    ax_hod = fig_hod.add_subplot(1, 1, 1)
    h2 = Hodograph(ax_hod, component_range=80.)
    h2.add_grid(increment=20, ls='-', lw=1.5, alpha=0.5)
    h2.add_grid(increment=10, ls='--', lw=1, alpha=0.2)
    ax_hod.set_box_aspect(1)
    ax_hod.set_xticks([])
    ax_hod.set_yticks([])
    for i in range(10, 120, 20):
        ax_hod.annotate(str(i), (i, 0), xytext=(0, 2),
                        textcoords='offset pixels',
                        clip_on=True, fontsize=10,
                        weight='bold', alpha=0.3, zorder=0)
        ax_hod.annotate(str(i), (0, i), xytext=(0, 2), textcoords='offset pixels', clip_on=True, fontsize=10, weight='bold', alpha=0.3, zorder=0)
    texts = []
    for i in range(1, 13):
        idx = (np.abs(z - i)).argmin().item()
        u_km = u[idx].values
        v_km = v[idx].values
        texts.append(ax_hod.text(u_km, v_km, f"{i}", color="w", fontsize=15, path_effects=[path_effects.withStroke(linewidth=1, foreground="black")],ha='center', va='center', zorder=10, alpha=0.8))
    adjust_text(texts, ax=ax_hod, arrowprops=dict(arrowstyle='-', color='gray', lw=1), min_arrow_len=0.1)
    h2.plot(u, v, linewidth=2)
    h2.plot_colormapped(u, v, c=p, label='0-12 km wind')
    ax_hod.set_title(f"UGA-WRF Hodograph for {airport.upper()} - Hour {f_hour}\nValid: {valid_time_str} - Init: {init_str}")
    ax_hod.set_xlabel('U (knots)')
    ax_hod.set_ylabel('V (knots)')
    fig_hod.tight_layout()
    fig_hod.savefig(
    os.path.join(output_path, f"hodograph_hour_{f_hour}.png"),bbox_inches='tight')
    plt.close(fig_hod)

#Init_dt is the datetime objects and init_str is the string version of that object
#data = qrd file, x_y is the lat/lon for the airport
#forecast time is an array of dtatetime objects
def plot_skewt(data, x_y, timestep, airport, output_path, forecast_times, init_dt, init_str, run_time):

    #Defining forecast times:
    #timestep is obtainined through the for-loop in ugawrf
    valid_time = forecast_times[timestep]

    #inital time - forecast time to get the forecast hour
    f_hour = int(round((valid_time - init_dt).total_seconds() / 3600))

    #Obtains variables from the wrfout file
    raw_pressure = getvar(data, "pressure", timeidx = timestep)
    raw_temperatrue = getvar(data, "tc", timeidx = timestep)
    raw_dewpoint = getvar(data, "td", timeidx = timestep)
    raw_Xcomponent_windspeed = getvar(data, "ua", timeidx = timestep)
    raw_Ycomponent_winderspeed = getvar(data, "va", timeidx = timestep)
    raw_height = getvar(data, "z",timeidx = timestep)

    #What exactly does ":, x_y[0], x_y[1]" mean? 
    #Extract data (w.r.t to height) at a particular location + specifiy units 
    raw_pressure = raw_pressure[:, x_y[0], x_y[1]] * units.hPa
    raw_temperatrue = raw_temperatrue[:, x_y[0], x_y[1]] * units.degC
    raw_dewpoint = raw_dewpoint[:, x_y[0], x_y[1]] * units.degC
    raw_Xcomponent_windspeed = raw_Xcomponent_windspeed[:, x_y[0], x_y[1]] * units.knots
    raw_Ycomponent_winderspeed = raw_Ycomponent_winderspeed[:, x_y[0], x_y[1]] * units.knots
    raw_height = raw_height[:, x_y[0], x_y[1]] * units.meters

    #Reassigns the data into a unit array
    raw_pressure = raw_pressure.metpy.unit_array
    raw_temperatrue = raw_temperatrue.metpy.unit_array
    raw_dewpoint = raw_dewpoint.metpy.unit_array
    raw_Xcomponent_windspeed = raw_Xcomponent_windspeed.metpy.unit_array
    raw_Ycomponent_winderspeed = raw_Ycomponent_winderspeed.metpy.unit_array
    raw_height = raw_height.metpy.unit_array

    
    fig = plt.figure(figsize=(18, 12)) #Create a fig with certain size
    skew = SkewT(fig, rect=(0.05, 0.05, 0.5, 0.90)) #Create skewT with that fig and set the skewT bounds

    #Axises limits
    skew.ax.set_ylim(1000, 100) 
    skew.ax.set_xlim(-35, 45)

    #Label axis
    skew.ax.set_xlabel(str.upper("Temperature (°C)"), weight="bold")
    skew.ax.set_ylabel(str.upper("Pressure (hPa)"), weight="bold")

    #Set the background of the Skew T and figure to white
    fig.set_facecolor("#ffffff")
    skew.ax.set_facecolor("#ffffff")

    #Plot fundamental background lines
    #alpha: transparency of line, and lw: linewidth
    skew.plot_dry_adiabats(color="red", alpha=0.3, lw=1)
    skew.plot_moist_adiabats(color="blue", alpha=0.3, lw=1)
    skew.plot_mixing_lines(color="green", alpha=0.3, lw=1)
    skew.ax.axvline(0, linestyle="--", color="blue", alpha=0.5, label="0C isotherm") #Bold 0C isotherm
   
    #Plot the variables we derived from WRF, second parameter is color
    #Think of it as plotting temp/dew/ect w.r.t pressure
    skew.plot(raw_pressure, raw_temperatrue, "r", lw=4, label="Temperature")
    skew.plot(raw_pressure, raw_dewpoint, "g", lw=4, label="Dewpoint")

    #plot windbarbs
    #creates an log spaced array where each element is log-spaced; convert to hPa 
    interval = np.logspace(2, 3, 40) * units.hPa  #Why does it start at 2 and end at 3?
    #Retrieves the indicies from the data array that are closest to the indicies in the interval array
    idx = mpcalc.resample_nn_1d(raw_pressure, interval) 
    #inputs the necessary variables at the refined indicies defined above
    skew.plot_barbs(pressure=raw_pressure[idx], u=raw_Xcomponent_windspeed[idx], v=raw_Ycomponent_winderspeed[idx])


    #Calculate temperature and pressure at the LFC + LCL height
    lfc_p, lfc_t = mpcalc.lfc(raw_pressure, raw_temperatrue, raw_dewpoint)
    lcl_p, lcl_t = mpcalc.lcl(raw_pressure[0], raw_temperatrue[0], raw_dewpoint[0])

    #LFC will return nan if there is no LFC, from a meteologoical stand point
    #Marker: shape that will indicate the LCL/LFC, color: circle outline color
    #Markerfacecolor: color of inside the shape, in this case circle
    skew.plot(lfc_p, lfc_t, marker="o", color="k", markerfacecolor="k", label="lfc")
    skew.plot(lcl_p, lcl_t, "ko", markerfacecolor="white", label="lcl")

    #Want to plot lines represetning LCL, LFC, and EL way off to the right
    #In order to do that need to convert SkewT coords to x,y coords on the skewT itself
    #Then convert the coords from the skewT to relative coords to the whole fig
    temp_temp_array = [32, 38]
    temp_pressure_array = [lcl_p.m, lcl_p.m]
    
    skew.plot(temp_pressure_array, temp_temp_array, "black", label="LCL")
    
    test= ((2 * (raw_pressure[0].m - lcl_p.m))/np.sqrt(2)) + lcl_t.m
    #print(f"LCL_p: {lcl_p}.m, sfc_pressure: {raw_pressure[0].m}, LCL_t: {lcl_t.m}")
    test_2 = 0.006 * test
    #print(f"test: {test_2}")
    skew.ax.text(test_2, 0.5, "lcl if it actually worked", weight="bold", fontsize=20)

    #Calculate and plot parcel path, need to convert to C!
    parcel_path = mpcalc.parcel_profile(raw_pressure, raw_temperatrue[0], raw_dewpoint[0]).to('degC')
    skew.plot(raw_pressure, parcel_path, color="black", lw=2, label="Parcel path") #ls: linestyle, "--": dotted

    #Calculate cape then shade the cape/cin regions
    skew.shade_cin(raw_pressure, raw_temperatrue, parcel_path, raw_dewpoint, alpha = 0.2, label="CAPE")
    skew.shade_cape(raw_pressure, raw_temperatrue, parcel_path, alpha = 0.2, label="CIN")

    #Plotting a hodograph; rect tuple defines the shape and position on fig
    hodo_ax = plt.axes((0.48, 0.45, 0.5, 0.5))
    #compnent_range = tells you the range, in this case [-80kts to 80kts]
    hodo = Hodograph(hodo_ax, component_range=80) 

    #Adds polar grids (circles) on the hodo
    hodo.add_grid(increment=20, ls="-", lw=1.5, alpha=0.5) #Darker circles every 20kts
    hodo.add_grid(increment=10, ls="--", lw=1, alpha=0.3) #lighter cirlles every 10kts

    hodo.ax.set_box_aspect(1) #Set height to width ratio of the hodograph box
    #Remove any ticks along the y and x axis
    hodo.ax.set_yticklabels([])
    hodo.ax.set_xticklabels([])
    hodo.ax.set_xticks([])
    hodo.ax.set_yticks([])
    #Remove any labels alon the x and y axis
    hodo.ax.set_xlabel(" ")
    hodo.ax.set_ylabel(" ")
    
    #plt.xticks((np.arange(0, 0, 1)))
    #plt.yticks((np.arange(0, 0, 1)))

    #Plots the scale on the x and y axis
    for i in range(10, 90, 10):
        #Adds scale to x axis (i,0); xytest/textcoords offsets the labels up by just a little to make it look nicer
        #clip_on removes any labels that go outside the hodograph fig
        hodo.ax.annotate(str(i), (i, 0), xytext=(0,2), textcoords="offset pixels", clip_on=True, 
                         fontsize=10, weight="bold", alpha=0.3)
        #Label y axis
        hodo.ax.annotate(str(i), (0, i), xytext=(2,0), textcoords="offset pixels", clip_on=True, 
                         fontsize=10, weight="bold", alpha=0.3)

    #plot u and v components on the hodo; third parameter, pressure, is needed to determine the color intervals
    hodo.plot_colormapped(raw_Xcomponent_windspeed, raw_Ycomponent_winderspeed, raw_pressure, lw=3, label="0-12KM WIND")

    #Calculate the right mover, left mover, and mean wind vectors
    RM, LM, MW = mpcalc.bunkers_storm_motion(raw_pressure, raw_Xcomponent_windspeed, raw_Ycomponent_winderspeed, raw_height)

    #Plots RM, LW, and MW on the hodo
    #Add 0.5 to each coord since the text covers up the actual point, will add a dot at each actual coord to make it clear
    #Why the ".m"?
    hodo.ax.text((RM[0].m + 0.5), (RM[1].m + 0.5), "RM", weight="bold", ha="left", fontsize=10, alpha=0.6, color="red")
    hodo.ax.text((LM[0].m + 0.5), (LM[1].m + 0.5), "LM", weight="bold", ha="left", fontsize=10, alpha=0.6, color="blue")
    hodo.ax.text((MW[0].m + 0.5), (MW[1].m + 0.5), "MW", weight="bold", ha="left", fontsize=10, alpha=0.6, color="black")

    #plots RM, LM, MW as a point in the hodo
    #Since hodo.plot takes in an array of values you cannot actually plot one point
    #So you add a little bit to each vector to create an array
    #Instead of a point, you are plotting a very small line segment
    #Make sure around any ordered pair "[]" is used and NOT "{}", {} defines a set, not ordered pair
    RMx = [RM[0].m, RM[0].m + 0.1]
    RMy = [RM[1].m, RM[1].m + 0.1]
    hodo.plot(RMx, RMy, color="red")

    #Left mover
    LMx = [LM[0].m, LM[0].m + 0.1]
    LMy = [LM[1].m, LM[1].m + 0.1]
    hodo.plot(LMx, LMy, color="blue")

    #Mean wind
    MWx = [MW[0].m, MW[0].m + 0.1]
    MWy = [MW[1].m, MW[1].m + 0.1]
    hodo.plot(MWx, MWy, color="black")    

    #Need to continue working on getting the effective inflow later shaded on the hodograph
    #get X and Y components for a vector going from the sfc to RM 
    sfc_to_RM_XVector = [raw_Xcomponent_windspeed[0].m, RM[0].m]
    sfc_to_RM_YVector = [raw_Ycomponent_winderspeed[0].m, RM[1].m]

    #Plot sfc to RM vector
    hodo.plot(sfc_to_RM_XVector, sfc_to_RM_YVector, color="k", linewidth=0.5)

    #Creates a rectangle (anchor point, width, height, ect..)
    #Transform=fig.transFigure indicates that the measurements are relative to fig dimensions
    #patches.extend adds the new rectangle to the list of shapes on the fig
    fig.patches.extend([plt.Rectangle((0.562, 0.05), 0.334, 0.37, edgecolor="black", facecolor="white", 
                                      linewidth=1, alpha=1, transform=fig.transFigure, figure=fig)])
    
    #Calculate kindex and totals totals
    kindex = mpcalc.k_index(raw_pressure, raw_temperatrue, raw_dewpoint)
    totals_totals = mpcalc.total_totals_index(raw_pressure, raw_temperatrue, raw_dewpoint)

    #Calculate the mixed layer and most unstable cape and cin
    mlcape, mlcin = mpcalc.mixed_layer_cape_cin(raw_pressure, raw_temperatrue, raw_dewpoint)
    mucape, mucin = mpcalc.most_unstable_cape_cin(raw_pressure, raw_temperatrue, raw_dewpoint, depth=50 * units.hPa)
    sbcape, sbcin = mpcalc.surface_based_cape_cin(raw_pressure, raw_temperatrue, raw_dewpoint)

    #obtains all pressure and temperature values from the data set
    #that are at or below lcl pressure level
    new_lcl_p = np.append(raw_pressure[raw_pressure > lcl_p], lcl_p)
    new_lcl_t = np.append(raw_temperatrue[raw_pressure > lcl_p], lcl_t)

    #estaimte the lcl height using hypsometric equation
    lcl_height = mpcalc.thickness_hydrostatic(new_lcl_p, new_lcl_t)

    #Compute SRH at 1, 3, and 6km, the depth is the how high in the atmopshere SRH is computed
    Pos_helicity1, neg_helicity1, total_helicity1 = mpcalc.storm_relative_helicity(raw_height,
                                raw_Xcomponent_windspeed, raw_Ycomponent_winderspeed, depth=1 * units.km)
    Pos_helicity3, neg_helicity3, total_helicity3 = mpcalc.storm_relative_helicity(raw_height,
                                raw_Xcomponent_windspeed, raw_Ycomponent_winderspeed, depth=3 * units.km)
    Pos_helicity6, neg_helicity6, total_helicity6 = mpcalc.storm_relative_helicity(raw_height,
                                raw_Xcomponent_windspeed, raw_Ycomponent_winderspeed, depth=6 * units.km)
    
    #Calculate bulk shear from sfc to 1, 3, 6km
    #Since the output is u and v components, need to calculate magnitude
    ubshear1, vbshear1 = mpcalc.bulk_shear(raw_pressure, raw_Xcomponent_windspeed, raw_Ycomponent_winderspeed,
                                raw_height, depth=1 * units.km)
    bshear1 = mpcalc.wind_speed(ubshear1, vbshear1)
    ubshear3, vbshear3 = mpcalc.bulk_shear(raw_pressure, raw_Xcomponent_windspeed, raw_Ycomponent_winderspeed,
                                raw_height, depth=3 * units.km)
    bshear3 = mpcalc.wind_speed(ubshear3, vbshear3)
    ubshear6, vbshear6 = mpcalc.bulk_shear(raw_pressure, raw_Xcomponent_windspeed, raw_Ycomponent_winderspeed,
                                raw_height, depth=6 * units.km)
    bshear6 = mpcalc.wind_speed(ubshear6, vbshear6)    

    STP = mpcalc.significant_tornado(sbcape, lcl_height, total_helicity3,
                                     bshear3).to_base_units()
    SCP = mpcalc.supercell_composite(mucape, total_helicity3, bshear3)

    #plots parameters on the bottom right of the sounding
    #":0.f" rounds to the nearest whole number
    # "~P" abbreviates units
    #Therodynamic parameters
    plt.figtext(0.58, 0.37, "SBCAPE: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.71, 0.37, f"{sbcape:.0f~P}", weight="bold", fontsize=15,
                color="orangered", ha="right")
    plt.figtext(0.58, 0.34, "SBCIN: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.71, 0.34, f"{sbcin:.0f~P}", weight="bold", fontsize=15,
                color="lightblue", ha="right")
    plt.figtext(0.58, 0.29, "MLCAPE: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.71, 0.29, f"{mlcape:.0f~P}", weight="bold", fontsize=15,
                color="orangered", ha="right")
    plt.figtext(0.58, 0.26, "MLCIN: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.71, 0.26, f"{mlcin:.0f~P}", weight="bold", fontsize=15,
                color="lightblue", ha="right")
    plt.figtext(0.58, 0.21, "MUCAPE: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.71, 0.21, f"{mucape:.0f~P}", weight="bold", fontsize=15,
                color="orangered", ha="right")
    plt.figtext(0.58, 0.18, "MUCIN: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.71, 0.18, f"{mucin:.0f~P}", weight="bold", fontsize=15,
                color="lightblue", ha="right")
    plt.figtext(0.58, 0.13, "TT-INDEX: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.71, 0.13, f"{totals_totals:.0f~P}", weight="bold", fontsize=15,
                  color="orangered", ha="right")
    plt.figtext(0.58, 0.10, "K-INDEX: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.71, 0.10, f"{kindex:.0f~P}", weight="bold", fontsize=15,
                color="orangered", ha="right")

    #Kinematic parameters
    plt.figtext(0.73, 0.37, "0-1KM SRH: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.88, 0.37, f"{total_helicity1:.0f~P}", weight="bold", fontsize=15,
                color="navy", ha="right")
    plt.figtext(0.73, 0.34, "0-1KM SHEAR: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.88, 0.34, f"{bshear1:.0f~P}", weight="bold", fontsize=15,
                color="navy", ha="right")
    plt.figtext(0.73, 0.29, "0-3KM SRH", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.88, 0.29, f"{total_helicity3:.0f~P}", weight="bold", fontsize=15,
                color="navy", ha="right")
    plt.figtext(0.73, 0.26, "0-3KM SHEAR: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.88, 0.26, f"{bshear3:.0f~P}", weight="bold", fontsize=15, 
                color="navy", ha="right")
    plt.figtext(0.73, 0.21, "0-6KM SRH: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.88, 0.21, f"{total_helicity6:.0f~P}", weight="bold", fontsize=15, 
                color="navy", ha='right')
    plt.figtext(0.73, 0.18, "0-6KM SHEAR: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.88, 0.18, f"{bshear6:.0f~P}", weight="bold", fontsize=15,
                color="navy", ha="right")
    plt.figtext(0.73, 0.13, "SIG TOR: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.88, 0.13, f"{STP[0]:.0f~P}", weight="bold", fontsize=15,
                color="orangered", ha="right")
    plt.figtext(0.73, 0.1, "SCP: ", weight="bold", fontsize=15,
                color="black", ha="left")
    plt.figtext(0.88, 0.1, f"{SCP[0]:.0f~P}", weight="bold", fontsize=15,
                color="orangered", ha="right")
    
    skew.ax.legend(loc="upper left")
    hodo.ax.legend(loc="upper left")

    fig.suptitle(f"Upper Air Data for {airport.upper()} - Hour {f_hour}\nValid: {str(valid_time)} - Init: {init_str}", x=0.3, ha="center", va="top", weight="bold", fontsize=16)

    os.makedirs(output_path, exist_ok=True)
    plt.savefig(os.path.join(output_path, f"hour_{f_hour}.png"))
    plt.close()
    print(f'-> {airport} skewt hr {f_hour}')