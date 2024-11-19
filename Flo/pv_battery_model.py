
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Battery:
    def __init__(self, SoC=0, max_capacity=10):
        self.SoC = SoC                      # Ladezustand in kWh
        self.max_capacity = max_capacity    # Maximale Kapazität in kWh
        self.max_charge = 5                 # Maximale Ladeleistung in kW
        self.max_discharge = 5              # Maximale Entladeleistung in kW
        self.time_full = 0                  # Zeit, in der die Batterie voll ist
        self.time_empty = 0                 # Zeit, in der die Batterie leer ist

    def charge(self, kWh):
            if(kWh <= self.max_charge):
                if((self.SoC + kWh) >= self.max_capacity):
                    remaining_power = self.SoC + kWh - self.max_capacity
                    self.SoC = self.max_capacity
                    self.time_full += 1
                    return remaining_power       # Jener Anteil der nicht geladen werden konnte
                
                elif((self.SoC + kWh) < self.max_capacity):
                    self.SoC = self.SoC + kWh 
                    return 0                                        # Jener Anteil der nicht geladen werden konnte

            elif(kWh > self.max_charge):
                if((self.SoC + self.max_charge) >= self.max_capacity):
                    remaining_power = self.SoC + kWh - self.max_capacity
                    self.SoC = self.max_capacity
                    self.time_full += 1
                    return remaining_power       # Jener Anteil der nicht geladen werden konnte
                
                elif((self.SoC + self.max_charge) < self.max_capacity):
                    self.SoC = self.SoC + self.max_charge
                    return 0                                        # Jener Anteil der nicht geladen werden konnte

            
            
    def discharge(self, kWh):
            
            if(kWh <= self.max_discharge):
                if((self.SoC - kWh) <= 0):
                    remaining_power = kWh - self.SoC 
                    self.SoC = 0
                    self.time_empty += 1
                    return remaining_power                          # Jener Anteil von Energie in kWh der nicht mehr entladen werden kann
                elif((self.SoC - kWh) > 0):
                    self.SoC = self.SoC - kWh
                    return 0                                        # Jener Anteil von Energie in kWh der nicht mehr entladen werden kann 
            
            elif(kWh > self.max_discharge):
                if((self.SoC - self.max_discharge) <= 0):
                    remaining_power = kWh - self.SoC
                    self.SoC = 0
                    self.time_empty += 1
                    return remaining_power                           # Jener Anteil von Energie in kWh der nicht mehr entladen werden kann
                elif((self.SoC - self.max_discharge) > 0):
                    self.SoC = self.SoC - kWh
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
    pv_size = 70       # Göße der PV-Anlage in kWp
    filename_pv = "C:/Users/flori/EMS/EMS_Projekt/Flo/files/pv_1kWp.csv"    # r"...\...\"
    pv_scaled = pv(pv_size, filename_pv)      # PV-Anlage Daten einlesen

    # Batterie erstellen
    battery = Battery(SoC=0, max_capacity=100)

    # Nachfrage festlegen
    constant_demand = 3    # Konstante Entladung in kWh

    time_period = 8760      # Anzahl der Stunden im Jahr -> muss mit den Anzahl der Zeilen vom Dataframe df_p_s zusammenpassen

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




