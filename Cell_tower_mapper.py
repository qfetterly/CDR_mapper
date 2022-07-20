import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import folium
import webbrowser


def read_excel(file):
    df = pd.read_excel(file, header=[11])
#                               ^column titles are in row 12 in Excel, but here starting with zero it's 11
    df = df.dropna(subset='1st Tower LAT')
#         ^drops rows without tower location
    df['Date'] = pd.to_datetime(df['Date'], utc=True)
    analysis(df)
    return df


def analysis(df):
    # KC = key columns idk
    KC = df[['Date', '1st Tower Address', '1st Tower LAT', '1st Tower LONG', '1st Tower Azimuth']]

    KC['TowerShift1'] = KC['1st Tower Address'].shift(-1)
    KC['TowerShift2'] = KC['1st Tower Address'].shift(1)
    KC['azimuthShift1'] = KC['1st Tower Azimuth'].shift(-1)
    KC['azimuthShift2'] = KC['1st Tower Azimuth'].shift(1)

    collapse1: any = KC[
        (KC['1st Tower Address'] != KC['TowerShift1']) |
        (KC['1st Tower Address'] != KC['TowerShift2']) ]
        # (KC['1st Tower Azimuth'] != KC['azimuthShift1']) |
        # (KC['1st Tower Azimuth'] != KC['azimuthShift2']

    tower_coords1 = collapse1[['1st Tower LAT', '1st Tower LONG', '1st Tower Azimuth']]\
        .drop_duplicates()
    # print("all towers", tower_coords1, "\n\n")
    within_Margin = collapse1[(collapse1['Date'] >= timerange[0]) &
                              (collapse1['Date'] <= timerange[1])]
    tower_coords2 = pd.DataFrame()
    if len(within_Margin) != 0:
        tower_coords2 = within_Margin[['Date', '1st Tower LAT', '1st Tower LONG', '1st Tower Azimuth', '1st Tower Address']]
        # print("within timeframe", tower_coords2, "\n\n")
        try:
            popups(tower_coords1, tower_coords2)
        except:
            make_map(tower_coords1, tower_coords2)
    else:
        make_map(tower_coords1, tower_coords2)
    return tower_coords1, tower_coords2


def popups(tower_coords1, tower_coords2):
    tower_coords2['Address Shift'] = tower_coords2['1st Tower Address'].shift(1)
    tower_coords2['string'] = ''
    for row in tower_coords2.iterrows():
        if tower_coords2[row, '1st Tower Address'] == tower_coords2[row, 'Address Shift']:
            tower_coords2[row, 'string'] = '- ' + tower_coords2[row, 'Date'].strftime("%m-%d %H:%M")
        else:
            tower_coords2[row, 'string'] = '\n' + tower_coords2[row, 'Date'].strftime("%m-%d %H:%M")
    print_sort2 = tower_coords2.groupby(tower_coords2['1st Tower Address'])['string'].apply(
        ' '.join).reset_index()
    make_map(tower_coords1, print_sort2)
    return print_sort2

def make_map(tower_coords1, print_sort2):
    map2 = folium.Map(
        location=[33.840208, -84.272767],
        # ^this is some random coord in the middle of the county
        tiles='cartodbpositron',
        # ^this is the map style
        zoom_start=12,
    )
    if coords:
        incident_location(coords[0], coords[1], map2)
    plot_all_towers(tower_coords1, map2)
    if len(print_sort2) != 0:
        plot_timeframe(print_sort2, map2)
    map2.save("map2.html")
    webbrowser.open("map2.html")
    #   ^I was lazy and just put new color circles on top of the old ones
    return map2


def incident_location(incident_LAT, incident_LONG, map2):
    folium.Circle(location=[incident_LAT, incident_LONG],
                  color='red',
                  radius=30).add_child(folium.Popup(Iloc.address)).add_to(map2)


def plot_all_towers(tower_coords1, map2):
    tower_coords1.apply(lambda row: folium.Circle(
        location=[row['1st Tower LAT'], row['1st Tower LONG']],
        radius=5,
        color='black',
        opacity=0.5
        ).add_to(map2), axis=1)
    tower_coords1.apply(lambda row: folium.Circle(
        location=[row['1st Tower LAT'], row['1st Tower LONG']],
        radius=1400,
        opacity=0.5
        ).add_to(map2), axis=1)


def plot_timeframe(print_sort2, map2):

    print_sort2.apply(lambda row: folium.Circle(
        location=[row['1st Tower LAT'], row['1st Tower LONG']],
        radius=1400,
        color='red',
        opacity=1,
        popup=row['string']
        ).add_to(map2), axis=1)


def main(file, loc, timerangein):
    global coords
    coords = []
    if loc:
        global Iloc
        Iloc = loc
        coords = [loc.latitude, loc.longitude]
    global timerange
    timerange = [pd.to_datetime(timerangein[0], utc=True), pd.to_datetime(timerangein[1], utc = True)]
    read_excel(file)