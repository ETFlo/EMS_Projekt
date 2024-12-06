import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class Battery:
    #def __init__(self, SoC=0, max_capacity=10):
    SoC:float = 0 / 1000                     # Ladezustand in kWh
    max_capacity:float = 10 / 1000           # Maximale Kapazität in kWh
    max_charge:float = 5 / 1000              # Maximale Ladeleistung in kW
    max_discharge:float = 5 / 1000           # Maximale Entladeleistung in kW
    time_full:float = 0                      # Zeit, in der die Batterie voll ist
    time_empty:float = 0                     # Zeit, in der die Batterie leer ist

    

    def charge(self, power, time):           # Lädt wenn charge positiv und entlädt wenn charge negativ

        """
        Gibt eine Lade-/Entladeleistung zurück, welche für das Netz zu Verfügung stellt in der Zeitspanne time

        :param charge: Jene Leistung in MW, die in einer bestimmten Zeitspanne auftritt
        :param time: Zeitspanne in h
        :return: Ladeleistung positiv, Entladeleistung negativ in MW
        """ 

        charge = power * time
        max_charge_time = self.max_charge * time
        max_discharge_time = self.max_discharge * time

        sum = self.SoC + charge

        if charge >= 0:
            self.SoC = min(self.SoC + charge, self.max_capacity, self.SoC + max_charge_time)    # Finde neue SoC beim Laden
            sum = sum - self.SoC                                                                   # sum -> Jener Wert der nicht in die Batterie geladen werden konnte
        else:
            self.SoC = max(self.SoC + charge, 0, self.SoC - max_discharge_time)                 # Finde neue SoC beim Entladen
            sum = self.SoC - sum + charge                                                          # sum -> Jener Wert den die Batterie entlädt, also den Netz zu Verfügung stellt -> <= 0
        match self.SoC:             # Erhöhe Leer oder Voll wenn SoC gleich 0 oder max capacity erreicht wurde
            case 0:
                self.time_empty += 1
            case self.max_capacity:
                self.time_full += 1
        return (sum / time)


    def charge_full(self, charge):           # Lädt wenn charge positiv und entlädt wenn charge negativ
            remaining_power = self.SoC + charge
            if charge >= 0:
                self.SoC = min(self.SoC + charge, self.max_capacity, self.SoC + self.max_charge)    # Finde neue SoC beim Laden
                remaining_power = remaining_power - self.SoC
            else:
                self.SoC = max(self.SoC + charge, 0, self.SoC - self.max_discharge)                 # Finde neue SoC beim Entladen
                remaining_power = self.SoC - remaining_power
            match self.SoC:             # Erhöhe Leer oder Voll wenn SoC gleich 0 oder max capacity erreicht wurde
                case 0:
                      self.time_empty += 1
                case self.max_capacity:
                      self.time_full += 1
            return remaining_power
    
    # der übergebene parameter "charge", ist ein Energiewert in kWh für eine Viertelstunde
    def charge_quarter(self, charge):           # Lädt wenn charge positiv und entlädt wenn charge negativ
            
            remaining_power = self.SoC + charge

            max_charge_quarter = self.max_charge / 4
            max_discharge_quarter = self.max_discharge / 4

            if charge >= 0:
                self.SoC = min(self.SoC + charge, self.max_capacity, self.SoC + max_charge_quarter)    # Finde neue SoC beim Laden
                remaining_power = remaining_power - self.SoC
            else:
                self.SoC = max(self.SoC + charge, 0, self.SoC - max_discharge_quarter)                 # Finde neue SoC beim Entladen
                remaining_power = self.SoC - remaining_power
            match self.SoC:             # Erhöhe Leer oder Voll wenn SoC gleich 0 oder max capacity erreicht wurde
                case 0:
                      self.time_empty += 1
                case self.max_capacity:
                      self.time_full += 1
            return remaining_power 

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
    filename_pv = r"C:\Users\andre\Desktop\MEE\Semester 1\EMS-Project\GIT-repository\EMS_Projekt\Flo\files\pv_1kWp.csv"    # r"...\...\"
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
        charge_amount = pv_scaled[i] - constant_demand
        if((pv_scaled[i] - constant_demand) >= 0):
            PV_cutoff[i] = battery.charge(charge_amount)
        else:
            Demand_cutoff[i] = battery.charge(charge_amount) 
        SoC_over_time[i] = battery.SoC

    print("Full",battery.time_full)
    print("Empty",battery.time_empty)
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