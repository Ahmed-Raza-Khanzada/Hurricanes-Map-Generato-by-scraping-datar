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

def make_folium_data(storm  ,storm_name,zipurl,kmzurl = False):
    # storm = 'al09023'
    # storm_name = 'TS Harold'
    # try:
    #   !rm -rf 'noaa_data'
    # except:
    #   pass
    sdir = Path('noaa_data')
    if sdir.is_dir():
        shutil.rmtree(sdir)
    sdir.mkdir()

    # zipurl = f'https://www.nhc.noaa.gov/gis/forecast/archive/al092023_5day_006.zip'


    subFolder = sdir / zipurl.split("/")[-1].split(".")[0]
    with urlopen(zipurl) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall(subFolder)
    print(subFolder)

    for file in subFolder.glob('*_5day_lin.shp'):
        track_line = file
        break


    t = str(track_line)
    t_s = storm + '-'
    t_e = '_5day_lin.shp'
    gen = t[t.find(t_s)+len(t_s):t.rfind(t_e)]

    dateStr = datetime.datetime.today().strftime('%Y%m%d') + f'_{gen}_{storm_name}'
    pathStr = Path(dateStr)
    # Create the output directory for this storm prediction run.
    # if pathStr.is_dir():
    #     print ("Directory '%s' already exists" % pathStr)
    # else:
    #     try:
    #         pathStr.mkdir()
    #     except OSError:
    #         print ("Failed to create directory '%s'" % pathStr)
    #     else:
    #         print ("Created directory '%s'" % pathStr)



    epsg_project = 'EPSG:9311'
    epsg_folium = 'EPSG:4326'


    gdf_storm_line = gpd.read_file(track_line)
    gdf_storm_line.crs = epsg_folium

    for file in subFolder.glob('*_5day_pts.shp'):
        track_pts = file
        break
    gdf_storm_points = gpd.read_file(track_pts)
    gdf_storm_points.crs = epsg_folium
    print(dateStr)

    for file in subFolder.glob('*_5day_pgn.shp'):
        track_env = file
        break
    gdf_storm_envelope_1 = gpd.read_file(track_env)
    gdf_storm_envelope_1.crs = epsg_folium

    def getXY(pt):
        return (pt.x, pt.y)

    gdf_storm_envelope_1['geometry'].crs = epsg_project
    centroidseries = gdf_storm_envelope_1['geometry'].centroid
    gdf_storm_envelope_1['geometry'].crs = epsg_folium

    longs,lats = [list(t) for t in zip(*map(getXY, centroidseries))]


    do_surge = False

    for file in subFolder.glob('*_ww_wwlin.shp'):
        track_surge = file
        # display(track_surge)
        do_surge = True
        break
    else:
        print('No surge data')
    print('do_surge = ', do_surge)

    try:
        gdf_wwlin = gpd.read_file(track_surge)
        gdf_wwlin.crs = epsg_folium
        # gdf_wwlin.plot()
    except:
        do_surge = False
    # print(do_surge)

    do_wind = False

    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    # zipurl = f'https://www.nhc.noaa.gov/storm_graphics/api/{storm.upper()}_034Aadv_WW.kmz'
    if kmzurl:

      do_wind = True
      outKML = Path(sdir / str(storm.upper() + '_kml/'))
      with urlopen(kmzurl) as zipresp:
          with ZipFile(BytesIO(zipresp.read())) as zfile:
              zfile.extractall(outKML)


      for file in outKML.glob('*.kml'):
          inKML = file
          break

      gdf_winds = gpd.read_file(inKML, driver='KML')
      gdf_winds = gdf_winds[gdf_winds['geometry'].geom_type == 'LineString']


      gdf_winds['Description'] = gdf_winds['Description'].apply(lambda x: re.sub('<[^<]+?>', '', x).strip())
      gdf_winds.reset_index(drop=True, inplace=True)

      pathStr / (str(pathStr) + "_Projected_Path.html")
    windzipurl = 'https://www.nhc.noaa.gov/gis/forecast/archive/wsp_120hr5km_latest.zip'
    # print(windzipurl)
    windDir =  sdir / 'wsp_120hr5km_latest'
    with urlopen(windzipurl) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall(windDir)
    wind_file = []
    for file in windDir.glob('*knt*.shp'):
      wind_file.append(file)
    wind_file.sort()
    wind_file
    gdf_wind_field = []
    for f in wind_file:
        gwf = gpd.read_file(f)
        gwf.crs = epsg_folium
        gdf_wind_field.append(gwf)
        # gwf.plot()
    gdf_wind_field[0]
    if kmzurl:
      if do_surge:
        return gdf_wind_field,gdf_storm_points,gdf_storm_envelope_1,gdf_storm_line,gdf_winds,gdf_wwlin,do_wind,do_surge,lats,longs,pathStr
      else:
         return gdf_wind_field,gdf_storm_points,gdf_storm_envelope_1,gdf_storm_line,gdf_winds,None,do_wind,do_surge,lats,longs,pathStr
    if do_surge:
      return gdf_wind_field,gdf_storm_points,gdf_storm_envelope_1,gdf_storm_line,False,gdf_wwlin,do_wind,do_surge,lats,longs,pathStr
    else:
        return gdf_wind_field,gdf_storm_points,gdf_storm_envelope_1,gdf_storm_line,False,None,do_wind,do_surge,lats,longs,pathStr




