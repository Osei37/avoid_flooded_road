from math import floor
import pandas as pd
import glob
import re
import numpy as np
import libgsidem2el as gsi

# 道路ネットワークのノードの標高を求める
def main():
    path_osm = 'day14/OSM/bike/'
    
    dem = gsi.libgsidem2el('DEM5A')
    
    osm_folders = glob.glob(path_osm+'*')

    for osm_folder in osm_folders:
        osm_data = pd.read_csv(osm_folder+'/road_network_nodes.csv')
        osm_data['elevation'] = -1
        for idx, data in osm_data.iterrows():
            x = data['x']
            y = data['y']
            el = dem.getEL(x, y, zoom=15)
            osm_data['elevation'][idx] = el
            print(idx)
        osm_data.to_csv(osm_folder+'/road_network_nodes_elevation.csv', index=False)

if __name__ == '__main__':
    main()
