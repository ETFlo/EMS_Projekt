import pandapower as pp
import pandapower.plotting as plot
import numpy as np
import pandas as pd
import pv_battery_model_v2 as pv_battery_model
import matplotlib.pyplot as plt
from plotfunktion import spannungsplot



# Die battery_control Funktion definieren
#Rückgabewert in % (auch negativ)
def battery_control(vm_pu, soc_percent, vm_low_weight, vm_high_weight, low_exp, high_exp):
    """
    Berechnet den Rückgabewert basierend auf dem übergebenen vm_pu-Wert.

    Der Rückgabewert liegt zwischen -1 und 1 und folgt einer polynomielle Funktion:
    - Bei vm_pu = 0.97 beträgt der Rückgabewert -1.
    - Bei vm_pu = 1.03 beträgt der Rückgabewert 1.
    - Dazwischen verläuft die Funktion polynmomiell.

    :param vm_pu: Der Eingangswert (float)
    :return: Der berechnete Rückgabewert (float)
    """
    #vm_pu = vm_pu + 0.02       #   verschiebt die Lade-/Entladelogik um den Wert z.B. 2 % 

    if vm_pu < 0.97:
        return -1
    elif vm_pu > 1.03:
        return 1

    # Normalisierung von vm_pu in den Bereich [-1, 1]
    if vm_pu <= 1.0:
        # Abfall von -1 bis 0
        return -(((1 - vm_pu) / (1.0 - 0.97)) ** low_exp * vm_low_weight + soc_percent ** low_exp * (1 - vm_low_weight))
    else:
        # Anstieg von 0 bis 1
        return ((vm_pu - 1.0) / (1.03 - 1.0)) ** high_exp * vm_high_weight + (1 - soc_percent) ** high_exp * (1 - vm_high_weight)


def voltage_range_exceedance(v_max, v_min, band):
    if(abs(1 - v_min) > 0.03):
        return 1
    elif(abs(v_max - 1) > 0.03):
        return 1
    else:
        return 0


def simulate(bat1_max_charge, bat1_max_discharge, bat2_max_charge, bat2_max_discharge, battery_low_weight, battery_high_weight, battery_low_exp, battery_high_exp):
    
    # Parameter
    overstepping_voltage = 0
    voltage_bandwidth = 0.03            # Spannungsbandbreitenhöhe in +-
    
    # Erstellung eines leeren Netzes
    net = pp.create_empty_network()

    # create bus
    mv_bus = pp.create_bus(net, vn_kv=20, name="MV Bus")  # Mittelspannungsseite
    lv_bus = pp.create_bus(net, vn_kv=0.4, name="LV Bus")  # Niederspannungsseite

    v1_1 = pp.create_bus(net, vn_kv=0.4, name="v1.1")
    v1_2 = pp.create_bus(net, vn_kv=0.4, name="v1.2")
    v1_2_1_1 = pp.create_bus(net, vn_kv=0.4, name="v1.2.1.1")
    v1_2_1_2 = pp.create_bus(net, vn_kv=0.4, name="v1.2.1.2")
    v1_2_2_1 = pp.create_bus(net, vn_kv=0.4, name="v1.2.2.1")
    v1_2_2_2 = pp.create_bus(net, vn_kv=0.4, name="v1.2.2.2")
    v2_1 = pp.create_bus(net, vn_kv=0.4, name="v2.1")
    v2_2 = pp.create_bus(net, vn_kv=0.4, name="v2.2")
    v2_2_1_1 = pp.create_bus(net, vn_kv=0.4, name="v2.2.1.1")
    v2_2_1_2 = pp.create_bus(net, vn_kv=0.4, name="v2.2.1.2")
    v2_2_2_1 = pp.create_bus(net, vn_kv=0.4, name="v2.2.2.1")
    v2_2_2_2 = pp.create_bus(net, vn_kv=0.4, name="v2.2.2.2")

    # external grid
    pp.create_ext_grid(net, mv_bus, vm_pu=1.02, name="external grid")

    # create transformer
    pp.create_transformer(net, mv_bus, lv_bus, std_type="0.4 MVA 20/0.4 kV")
    #print(pp.available_std_types(net, "trafo"))     # zeigt mir verschiedene verfügbare Trafos

    # create line
    pp.create_line(net, lv_bus, v1_1, std_type="NAYY 4x50 SE", length_km=0.1, name="line1.1")
    pp.create_line(net, v1_1, v1_2, std_type="NAYY 4x50 SE", length_km=0.1, name="line1.2")
    pp.create_line(net, v1_2, v1_2_1_1, std_type="NAYY 4x50 SE", length_km=0.1, name="line1.2.1.1")
    pp.create_line(net, v1_2_1_1, v1_2_1_2, std_type="NAYY 4x50 SE", length_km=0.1, name="line1.2.1.2")
    pp.create_line(net, v1_2, v1_2_2_1, std_type="NAYY 4x50 SE", length_km=0.1, name="line1.2.2.1")
    pp.create_line(net, v1_2_2_1, v1_2_2_2, std_type="NAYY 4x50 SE", length_km=0.1, name="line1.2.2.2")
    pp.create_line(net, lv_bus, v2_1, std_type="NAYY 4x50 SE", length_km=0.1, name="line2_1")
    pp.create_line(net, v2_1, v2_2, std_type="NAYY 4x50 SE", length_km=0.1, name="line2.2")
    pp.create_line(net, v2_2, v2_2_1_1, std_type="NAYY 4x50 SE", length_km=0.1, name="line2.2.1.1")
    pp.create_line(net, v2_2_1_1, v2_2_1_2, std_type="NAYY 4x50 SE", length_km=0.1, name="line2.2.1.2")
    pp.create_line(net, v2_2, v2_2_2_1, std_type="NAYY 4x50 SE", length_km=0.1, name="line2.2.2.1")
    pp.create_line(net, v2_2_2_1, v2_2_2_2, std_type="NAYY 4x50 SE", length_km=0.2, name="line2.2.2.2")
    #print(pp.available_std_types(net))                # zeigt mir verschiedene verfügbare Kabeltypen


    # Variablenzuweisung für Lasten und Erzeuger
    l_1_1 = pp.create_load(net, v1_1, p_mw=0.1, q_mvar=0.01, name="L1.1")
    l_1_2 = pp.create_load(net, v1_2, p_mw=0.0, q_mvar=0.01, name="L1.2")
    l_1_2_1_1 = pp.create_load(net, v1_2_1_1, p_mw=0.0, q_mvar=0.01, name="L1.2.1.1")
    l_1_2_1_2 = pp.create_load(net, v1_2_1_2, p_mw=0.0, q_mvar=0.01, name="L1.2.1.2")
    l_1_2_2_1 = pp.create_load(net, v1_2_2_1, p_mw=0.0, q_mvar=0.01, name="L1.2.2.1")
    l_1_2_2_2 = pp.create_load(net, v1_2_2_2, p_mw=0.0, q_mvar=0.01, name="L1.2.2.2")
    l_2_1 = pp.create_load(net, v2_1, p_mw=0.0, q_mvar=0.01, name="L2.1")
    l_2_2 = pp.create_load(net, v2_2, p_mw=0.1, q_mvar=0.01, name="L2.2")
    l_2_2_1_1 = pp.create_load(net, v2_2_1_1, p_mw=0.0, q_mvar=0.01, name="L2.2.1.1")
    l_2_2_1_2 = pp.create_load(net, v2_2_1_2, p_mw=0.0, q_mvar=0.01, name="L2.2.1.2")
    l_2_2_2_1 = pp.create_load(net, v2_2_2_1, p_mw=0.1, q_mvar=0.01, name="L2.2.2.1")
    l_2_2_2_2 = pp.create_load(net, v2_2_2_2, p_mw=0.0, q_mvar=0.01, name="L2.2.2.2")

    # Variablenzuweisung für Erzeuger
    e_1_1 = pp.create_sgen(net, v1_1, p_mw=0.02, q_mvar=0.005, name="E1.1")
    e_1_2 = pp.create_sgen(net, v1_2, p_mw=0.03, q_mvar=0.005, name="E1.2")
    e_1_2_1_1 = pp.create_sgen(net, v1_2_1_1, p_mw=0.04, q_mvar=0.005, name="E1.2.1.1")
    e_1_2_1_2 = pp.create_sgen(net, v1_2_1_2, p_mw=0.05, q_mvar=0.005, name="E1.2.1.2")
    e_1_2_2_1 = pp.create_sgen(net, v1_2_2_1, p_mw=0.06, q_mvar=0.005, name="E1.2.2.1")
    e_1_2_2_2 = pp.create_sgen(net, v1_2_2_2, p_mw=0.07, q_mvar=0.005, name="E1.2.2.2")
    e_2_1 = pp.create_sgen(net, v2_1, p_mw=0.08, q_mvar=0.005, name="E2.1")
    e_2_2 = pp.create_sgen(net, v2_2, p_mw=0.09, q_mvar=0.005, name="E2.2")
    e_2_2_1_1 = pp.create_sgen(net, v2_2_1_1, p_mw=0.1, q_mvar=0.005, name="E2.2.1.1")
    e_2_2_1_2 = pp.create_sgen(net, v2_2_1_2, p_mw=0.11, q_mvar=0.005, name="E2.2.1.2")
    e_2_2_2_1 = pp.create_sgen(net, v2_2_2_1, p_mw=0.12, q_mvar=0.005, name="E2.2.2.1")
    e_2_2_2_2 = pp.create_sgen(net, v2_2_2_2, p_mw=0.13, q_mvar=0.005, name="E2.2.2.2")


    # Ergebnisse speichern
    results = []


    """ PV DATEN """
    # PV Daten einlesen
    filename_pv = "C:/Users/flori/EMS/EMS_Projekt/Flo/files/RESProfile.csv"  # Daten liegen in 1/4 h Zeitschritten vor
    pv_data = pd.read_csv(filename_pv, delimiter=";", parse_dates=["time"], index_col="time")

    # Extrahiere die PV-Daten (Spalten: PV5, PV6, PV8)
    pv_1_raw_data = pv_data["PV1"].values  # Rohwerte ohne Umrechnung
    pv_2_raw_data = pv_data["PV3"].values
    pv_3_raw_data = pv_data["PV4"].values

    #filename_pv = "C:/Users/flori/EMS/EMS_Projekt/Flo/files/pv_1kWp.csv"   # Daten liegen in Stundenzeitschritten vor
    #pv_1_data = pv_battery_model.pv(50, filename_pv) / 1000
    #pv_2_data = pv_battery_model.pv(50, filename_pv) / 1000
    #pv_3_data = pv_battery_model.pv(20, filename_pv) / 1000

    pv_1_data = pv_battery_model.pv_scale(pv_1_raw_data, 50) / 1000
    pv_2_data = pv_battery_model.pv_scale(pv_2_raw_data, 30) / 1000
    pv_3_data = pv_battery_model.pv_scale(pv_3_raw_data, 20) / 1000
    """ -------- """

    """ LAST DATEN """
    #Last Daten einlesen
    filename_load = "C:/Users/flori/EMS/EMS_Projekt/Flo/files/LoadProfile.csv"  # Daten liegen in 1/4 h Zeitschritten vor
    load_data = pd.read_csv(filename_load, delimiter=";", parse_dates=["time"], index_col="time")

    last1 = 10 * load_data["H0-A_pload"].values / 1000
    last2 = 20 * load_data["G2-A_pload"].values / 1000
    last3 = 15 * load_data["H0-B_pload"].values / 1000
    last4 = 10 * load_data["G3-A_pload"].values / 1000
    """ --------- """

    """ BATTERIE """
    b_1_2_1_1 = pv_battery_model.Battery(SoC = 1000/1000, max_capacity = 2000/1000, max_charge = bat1_max_charge / 1000, max_discharge = bat1_max_discharge / 1000)
    b_2_2_2_2 = pv_battery_model.Battery(SoC = 1000/1000, max_capacity = 2000/1000, max_charge = bat2_max_charge / 1000, max_discharge = bat2_max_discharge / 1000)
    """ --------- """

    voltage_difference = 0.0


    for t in range(600):
                
        # PV-Daten zuweisen
        net.sgen.at[e_1_1, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2_1_1, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2_1_2, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2_2_1, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2_2_2, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_2_1, "p_mw"] = pv_2_data[t]
        net.sgen.at[e_2_2, "p_mw"] = pv_2_data[t]
        net.sgen.at[e_2_2_1_1, "p_mw"] = pv_3_data[t]
        net.sgen.at[e_2_2_1_2, "p_mw"] = pv_3_data[t]
        net.sgen.at[e_2_2_2_1, "p_mw"] = pv_3_data[t]
        net.sgen.at[e_2_2_2_2, "p_mw"] = pv_3_data[t]

        """
        # PV-Daten zuweisen
        net.sgen.at[e_1_1, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2_1_1, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2_1_2, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2_2_1, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_1_2_2_2, "p_mw"] = pv_1_data[t]
        net.sgen.at[e_2_1, "p_mw"] = pv_2_data[t]
        net.sgen.at[e_2_2, "p_mw"] = pv_2_data[t]
        net.sgen.at[e_2_2_1_1, "p_mw"] = pv_3_data[t]
        net.sgen.at[e_2_2_1_2, "p_mw"] = pv_3_data[t]
        net.sgen.at[e_2_2_2_1, "p_mw"] = pv_3_data[t]
        net.sgen.at[e_2_2_2_2, "p_mw"] = 5*pv_3_data[t]
        #net.sgen.at[e_2_2_2_2, "q_mw"] = 5*pv_3_data[t] * 0.2
        """
        
        #Lasten zuweisen
        net.load.at[l_1_1, "p_mw"] = last1[t]
        net.load.at[l_1_2, "p_mw"] = last2[t]
        net.load.at[l_1_2_1_1, "p_mw"] = last3[t]
        net.load.at[l_1_2_1_2, "p_mw"] = last2[t]
        net.load.at[l_1_2_2_1, "p_mw"] = last2[t]
        net.load.at[l_1_2_2_2, "p_mw"] = last1[t]
        net.load.at[l_2_1, "p_mw"] = last1[t]
        net.load.at[l_2_2, "p_mw"] = last4[t]
        net.load.at[l_2_2_1_1, "p_mw"] = last4[t]
        net.load.at[l_2_2_1_2, "p_mw"] = last3[t]
        net.load.at[l_2_2_2_1, "p_mw"] = last1[t]
        net.load.at[l_2_2_2_2, "p_mw"] = last4[t]

        """
        # Blindleistung zuweisen
        net.load.at[l_1_1, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_1_2, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_1_2_1_1, "q_mvar"] = load_data["G1-B_qload"].iloc[t]  
        net.load.at[l_1_2_1_2, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_1_2_2_1, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_1_2_2_2, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_2_1, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_2_2, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_2_2_1_1, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_2_2_1_2, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_2_2_2_1, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        net.load.at[l_2_2_2_2, "q_mvar"] = load_data["G1-B_qload"].iloc[t]
        """

        
        # zum prüfen des Netzes, bei einer Fehlermeldung
        try:
            pp.runpp(net, max_iter=1500)
        except pp.pandapower.powerflow.LoadflowNotConverged:
            print("Lastfluss nicht konvergiert!")
            print("Knotenspannungen:")
            print(net.res_bus)
            print("Leitungsbelastungen:")
            print(net.res_line)
        
        """
        # Erster Versuch den Spannungsabfall mit Hilfe der Batterie zu regulieren
        if(net.res_bus.at[v2_2_2_2, "vm_pu"] > 1.025):
            #pv_power = b_2_2_2_2.charge_quarter(pv_4_data_x[t] * 1/4) * 4
            pv_power = b_2_2_2_2.charge(pv_4_data_x[t],1/4)
            net.sgen.at[e_2_2_2_2, "p_mw"] = abs(pv_power)
            pp.runpp(net)
        elif(net.res_bus.at[v2_2_2_2, "vm_pu"] < 0.975):
            #pv_power = b_2_2_2_2.charge_quarter(-b_2_2_2_2.max_discharge * 1/4) * 4
            #pv_power = b_2_2_2_2.max_discharge * 1/4 - remaining_pv
            #pv_power = pv_power + b_2_2_2_2.charge(-2, 1/4)
            pv_power = pv_power + abs(b_2_2_2_2.charge(-b_2_2_2_2.max_discharge, 1/4))
            net.sgen.at[e_2_2_2_2, "p_mw"] = pv_power
            pp.runpp(net) 
        """

        
        battery_action1 = battery_control(net.res_bus.at[v1_2_1_1, "vm_pu"], b_1_2_1_1.SoC / b_1_2_1_1.max_capacity, battery_low_weight, battery_high_weight, battery_low_exp, battery_high_exp)
        battery_action2 = battery_control(net.res_bus.at[v2_2_2_2, "vm_pu"], b_2_2_2_2.SoC / b_2_2_2_2.max_capacity, battery_low_weight, battery_high_weight, battery_low_exp, battery_high_exp)

        if(battery_action1 > 0):                                
            net.sgen.at[e_1_2_1_1, "p_mw"] = net.sgen.at[e_1_2_1_1, "p_mw"] - b_1_2_1_1.charge(battery_action1*b_1_2_1_1.max_charge, 1/4)
        else:
            net.sgen.at[e_1_2_1_1, "p_mw"] = net.sgen.at[e_1_2_1_1, "p_mw"] - b_1_2_1_1.charge(battery_action1*b_1_2_1_1.max_discharge, 1/4)

        if(battery_action2 > 0):
            net.sgen.at[e_2_2_2_2, "p_mw"] = net.sgen.at[e_2_2_2_2, "p_mw"] - b_2_2_2_2.charge(battery_action2*b_2_2_2_2.max_charge, 1/4)
        else:
            net.sgen.at[e_2_2_2_2, "p_mw"] = net.sgen.at[e_2_2_2_2, "p_mw"] - b_2_2_2_2.charge(battery_action1*b_2_2_2_2.max_discharge, 1/4)

        pp.runpp(net)
        

        
        # Ergebnisse speichern
        results.append({
            "time": t,
            "voltage_bus_lv": net.res_bus.at[lv_bus, "vm_pu"],
            "voltage_bus_1_1": net.res_bus.at[v1_1, "vm_pu"],
            "voltage_bus_1_2": net.res_bus.at[v1_2, "vm_pu"],
            "voltage_bus_1_2_1_1": net.res_bus.at[v1_2_1_1, "vm_pu"],
            "voltage_bus_1_2_1_2": net.res_bus.at[v1_2_1_2, "vm_pu"],
            "voltage_bus_1_2_2_1": net.res_bus.at[v1_2_2_1, "vm_pu"],
            "voltage_bus_1_2_2_2": net.res_bus.at[v1_2_2_2, "vm_pu"],
            "voltage_bus_2_1": net.res_bus.at[v2_1, "vm_pu"],
            "voltage_bus_2_2": net.res_bus.at[v2_2, "vm_pu"],
            "voltage_bus_2_2_1_1": net.res_bus.at[v2_2_1_1, "vm_pu"],
            "voltage_bus_2_2_1_2": net.res_bus.at[v2_2_1_2, "vm_pu"],
            "voltage_bus_2_2_2_1": net.res_bus.at[v2_2_2_1, "vm_pu"],
            "voltage_bus_2_2_2_2": net.res_bus.at[v2_2_2_2, "vm_pu"]
        })

        max_vm_pu = net.res_bus["vm_pu"].max()
        min_vm_pu = net.res_bus["vm_pu"].min()

        
        overstepping_voltage = overstepping_voltage + voltage_range_exceedance(max_vm_pu, min_vm_pu, voltage_bandwidth)

        if(abs(max_vm_pu - 1) > voltage_difference):
            voltage_difference = abs(max_vm_pu - 1)
        if(abs(1 - min_vm_pu) > voltage_difference):
            voltage_difference = abs(1 - min_vm_pu)
        
    

    
    
    # Ergebnisse in DataFrame umwandeln
    results_df = pd.DataFrame(results)
    #print(results_df.head())

    # Lastfluss-Berechnung 
    #pp.runpp(net)


    #load_results = net.res_load.join(net.load["name"], how='left')
    #print(load_results)

    # Ergebnisse speichern in eine CSV Datei
    #results_df.to_csv("C:/Users/flori/EMS/EMS_Projekt/Flo/files/typical_pv_results.csv", index=False)


    plot.simple_plot(net, show_plot=True, plot_gens=True, plot_loads=True, plot_sgens=True)


    # Spannungen plotten
    plt.figure(2,figsize=(12, 6))
    plt.plot(results_df["time"], results_df["voltage_bus_lv"], label="LV Bus")
    plt.plot(results_df["time"], results_df["voltage_bus_1_1"], label="Bus 1-1")
    plt.plot(results_df["time"], results_df["voltage_bus_1_2_1_1"], label="Bus 1-2-1-1")
    plt.plot(results_df["time"], results_df["voltage_bus_2_2"], label="Bus 2-2")
    plt.plot(results_df["time"], results_df["voltage_bus_2_2_2_2"], label="Bus 2-2-2-2")

    # Titel, Labels und Legende
    plt.title("Spannungsverlauf an verschiedenen Knoten")
    plt.xlabel("Zeit")
    plt.ylabel("Spannung [p.u.]")
    plt.legend()
    plt.grid(True)
    plt.show()


    # Weg/Spannungs - Diagramm
    #spannungsplot(net, results_df, 524)
    #spannungsplot(net, results_df, 560)
    #spannungsplot(net, results_df, 565)
    #spannungsplot(net, results_df, 570) 
    
    print("Anzahl der Spannungsbandüberschreitungen: ", overstepping_voltage)
    

    return overstepping_voltage
    #return voltage_difference



if __name__ == "__main__":
    #v_delta = simulate(1.000e+01,  1.532e+01,  1.000e+01,  1.045e+01,  5.000e-01, 5.000e-01,  2.000e+00,  2.000e+00)    # Standardverfahren
    #v_delta = simulate(2.758e+01,  2.253e+01,  1.762e+01,  1.089e+01,  1.824e-02, 4.453e-01,  8.551e+00,  3.067e-02)    # Nelder-Mead Verfahren
    #v_delta = simulate(4.663e+01,  2.184e+01,  5.455e+01,  9.744e+00, 5.136e-02,  3.376e-01,  3.754e+00,  2.332e+00)    # Differential-Evolution Verfahren

    #overstepping_voltage = simulate(1.086e+01,  1.438e+01,  1.007e+01,  1.153e+01,  4.957e-01, 4.325e-01,  1.691e+00,  2.687e+00)    # Standardverfahren
    overstepping_voltage = simulate(4.757e+01,  2.158e+01,  1.161e+01,  1.071e+01, 3.059e-01,  6.506e-01, 5.513e+00,  8.571e-01)    # Differential-Evolution Verfahren

