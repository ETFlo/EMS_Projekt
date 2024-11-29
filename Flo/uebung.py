import pandapower as pp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Netz erstellen (wie zuvor)
net = pp.create_empty_network()

# Mittelspannungsebene (20 kV)
bus_hv = pp.create_bus(net, vn_kv=20, name="Mittelspannung")

# Niederspannungsebene (0.4 kV)
bus_lv = pp.create_bus(net, vn_kv=0.4, name="Niederspannung")

pp.create_ext_grid(net, bus=bus_hv, vm_pu=1.0, name="External Grid")
# Trafo hinzufügen
pp.create_transformer(net, hv_bus=bus_hv, lv_bus=bus_lv, std_type="0.4 MVA 20/0.4 kV")
#pp.create_transformer_from_parameters(
#    net, hv_bus=bus_hv, lv_bus=bus_lv, sn_mva=0.4, vn_hv_kv=20, vn_lv_kv=0.4,
#    vscr_percent=0.4, vsc_percent=6.0, pfe_kw=0.5, i0_percent=0.1, name="Trafo"
#)

# Niederspannungsbusse
bus_load_1 = pp.create_bus(net, vn_kv=0.4, name="Last 1")
bus_load_2 = pp.create_bus(net, vn_kv=0.4, name="Last 2")
bus_load_3 = pp.create_bus(net, vn_kv=0.4, name="Last 3")

# Leitungen
pp.create_line_from_parameters(net, bus_lv, bus_load_1, length_km=0.2, r_ohm_per_km=0.642, 
                                x_ohm_per_km=0.083, c_nf_per_km=210, max_i_ka=0.192, name="Leitung zu Last 1")
pp.create_line_from_parameters(net, bus_load_1, bus_load_2, length_km=0.2, r_ohm_per_km=0.642, 
                                x_ohm_per_km=0.083, c_nf_per_km=210, max_i_ka=0.192, name="Leitung zu Last 2")
pp.create_line_from_parameters(net, bus_load_2, bus_load_3, length_km=0.2, r_ohm_per_km=0.642, 
                                x_ohm_per_km=0.083, c_nf_per_km=210, max_i_ka=0.192, name="Leitung zu Last 3")

# Lasten hinzufügen
pp.create_load(net, bus_load_1, p_mw=0.05, q_mvar=0.02, name="Load 1")
pp.create_load(net, bus_load_2, p_mw=0.06, q_mvar=0.03, name="Load 2")
pp.create_load(net, bus_load_3, p_mw=0.07, q_mvar=0.04, name="Load 3")

# PV-Anlagen hinzufügen
pv_1 = pp.create_sgen(net, bus_load_1, p_mw=0, name="PV 1")
pv_2 = pp.create_sgen(net, bus_load_2, p_mw=0, name="PV 2")
pv_3 = pp.create_sgen(net, bus_load_3, p_mw=0, name="PV 3")

# Typisches Einspeiseprofil erstellen
n_steps = 35040  # Viertelstundenschritte (8760 Stunden * 4)
hours = np.arange(n_steps) / 4  # Zeit in Stunden (0 bis 8760)
days = hours / 24  # Tage (0 bis 365)

# Tagesprofil: Sinuskurve, max. bei 12 Uhr (Mittagszeit)
daily_profile = np.maximum(0, np.sin((hours % 24 - 6) * np.pi / 12))

# Jahreszeitenmodulation: Weniger im Winter, mehr im Sommer (cosinusförmig)
seasonal_variation = 0.5 * (1 + np.cos(2 * np.pi * (days - 80) / 365))

# PV-Einspeiseprofil
typical_pv_profile = daily_profile * seasonal_variation

# Skalierung für jede PV-Anlage
pv1_profile = 0.03 * typical_pv_profile  # Max 30 kW
pv2_profile = 0.04 * typical_pv_profile  # Max 40 kW
pv3_profile = 0.05 * typical_pv_profile  # Max 50 kW

# Ergebnisse speichern
results = []

# Simulation über alle Zeitschritte
for t in range(n_steps):
    # PV-Leistungen für diesen Zeitschritt setzen
    net.sgen.at[pv_1, "p_mw"] = -pv1_profile[t]
    net.sgen.at[pv_2, "p_mw"] = -pv2_profile[t]
    net.sgen.at[pv_3, "p_mw"] = -pv3_profile[t]
    
    # Lastflussberechnung
    pp.runpp(net)
    
    # Ergebnisse speichern
    results.append({
        "time": hours[t],
        "voltage_bus_lv": net.res_bus.at[bus_lv, "vm_pu"],
        "voltage_bus_load_1": net.res_bus.at[bus_load_1, "vm_pu"],
        "voltage_bus_load_2": net.res_bus.at[bus_load_2, "vm_pu"],
        "voltage_bus_load_3": net.res_bus.at[bus_load_3, "vm_pu"],
        "line_loss_mw": net.res_line["pl_mw"].sum(),
    })

# Ergebnisse in DataFrame umwandeln
results_df = pd.DataFrame(results)

# Ergebnisse speichern
results_df.to_csv("typical_pv_results.csv", index=False)

# Typisches PV-Profil visualisieren
plt.figure(figsize=(10, 6))
plt.plot(hours[:96], pv1_profile[:96], label="PV1 (30 kW)")
plt.plot(hours[:96], pv2_profile[:96], label="PV2 (40 kW)")
plt.plot(hours[:96], pv3_profile[:96], label="PV3 (50 kW)")
plt.xlabel("Stunden")
plt.ylabel("Leistung (MW)")
plt.title("Typisches PV-Profil (erster Tag)")
plt.legend()
plt.grid()
plt.show()
