import plotly.graph_objs as go
from pv_battery_model_v2 import Battery


def spannungsplot(net, results_df, time):

    """
    Gibt einen Spannungsplot aus.

    :param net: Benötigt die Pandapower Netzwerk
    :param results_df: Benötigt den results Dataframe
    :param time: Die Zeitinstanz in der er Plot erstellt werden soll
    :return: Erstellt einen Plot
    """ 

    results_c = results_df.iloc[time]
    points = []
    distances = {}

    current = {'id': 'LV Bus', 'x': 0, 'y': results_c['voltage_bus_lv'], 'connected_to': None}
    points.append(current)
    distances['LV Bus']=0


    for i, line in net.line.iterrows():
        bus_c = net.bus.iloc[line['to_bus']]['name']
        bus_connected = net.bus.iloc[line['from_bus']]['name']
        dict_c = "voltage_bus_" + bus_c[1:].replace(".", "_")
        distance = distances[bus_connected] + line["length_km"]
        distances[bus_c] = distance
        #print(net.line.loc[1])
        current = {'id': bus_c, 'x': distance, 'y': results_c[dict_c], 'connected_to': bus_connected}
        points.append(current)

    ### Plotting
    # Prepare data for plotting
    x_coords = [point['x'] for point in points]
    y_coords = [point['y'] for point in points]
    labels = [point['id'] for point in points]

    # Create scatter plot of points
    trace_points = go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers',
        marker=dict(
            size=10,
            color='red',
            line=dict(width=2, color='DarkSlateGrey')
        ),
        text=labels,
        textposition='top center'
    )

    # Prepare connection lines
    connection_lines = []
    for point in points:
        if point['connected_to'] is not None:
            # Find the connected point
            connected_point = next(p for p in points if p['id'] == point['connected_to'])
            
            # Create a line trace
            line = go.Scatter(
                x=[point['x'], connected_point['x']],
                y=[point['y'], connected_point['y']],
                mode='lines',
                line=dict(color='blue', width=2),
                showlegend=False
            )
            connection_lines.append(line)

    # Combine all traces
    data = [trace_points] + connection_lines

    # Create the layout
    layout = go.Layout(
        title='Spannungsplot',
        xaxis=dict(title='Abstand'),
        yaxis=dict(title='Spannung [pU]'),
        hovermode='closest'
    )

    # Create figure and show
    fig = go.Figure(data=data, layout=layout)
    fig.show()

def battery_control(lv_bus_value, battery_soc, max_soc):
    # Initialisierung von charge_rate basierend auf battery_soc und lv_bus_value
    battery_soc = battery_soc * 100 / max_soc  # Umrechnung auf Skala von 0 bis 100
    threshold = False
    charge_rate = 0

    # Setze den Threshold nur, wenn sowohl der battery_soc als auch der lv_bus_value die Schwellenwerte überschreiten
    if battery_soc >=10 and lv_bus_value <= 0.975:
        return -1
    if battery_soc <=90 and lv_bus_value > 1:
        return 1
    '''
    if battery_soc >= 90 and lv_bus_value <= 1.03:
        threshold = True
    elif battery_soc >= 80 and battery_soc <= 90 and lv_bus_value <= 1.02333333:
        threshold = True
    elif battery_soc >= 70 and battery_soc <= 80 and lv_bus_value <= 1.02:
        threshold = True
    elif battery_soc >= 60 and battery_soc <= 70 and lv_bus_value <= 1.01666667:
        threshold = True
    elif battery_soc >= 50 and battery_soc <= 60 and lv_bus_value <= 1.00:
        threshold = True
    elif battery_soc >= 40 and battery_soc <= 50 and lv_bus_value >= 0.99666667:
        threshold = True
    elif battery_soc >= 30 and battery_soc <= 40 and lv_bus_value >= 0.99:
        threshold = True
    elif battery_soc >= 20 and battery_soc <= 30 and lv_bus_value >= 0.98333333:
        threshold = True
    elif battery_soc >= 10 and battery_soc <= 20 and lv_bus_value >= 0.97666667:
        threshold = True

    # Überprüfen, ob der Threshold erreicht wurde, und berechne charge_rate
    if threshold:
        if battery_soc >= 90:
            charge_rate = -0.90
        elif battery_soc >= 80:
            charge_rate = -0.77777778
        elif battery_soc >= 70:
            charge_rate = -0.55555556
        elif battery_soc >= 60:
            charge_rate = -0.33333333
        elif battery_soc >= 50:
            charge_rate = -0.0
        elif battery_soc >= 40:
            charge_rate = 0.11111111
        elif battery_soc >= 30:
            charge_rate = 0.33333333
        elif battery_soc >= 20:
            charge_rate = 0.55555556
        elif battery_soc <= 10:
            charge_rate = 0.77777778
        charge_rate = charge_rate * battery_soc / 100  # Skalierung auf den SOC-Wert
    else:
        # Berechne charge_rate auch für kleine SOC-Werte (z.B. 2, 3)
        if battery_soc < 10:
            charge_rate = 1 * (battery_soc / 10)  # Setze einen Wert nahe 1, abhängig von SOC
        elif battery_soc < 20:
            charge_rate = 0.5 * (battery_soc / 10)  # Lineare Steigerung bis 20% SOC
    '''
    return charge_rate

def get_index(net, type, name):
    to_exec = f"net.{type}[net.{type}[\"name\"] == \"{name}\"].index[0]"
    return eval(to_exec)

if __name__ == "__main__":
    #Batterie = Battery(0/1000, 500/1000, 25/1000, 25/1000)
    print(battery_control(0.8, 500, 1000))
