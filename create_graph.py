from tracemalloc import start
import pandas as pd
from rtree import index
import glob

def translate_geometry(geometry):
    # string to float list
    geometry = geometry.replace('LINESTRING', '')
    geometry = geometry.replace(' (', '[[')
    geometry = geometry.replace(')', ']]')
    geometry = geometry.replace(', ', '] [')
    geometry = geometry.replace(' ', ',')
    geometry_list = eval(geometry)
    # [[latitude, longitude],...]
    geometry_list_new = []
    for point in geometry_list:
        geometry_list_new.append([point[1], point[0]])
    return geometry_list_new

def main():
    
    path_osm = 'day14/app/data/OSM'
    path_folders = glob.glob(path_osm+'/**')
    
    print(path_folders)

    latlon_list = []
    new_edge_data = [] # [隣接行列の始点のidx，隣接行列の終点のidx，geometry]
    
    for path_folder in path_folders:
        print(path_folder)
        # if 'Hachioji' in path_folder:
        #     continue
        path_edges = path_folder+'/road_network_edges.csv'
        edge_data = pd.read_csv(path_edges)
        path_nodes = path_folder+'/road_network_nodes_elevation.csv'
        node_data = pd.read_csv(path_nodes)
        
        for idx, edge_ in edge_data.iterrows():
            # print(idx, '/', len(edge_data))
            edge_list = translate_geometry(edge_['geometry'])
            start_coord = edge_list[0]
            goal_coord = edge_list[-1]
            length = edge_['length']

            if start_coord not in latlon_list:
                start_idx = len(latlon_list)
                latlon_list.append(start_coord)
            else:
                start_idx = latlon_list.index(start_coord)

            if goal_coord not in latlon_list:
                goal_idx = len(latlon_list)
                latlon_list.append(goal_coord)
            else:
                goal_idx = latlon_list.index(goal_coord)

            new_edge_data.append([start_idx, goal_idx, length, edge_list])

    matrix = [[0] * len(latlon_list) for i in range(len(latlon_list))]

    for edge_ in new_edge_data:
        start = edge_[0]
        goal = edge_[1]
        weight = edge_[2]
        matrix[start][goal] = weight
        matrix[goal][start] = weight
    
    # 
    water_level_all = {}
    water_level = [-1]*len(latlon_list)

    for path_folder in path_folders:
        path_edges = path_folder+'/road_network_edges.csv'
        edge_data = pd.read_csv(path_edges)
        path_nodes = path_folder+'/road_network_nodes_elevation.csv'
        node_data = pd.read_csv(path_nodes)

        for idx, node_ in node_data.iterrows():
            water_level_all['['+str(node_['y'])+', '+str(node_['x'])+']'] = node_['elevation']
    
    for i, latlon in enumerate(latlon_list):
        # print(latlon)
        v = water_level_all[str(latlon)]
        if v=='e':
            v=-1
            print('e')
        water_level[i] = float(v)

    df_matrix = pd.DataFrame(matrix)
    df_matrix.to_csv(path_osm+'/matrix.csv', index=False)
    
    df_latlon_list = pd.DataFrame(latlon_list)
    df_latlon_list.to_csv(path_osm+'/latlon_list.csv', index=False)
    
    df_water_level = pd.DataFrame(water_level)
    df_water_level.to_csv(path_osm+'/water_level_list.csv', index=False)

if __name__ == '__main__':
    main()
