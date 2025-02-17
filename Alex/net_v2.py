import pandapower as pp
import pandapower.plotting as plot
import numpy as np
import pandas as pd
import pv_battery_model_v2 as pv_battery_model
import matplotlib.pyplot as plt
from plotfunktion import spannungsplot, battery_control, get_index
import pickle
import plotly.express as px

def create_net():
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
    filename_pv = "./Flo/files/RESProfile.csv"  # Daten liegen in 1/4 h Zeitschritten vor
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
    pv_4_data_x = 5 * pv_3_data
    """ -------- """

    """ LAST DATEN """
    #Last Daten einlesen
    filename_load = "./Flo/files/LoadProfile.csv"  # Daten liegen in 1/4 h Zeitschritten vor
    load_data = pd.read_csv(filename_load, delimiter=";", parse_dates=["time"], index_col="time")

    last1 = 10 * load_data["H0-A_pload"].values / 1000
    last2 = 20 * load_data["G2-A_pload"].values / 1000
    last3 = 15 * load_data["H0-B_pload"].values / 1000
    last4 = 10 * load_data["G3-A_pload"].values / 1000
    """ --------- """

    """ BATTERIE """
    #b_2_2_2_2 = pv_battery_model.Battery(0/1000, 500/1000, 25/1000, 25/1000)
    """ --------- """


    # Simulation über alle Zeitschritte -> ein Zeitschritt ist aufgrund 
    for t in range(600):

        pv_power = pv_4_data_x[t]
            
                
        # PV-Daten zuweisen
        net.sgen.at[get_index(net, "sgen", "E1.1"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2.1.1"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2.1.2"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2.2.1"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2.2.2"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.1"), "p_mw"] = pv_2_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2"), "p_mw"] = pv_2_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2.1.1"), "p_mw"] = pv_3_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2.1.2"), "p_mw"] = pv_3_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2.2.1"), "p_mw"] = pv_3_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2.2.2"), "p_mw"] = abs(pv_power)
        #net.sgen.at[e_2_2_2_2, "q_mw"] = remaining_pv * 0.2

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
            pp.runpp(net, max_iter=1500, numba=False)
        except pp.pandapower.powerflow.LoadflowNotConverged:
            print("Lastfluss nicht konvergiert!")
            print("Knotenspannungen:")
            print(net.res_bus)
            print("Leitungsbelastungen:")
            print(net.res_line)
        

        '''
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
        '''

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


    # Ergebnisse in DataFrame umwandeln
    results_df = pd.DataFrame(results)
    print(results_df.head())
    #breakpoint()

    # Lastfluss-Berechnung 
    #pp.runpp(net)

    load_results = net.res_load.join(net.load["name"], how='left')
    # print(load_results)
    with open('./Alex/simulation/base_net.pkl', 'wb') as file:
        pickle.dump(net, file)
    with open('./Alex/simulation/base_results.pkl', 'wb') as file:
        pickle.dump(results_df, file)
    return net, results_df

def simulate_net(location):
    
    with open('./Alex/simulation/base_net.pkl', 'rb') as file:
        net = pickle.load(file)
    with open('./Alex/simulation/base_results.pkl', 'rb') as file:
        results_df = pickle.load(file)

    gen_location = location.replace("voltage_bus_", "E")
    gen_location = gen_location.replace("_", ".")

    load_location = location.replace("voltage_bus_", "L")
    load_location = load_location.replace("_", ".")

    # PV Daten einlesen
    filename_pv = "./Flo/files/RESProfile.csv"  # Daten liegen in 1/4 h Zeitschritten vor
    pv_data = pd.read_csv(filename_pv, delimiter=";", parse_dates=["time"], index_col="time")

    # Extrahiere die PV-Daten (Spalten: PV5, PV6, PV8)
    pv_1_raw_data = pv_data["PV1"].values  # Rohwerte ohne Umrechnung
    pv_2_raw_data = pv_data["PV3"].values
    pv_3_raw_data = pv_data["PV4"].values

    pv_1_data = pv_battery_model.pv_scale(pv_1_raw_data, 50) / 1000
    pv_2_data = pv_battery_model.pv_scale(pv_2_raw_data, 30) / 1000
    pv_3_data = pv_battery_model.pv_scale(pv_3_raw_data, 20) / 1000
    pv_4_data_x = 5 * pv_3_data

    """ LAST DATEN """
    #Last Daten einlesen
    filename_load = "./Flo/files/LoadProfile.csv"  # Daten liegen in 1/4 h Zeitschritten vor
    load_data = pd.read_csv(filename_load, delimiter=";", parse_dates=["time"], index_col="time")

    last1 = 10 * load_data["H0-A_pload"].values / 1000
    last2 = 20 * load_data["G2-A_pload"].values / 1000
    last3 = 15 * load_data["H0-B_pload"].values / 1000
    last4 = 10 * load_data["G3-A_pload"].values / 1000
    """ --------- """
    
    max_charge_rate = 25/1000
    cap = 10000/1000
    soc = 0.5
    batterie = pv_battery_model.Battery(soc*cap, cap, max_charge_rate, max_charge_rate)
    batterie_soc = []

    for t in range(600):
        batterie_soc.append(batterie.SoC)
        spannung = results_df.iloc[t][location]
        charge = battery_control(spannung, batterie.SoC, cap)
        if charge == 0:
            #if spannung >1:
            #    breakpoint()
            continue

        pv_power = pv_4_data_x[t]
            
                
        # PV-Daten zuweisen
        net.sgen.at[get_index(net, "sgen", "E1.1"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2.1.1"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2.1.2"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2.2.1"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E1.2.2.2"), "p_mw"] = pv_1_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.1"), "p_mw"] = pv_2_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2"), "p_mw"] = pv_2_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2.1.1"), "p_mw"] = pv_3_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2.1.2"), "p_mw"] = pv_3_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2.2.1"), "p_mw"] = pv_3_data[t]
        net.sgen.at[get_index(net, "sgen", "E2.2.2.2"), "p_mw"] = abs(pv_power)
        #net.sgen.at[e_2_2_2_2, "q_mw"] = remaining_pv * 0.2

        #Lasten zuweisen
        net.load.at[get_index(net, "load", "L1.1"), "p_mw"] = last1[t]
        net.load.at[get_index(net, "load", "L1.2"), "p_mw"] = last2[t]
        net.load.at[get_index(net, "load", "L1.2.1.1"), "p_mw"] = last3[t]
        net.load.at[get_index(net, "load", "L1.2.1.2"), "p_mw"] = last2[t]
        net.load.at[get_index(net, "load", "L1.2.2.1"), "p_mw"] = last2[t]
        net.load.at[get_index(net, "load", "L1.2.2.2"), "p_mw"] = last1[t]
        net.load.at[get_index(net, "load", "L2.1"), "p_mw"] = last1[t]
        net.load.at[get_index(net, "load", "L2.2"), "p_mw"] = last2[t]
        net.load.at[get_index(net, "load", "L2.2.1.1"), "p_mw"] = last3[t]
        net.load.at[get_index(net, "load", "L2.2.1.2"), "p_mw"] = last2[t]
        net.load.at[get_index(net, "load", "L2.2.2.1"), "p_mw"] = last2[t]
        net.load.at[get_index(net, "load", "L2.2.2.2"), "p_mw"] = last1[t]

        if charge < 0:
            net.sgen.at[get_index(net, "sgen", gen_location), "p_mw"] += min(max_charge_rate, abs(batterie.charge(charge,1))) #TODO: Batteriemodell anpassen
        elif charge > 0:
            net.load.at[get_index(net, "load", load_location), "p_mw"] += min(max_charge_rate, abs(batterie.charge(charge,1)))
            #breakpoint()
        else:
            print("Fehler: charge macht keinen Sinn")

        #breakpoint()
        
        # zum prüfen des Netzes, bei einer Fehlermeldung
        try:
            pp.runpp(net, max_iter=1500, numba=False)
        except pp.pandapower.powerflow.LoadflowNotConverged:
            print("Lastfluss nicht konvergiert!")
            print("Knotenspannungen:")
            print(net.res_bus)
            print("Leitungsbelastungen:")
            print(net.res_line)
            breakpoint()


        # Ergebnisse speichern
        results = {
            "time": t,
            "voltage_bus_lv": net.res_bus.at[get_index(net, "bus", "LV Bus"), "vm_pu"],
            "voltage_bus_1_1": net.res_bus.at[get_index(net, "bus", "v1.1"), "vm_pu"],
            "voltage_bus_1_2": net.res_bus.at[get_index(net, "bus", "v1.2"), "vm_pu"],
            "voltage_bus_1_2_1_1": net.res_bus.at[get_index(net, "bus", "v1.2.1.1"), "vm_pu"],
            "voltage_bus_1_2_1_2": net.res_bus.at[get_index(net, "bus", "v1.2.1.2"), "vm_pu"],
            "voltage_bus_1_2_2_1": net.res_bus.at[get_index(net, "bus", "v1.2.2.1"), "vm_pu"],
            "voltage_bus_1_2_2_2": net.res_bus.at[get_index(net, "bus", "v1.2.2.2"), "vm_pu"],
            "voltage_bus_2_1": net.res_bus.at[get_index(net, "bus", "v2.1"), "vm_pu"],
            "voltage_bus_2_2": net.res_bus.at[get_index(net, "bus", "v2.2"), "vm_pu"],
            "voltage_bus_2_2_1_1": net.res_bus.at[get_index(net, "bus", "v2.2.1.1"), "vm_pu"],
            "voltage_bus_2_2_1_2": net.res_bus.at[get_index(net, "bus", "v2.2.1.2"), "vm_pu"],
            "voltage_bus_2_2_2_1": net.res_bus.at[get_index(net, "bus", "v2.2.2.1"), "vm_pu"],
            "voltage_bus_2_2_2_2": net.res_bus.at[get_index(net, "bus", "v2.2.2.2"), "vm_pu"]
        }
        results_df.iloc[t] = pd.Series(results)

    return net, results_df, batterie_soc


if __name__ == "__main__":
    
    
    #net, results_df = create_net()

    net, results_df, batterie_soc = simulate_net("voltage_bus_1_2_2_2")

    # Ergebnisse speichern in eine CSV Datei
    #results_df.to_csv("C:/Users/flori/EMS/EMS_Projekt/Flo/files/typical_pv_results.csv", index=False)
    #breakpoint()

    plot.simple_plot(net, show_plot=True, plot_gens=True, plot_loads=True, plot_sgens=True)


    # Spannungen plotten
    plt.figure(2,figsize=(12, 6))
    plt.plot(results_df["time"], results_df["voltage_bus_lv"], label="LV Bus")
    plt.plot(results_df["time"], results_df["voltage_bus_1_1"], label="Bus 1-1")
    plt.plot(results_df["time"], results_df["voltage_bus_1_2_1_2"], label="Bus 1-2-1-2")
    plt.plot(results_df["time"], results_df["voltage_bus_2_2"], label="Bus 2-2")
    plt.plot(results_df["time"], results_df["voltage_bus_2_2_2_2"], label="Bus 2-2-2-2")

    # Titel, Labels und Legende
    plt.title("Spannungsverlauf an verschiedenen Knoten")
    plt.xlabel("Zeit")
    plt.ylabel("Spannung [p.u.]")
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.plot(batterie_soc)
    plt.show()

    # Weg/Spannungs - Diagramm
    spannungsplot(net, results_df, 524)
    spannungsplot(net, results_df, 560)
    spannungsplot(net, results_df, 565)
    spannungsplot(net, results_df, 570)

    results2 = results_df.drop('time', axis=1)
    fig = px.imshow(results2.T)
    fig.show()

