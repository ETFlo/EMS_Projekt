import pandapower as pp
import pandapower.plotting as plot
import numpy as np
import pv_battery_model

# Erstellung eines leeren Netzes
net = pp.create_empty_network()

# create bus
mv_bus = pp.create_bus(net, vn_kv=20, name="HV Bus")  # Hochspannungsseite
lv_bus = pp.create_bus(net, vn_kv=0.4, name="MV Bus")  # Mittelspannungsseite

v1_1 = pp.create_bus(net, vn_kv=0.4, name="v1.1")
v1_2 = pp.create_bus(net, vn_kv=0.4, name="v1.2")
v2_1 = pp.create_bus(net, vn_kv=0.4, name="v2.1")
v2_2 = pp.create_bus(net, vn_kv=0.4, name="v2.2")

# external grid
pp.create_ext_grid(net, mv_bus, vm_pu=1.02, name="external grid")

# create transformer
pp.create_transformer(net, mv_bus, lv_bus, std_type="0.4 MVA 20/0.4 kV")
#print(pp.available_std_types(net, "trafo"))     # zeigt mir verschiedene verfügbare Trafos

# create line
pp.create_line(net, lv_bus, v1_1, std_type="NAYY 4x50 SE", length_km=0.1, name="line1_1")
pp.create_line(net, v1_1, v1_2, std_type="NAYY 4x50 SE", length_km=0.1, name="line1_2")
pp.create_line(net, lv_bus, v2_1, std_type="NAYY 4x50 SE", length_km=0.1, name="line2_1")
pp.create_line(net, v2_1, v2_2, std_type="NAYY 4x50 SE", length_km=0.1, name="line2_2")
#print(pp.available_std_types(net))                # zeigt mir verschiedene verfügbare Kabeltypen


# create load
pp.create_load(net, v1_1, p_mw=0.1, q_mvar=0.01)
pp.create_load(net, v1_2, p_mw=0.1, q_mvar=0.01)
pp.create_load(net, v2_1, p_mw=0.1, q_mvar=0.01)
pp.create_load(net, v2_2, p_mw=0.1, q_mvar=0.01)
#pp.create_load(net, mv_bus, p_mw=0.1, q_mvar=0.05)


# PV-Anlagen hinzufügen
pv_1 = pp.create_sgen(net, v1_1, p_mw=0.2, name="PV 1")
pv_2 = pp.create_sgen(net, v1_2, p_mw=0, name="PV 2")
pv_3 = pp.create_sgen(net, v2_1, p_mw=0, name="PV 3")
pv_4 = pp.create_sgen(net, v2_2, p_mw=0, name="PV 4")


# Ergebnisse speichern
results = []


# PV Daten einlesen
filename_pv = "C:/Users/flori/EMS/EMS_Projekt/Flo/files/pv_1kWp.csv" 
pv_1_data = pv_battery_model.pv(10, filename_pv)
pv_2_data = pv_battery_model.pv(12, filename_pv)
pv_3_data = pv_battery_model.pv(14, filename_pv)


# Simulation über alle Zeitschritte
for t in range(np.size(pv_1_data)):

    # PV-Leistungen für diesen Zeitschritt setzen
    net.sgen.at[pv_1, "p_mw"] = -pv_1_data[t]
    net.sgen.at[pv_2, "p_mw"] = -pv_2_data[t]
    net.sgen.at[pv_3, "p_mw"] = -pv_3_data[t]
    
    # Lastflussberechnung
    pp.runpp(net)
    
    # Ergebnisse speichern
    results.append({
        "time": t,
        "voltage_bus_lv": net.res_bus.at[lv_bus, "vm_pu"],
        "voltage_bus_load_1_1": net.res_bus.at[v1_1, "vm_pu"],
        "voltage_bus_load_1_2": net.res_bus.at[v1_2, "vm_pu"],
        "voltage_bus_load_2_1": net.res_bus.at[v2_1, "vm_pu"],
        "voltage_bus_load_2_2": net.res_bus.at[v2_2, "vm_pu"],
        "line_loss_mw": net.res_line["pl_mw"].sum(),
    })
 

 # Ergebnisse in DataFrame umwandeln
results_df = pd.DataFrame(results)

# Anzeige der Netz-Elemente
#print(net)

# Lastfluss-Berechnung
#pp.runpp(net)

print(net)

print(net.res_bus)

plot.simple_plot(net, show_plot=True)

#print(get_connected)

"""
# Ergebnisse anzeigen
print("\nBus-Spannungen:")
print(net.res_bus)

print("\nLeitungsbelastungen:")
print(net.res_line)
"""