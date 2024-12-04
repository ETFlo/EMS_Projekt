import plotly.graph_objs as go

def spannungsplot(net, results_df, time):

    """
    Gibt einen Spannungsplot aus.

    :param net: Benötigt die Pandapower Netzwerk
    :param results_df: Benötigt das Results Dataframe
    :param time: Die Zeitinstanz in der er Plot erstellt werden soll
    :return: Erstellt einen Plot
    """ 

    results_c = results_df[time]
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