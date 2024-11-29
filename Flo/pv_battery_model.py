
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class Battery:
    #def __init__(self, SoC=0, max_capacity=10):
    SoC:float = 0                     # Ladezustand in kWh
    max_capacity:float = 10             # Maximale Kapazität in kWh
    max_charge:float = 5                # Maximale Ladeleistung in kW
    max_discharge:float = 5             # Maximale Entladeleistung in kW
    time_full:float = 0                  # Zeit, in der die Batterie voll ist
    time_empty:float = 0                 # Zeit, in der die Batterie leer ist


    def charge(self, charge):
            if(charge <= self.max_charge):
                if((self.SoC + charge) >= self.max_capacity):
                    remaining_power = self.SoC + charge - self.max_capacity
                    self.SoC = self.max_capacity
                    self.time_full += 1
                    return remaining_power       # Jener Anteil der nicht geladen werden konnte
                
                elif((self.SoC + charge) < self.max_capacity):         # nicht notwendig
                    self.SoC = self.SoC + charge 
                    return 0                                        # Jener Anteil der nicht geladen werden konnte

            elif(charge > self.max_charge):
                if((self.SoC + self.max_charge) >= self.max_capacity):
                    remaining_power = self.SoC + charge - self.max_capacity
                    self.SoC = self.max_capacity
                    self.time_full += 1
                    return remaining_power       # Jener Anteil der nicht geladen werden konnte
                
                elif((self.SoC + self.max_charge) < self.max_capacity):     # nicht notwendig
                    self.SoC = self.SoC + self.max_charge
                    return 0                                        # Jener Anteil der nicht geladen werden konnte

            
            
    def discharge(self, charge):
            
            if(charge <= self.max_discharge):
                if((self.SoC - charge) <= 0):
                    remaining_power = charge - self.SoC 
                    self.SoC = 0
                    self.time_empty += 1
                    return remaining_power                          # Jener Anteil von Energie in kWh der nicht mehr entladen werden kann
                elif((self.SoC - charge) > 0):
                    self.SoC = self.SoC - charge
                    return 0                                        # Jener Anteil von Energie in kWh der nicht mehr entladen werden kann 
            
            elif(charge > self.max_discharge):
                if((self.SoC - self.max_discharge) <= 0):
                    remaining_power = charge - self.SoC
                    self.SoC = 0
                    self.time_empty += 1
                    return remaining_power                           # Jener Anteil von Energie in kWh der nicht mehr entladen werden kann
                elif((self.SoC - self.max_discharge) > 0):
                    self.SoC = self.SoC - self.max_discharge
                    return 0                                        # Jener Anteil von Energie in kWh der nicht mehr entladen werden kann 


def input_pv(filename):
    return np.genfromtxt(filename)

def pv_scale(PV_Unscaled, f):
    return PV_Unscaled*f

def pv(factor, filename_pv):
    pv_unscaled = input_pv(filename_pv)

    pv_scaled = pv_scale(pv_unscaled, factor)

    #df_pv_scaled = pd.DataFrame({"Leistung [kWp]": pv_scaled})

    return pv_scaled



if __name__ == "__main__":
    
    # PV-Daten laden
    pv_size = 20       # Göße der PV-Anlage in kWp
    filename_pv = "C:/Users/flori/EMS/EMS_Projekt/Flo/files/pv_1kWp.csv"    # r"...\...\"
    pv_scaled = pv(pv_size, filename_pv)      # PV-Anlage Daten einlesen

    # Batterie erstellen
    battery = Battery(SoC=0, max_capacity=12, max_charge=5, max_discharge=5)

    # Nachfrage festlegen
    constant_demand = 2         # Konstante Entladung in kWh

    time_period = 8760          # Anzahl der Stunden im Jahr -> muss mit den Anzahl der Zeilen vom Dataframe df_p_s zusammenpassen

    # Ergebnisse speichern
    SoC_over_time = np.zeros(time_period)
    PV_cutoff = np.zeros(time_period)
    Demand_cutoff = np.zeros(time_period)

    # Simulation
    for i in range(np.size(pv_scaled)):

        # Batterie Laden mit überschüssiger PV-Energie
        if((pv_scaled[i] - constant_demand) >= 0):
            charge_amount = pv_scaled[i] - constant_demand
            PV_cutoff[i] = battery.charge(charge_amount)
            SoC_over_time[i] = battery.SoC

        elif((pv_scaled[i] - constant_demand) < 0):
            discharge_amount = constant_demand - pv_scaled[i]
            Demand_cutoff[i] = battery.discharge(discharge_amount)
            SoC_over_time[i] = battery.SoC

    print("Full",battery.time_full)
    # Erstelle den Plot
    plt.figure(figsize=(12, 6))

    # PV-Energie
    plt.plot(pv_scaled, label="PV-Leistung", color="orange")

    # Ladezustand der Batterie (SoC)
    plt.plot(SoC_over_time, label="Ladezustand Batterie (SoC)", color="blue")

    # Überschüssige PV-Energie
    plt.plot(PV_cutoff, label="PV-Cutoff", color="purple")

    # Nicht vorhandene Energie
    plt.plot(Demand_cutoff, label="Demand-Cutoff", color="red")

    # Diagrammtitel und Achsenbeschriftungen
    plt.title("Simulationsergebnisse", fontsize=14)
    plt.xlabel("Zeit [Stunden]", fontsize=12)
    plt.ylabel("Energie [kWh]", fontsize=12)

    # Legende
    plt.legend(loc="upper right", fontsize=10)

    # Raster hinzufügen
    plt.grid(alpha=0.3)

    # Diagramm anzeigen
    plt.show()




