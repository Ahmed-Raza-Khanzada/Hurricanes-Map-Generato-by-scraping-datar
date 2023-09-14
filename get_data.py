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
def get_each_hurricane(match_id,year1 = "2023"):

  link = f"https://www.nhc.noaa.gov/gis/archive_forecast.php?year={year1}"
  df = pd.read_html(link)
  df  = df[0]
  new_header = df.iloc[0] 
  df = df[1:] 
  df.columns = new_header
  d = {}
  print(df.head())
  for id1,name1 in zip(df[df.columns[0]],df[df.columns[1]]):
      name2 ="%20".join(name1.split(" "))
      id2 = id1+year1
      url = f"https://www.nhc.noaa.gov/gis/archive_forecast_results.php?id={id1}&year={year1}&name={name2}"#name = Tropical%20Storm%20BRET
      if id1.lower() ==match_id.lower():
        zip_urls = []
        kmz_urls = []
        
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        urls = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                # full_url = url + href
                if href.endswith("Aadv_WW.kmz"):
                    kmz_urls.append("https://www.nhc.noaa.gov"+href[2:])
                elif href.endswith(".zip"):
                    zip_urls.append("https://www.nhc.noaa.gov/gis/"+href)
        d[id2] = {"kmz_urls":list(set(kmz_urls)),"zip_urls":list(set(zip_urls)),"name":name1}  
        
      # if len(kmz_urls):
      #   print(name1,id2)
      #   print(len(kmz_urls),kmz_urls)    
      #   print(len(zip_urls),zip_urls)
        
  return d
# d = get_each_hurricane(year1 = "2023")
      