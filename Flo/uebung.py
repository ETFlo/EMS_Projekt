import pandapower as pp
import pandapower.plotting as plot
import numpy as np

# Erstellung eines leeren Netzes
net = pp.create_empty_network()

# create bus
hv_bus = pp.create_bus(net, vn_kv=20, name="HV Bus")  # Hochspannungsseite
mv_bus = pp.create_bus(net, vn_kv=0.4, name="MV Bus")  # Mittelspannungsseite

v1 = pp.create_bus(net, vn_kv=0.4, name="v1")
v1_1 = pp.create_bus(net, vn_kv=0.4, name="v1.1")
v2 = pp.create_bus(net, vn_kv=0.4, name="v2")

# external grid
pp.create_ext_grid(net, hv_bus, vm_pu=1.02, name="external grid")

# create transformer
pp.create_transformer(net, hv_bus, mv_bus, std_type="0.4 MVA 20/0.4 kV")
#print(pp.available_std_types(net, "trafo"))     # std_types of trafos

# create line
pp.create_line(net, mv_bus, v1, std_type="NAYY 4x50 SE", length_km=0.1, name="line1")
pp.create_line(net, v1, v1_1, std_type="NAYY 4x50 SE", length_km=0.1, name="line1.1")
pp.create_line(net, mv_bus, v2, std_type="NAYY 4x50 SE", length_km=0.1, name="line2")
#print(pp.available_std_types(net))


# create load
pp.create_load(net, v1, p_mw=0.1, q_mvar=0.01)
pp.create_load(net, v1, p_mw=0.1, q_mvar=0.01)
#pp.create_load(net, mv_bus, p_mw=0.1, q_mvar=0.05)


# create gen
pp.create_sgen(net, v1_1, p_mw=0.5, q_mvar=0.05, name="PV1")



 

# Anzeige der Netz-Elemente
#print(net)

# Lastfluss-Berechnung
pp.runpp(net)

print(net)

print(net.res_line)

plot.simple_plot(net, show_plot=True)

#print(get_connected)

"""
# Ergebnisse anzeigen
print("\nBus-Spannungen:")
print(net.res_bus)

print("\nLeitungsbelastungen:")
print(net.res_line)
"""