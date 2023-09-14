from get_data import get_each_hurricane
from get_hurricans import save_Map
from  make_folium_map import make_folium_data


def main(year1 = "2023",id1  = "al02"):
  data = get_each_hurricane(id1,year1)
  for id in data.keys():
      kmz_url  = data[id]["kmz_urls"]
      zip_url = data[id]["zip_urls"]
      name = data[id]["name"]
      #if you want all data of single hurrincane so you do loop instead of last(latest hurricane)
      if kmz_url:
        kmz_url = kmz_url[-1]
      else:
        kmz_url = False
      if zip_url:
        zip_url = zip_url[-1]
      try:
        gdf_wind_field,gdf_storm_points,gdf_storm_envelope_1,gdf_storm_line,gdf_winds,gdf_wwlin,do_wind,do_surge,lats,longs,outpath =   make_folium_data(id  ,name,
                                                                                                                            zip_url,
                                                                                                                            kmz_url )
        print(save_Map(gdf_wind_field,gdf_storm_points,gdf_storm_envelope_1,gdf_storm_line,gdf_winds,gdf_wwlin,do_wind,do_surge,lats,longs,outpath)._repr_html_())
      except Exception as e:
        print(f"Error in following Hurricane below {e} ")
        print(id,name)

if __name__ == "__main__":
  main(year1="2023",id1="al02")
