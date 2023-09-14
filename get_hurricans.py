import pandas as pd
import requests
from bs4 import BeautifulSoup
import time 
import matplotlib.pyplot as plt
import datetime
import folium
from folium import plugins
import geopandas as gpd
import fiona
from shapely.geometry import Polygon, box
import numpy as np
import pandas as pd

import re
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

import shutil
from pathlib import Path

import matplotlib.colors as colors
import matplotlib.cm as cmx

pd.set_option('display.max_columns', None)

# df.head()
def save_Map(gdf_wind_field,gdf_storm_points,gdf_storm_envelope_1,gdf_storm_line,gdf_winds,gdf_wwlin,do_wind,do_surge,lats,longs,pathStr):
    cm = plt.get_cmap('RdYlGn_r')#'Spectral_r')
    cNorm  = colors.Normalize(vmin=0, vmax=11)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
    folium_map = folium.Map(location=[lats[0],longs[0]], zoom_start=4)#, tiles="CartoDB positron")

    #-------------------------

    g_storm_track = folium.map.FeatureGroup(name="Storm Track", overlay=True, control=True, show=True)
    g_eye_zone = folium.map.FeatureGroup(name="Eye Zone", overlay=True, control=True, show=True)
    g_surge = folium.map.FeatureGroup(name="Storm Surge", overlay=True, control=True, show=True)
    g_wind = folium.map.FeatureGroup(name="Wind Arrival Times", overlay=True, control=True, show=False)

    g_wind_prob_34 = folium.map.FeatureGroup(name="Wind Prob 34kt", overlay=True, control=True, show=False)
    g_wind_prob_50 = folium.map.FeatureGroup(name="Wind Prob 50kt", overlay=True, control=True, show=False)
    g_wind_prob_64 = folium.map.FeatureGroup(name="Wind Prob 64kt", overlay=True, control=True, show=False)

    #-------------------------

    name = 'Artemis 1 Launchpad 39B'
    folium_map.add_child(
        folium.Marker(
            location=[28.6272, -80.6208],
            popup=name,
            tooltip=name
        )
    )

    #-------------------------

    track_color = 'purple'
    marker_color = 'purple'
    eye_zone_color = 'purple'
    surge_color = 'blue'
    wind_arrival_color = 'purple'

    #------------------------- lines around shores and islands

    if do_surge:
        g_surge.add_child(
            folium.features.GeoJson(
                gdf_wwlin,
                tooltip = 'Storm Surge',
                style_function=lambda feature: {
                    'color' : surge_color,
                    'weight' : 4,
                    'fillOpacity' : 0.3
                }
            )
        )

    #------------------------- a line

    g_storm_track.add_child(
        folium.features.GeoJson(
            gdf_storm_line,
            style_function=lambda feature: {
                'color' : track_color,
                'weight' : 2,
                'fillOpacity' : 0.2
            }
        ))

    #------------------------- an envelope

    g_eye_zone.add_child(
        folium.features.GeoJson(
            gdf_storm_envelope_1,
            style_function=lambda feature: {
                'fillColor': eye_zone_color,
                'color' : eye_zone_color,
                'weight' : 2,
                'fillOpacity' : 0.1
            }
        ))

    #------------------------- colored circles

    storm_label = ['D', 'S', 'H', 'M']
    storm_color = ['green', 'yellow', 'orange', 'red']

    for idx, row in gdf_storm_points.iterrows():
        tooltip_text = 'Date: ' + row.FLDATELBL \
        + '<br>Strength: ' + row.TCDVLP \
        + '<br>Max wind: ' + str(row.MAXWIND) \
        + '<br>Gust: ' + str(row.GUST)

        try:
            sIndex = storm_label.index(row.DVLBL)
            sColor = storm_color[sIndex]
            sRadius = 8 + 2*(sIndex + 1)
        except:
            sColor = 'black'
            sRadius = 100


        marker = folium.CircleMarker(
            [row.LAT, row.LON],
            radius=sRadius,
            color=sColor,
            fill=True,
            fill_opacity=0.5,
            weight=2,
            tooltip = tooltip_text)
        g_storm_track.add_child(marker)

    #-------------------------

    if do_wind:
        g_wind.add_child(
            folium.features.GeoJson(
                gdf_winds,
                tooltip = folium.features.GeoJsonTooltip(fields=['Description'], aliases=['Wind arrives:']),
                style_function=lambda feature: {
                    'color' : wind_arrival_color,
                    'weight' : 2,
                    'fillOpacity' : 0.3
                }
            )
        )

    #-------------------------

    def styler(feature):
        p = int(feature['id'])#feature['properties']['PERCENTAGE']
        if p < 0:
            p = -1
        if p < 0:
            fill_opacity = 0
            line_weight = 0
        else:
            fill_opacity = 0.3
            line_weight = 2
        color_string = colors.to_hex(scalarMap.to_rgba(float(p)))
        return {
            'fillColor': color_string,
            'color' : color_string,
            'weight' : line_weight,
            'fillOpacity' : fill_opacity
        }

    g_wind_prob_34.add_child(
        folium.features.GeoJson(
            gdf_wind_field[0][gdf_wind_field[0]['geometry'] != None],
            tooltip = folium.features.GeoJsonTooltip(fields=['PERCENTAGE'], aliases=['Prob 34 knot winds:']),
            style_function=styler
        )
    )

    g_wind_prob_50.add_child(
        folium.features.GeoJson(
            gdf_wind_field[1][gdf_wind_field[1]['geometry'] != None],
            tooltip = folium.features.GeoJsonTooltip(fields=['PERCENTAGE'], aliases=['Prob 50 knot winds:']),
            style_function=styler
        )
    )

    g_wind_prob_64.add_child(
        folium.features.GeoJson(
            gdf_wind_field[2][gdf_wind_field[2]['geometry'] != None],
            tooltip = folium.features.GeoJsonTooltip(fields=['PERCENTAGE'], aliases=['Prob 64 knot winds:']),
            style_function=styler
        )
    )

    #-------------------------

    if do_surge:
        folium_map.add_child(g_surge)
    folium_map.add_child(g_eye_zone)
    folium_map.add_child(g_wind_prob_34)
    folium_map.add_child(g_wind_prob_50)
    folium_map.add_child(g_wind_prob_64)
    if do_wind:
        folium_map.add_child(g_wind)
    folium_map.add_child(g_storm_track)

    #-------------------------

    folium.LayerControl(collapsed=False).add_to(folium_map)

    #-------------------------

    # folium_map
    outMap = pathStr / (str(pathStr) + "_Projected_Path.html")
    # folium_map.save(str(outMap))
    return folium_map
