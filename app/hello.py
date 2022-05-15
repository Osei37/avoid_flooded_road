# Flaskとrender_template（HTMLを表示させるための関数）をインポート
from flask import Flask, render_template, request
import pandas as pd
from rtree import index
from scipy.sparse.csgraph import shortest_path
import numpy as np
import itertools
import copy

# global変数
start_point = ['', '']
goal_point = ['', '']
route = [['', ''], ['', '']]
start_idx = -1
goal_idx = -1
water_level = 0
sink_coord = []

# csv読み込み
graph_df = pd.read_csv("day14/app/data/OSM/Hino,Tokyo,Japan/matrix.csv")
graph = graph_df.values.tolist()
graph_col_df = pd.read_csv("day14/app/data/OSM/Hino,Tokyo,Japan/latlon_list.csv")
graph_col = graph_col_df.values.tolist()
nodes_df = pd.read_csv("day14/app/data/OSM/Hino,Tokyo,Japan/road_network_nodes_elevation.csv")
nodes = nodes_df.values.tolist()
elevation_df = pd.read_csv("day14/app/data/OSM/Hino,Tokyo,Japan/water_level_list.csv")
elevation = elevation_df.values.tolist()
elevation = list(itertools.chain.from_iterable(elevation))

rtree_idx = index.Index()

for idx, latlon in enumerate(graph_col):
    rtree_idx.insert(idx, (latlon[0], latlon[1]))


# Flaskオブジェクトの生成
app = Flask(__name__)

# ルーティング(URLと関数を紐付け)
# --「***/」or「***/index」へアクセスがあった場合
@app.route("/")
@app.route("/index.html")
def index():
    return render_template('index.html', route=route, start_point=start_point, goal_point=goal_point, nodes=nodes, start_nearest=start_idx, goal_nearest=goal_idx, water_level=water_level, sink=sink_coord)


# --「***/index」からPOSTリクエストが来た場合
@app.route("/index.html", methods=["POST"])
def index_post():
    global start_point, goal_point, route, rtree_idx, start_idx, goal_idx, water_level, graph, sink_coord
    if request.form["type"] == "View" or request.form["type"] == "Excute":
        if request.form["WaterLevel"] != '':
            water_level = float(request.form["WaterLevel"])
            sink_coord = []
            for idx, value in enumerate(elevation):
                if value < water_level:
                    sink_coord.append(graph_col[idx])

    elif request.form["type"] == "Excute":
        if request.form["StartLat"] != '' and request.form["StartLng"] != '' and request.form["GoalLat"] != '' and request.form["GoalLng"] != '' and request.form["WaterLevel"] != '':
            # 最近傍を探す
            start_point = [float(request.form["StartLat"]), float(request.form["StartLng"])]
            start_idx = list(rtree_idx.nearest((start_point[0], start_point[1]), 1))[0]
            goal_point = [float(request.form["GoalLat"]), float(request.form["GoalLng"])]
            goal_idx = list(rtree_idx.nearest((goal_point[0], goal_point[1]), 1))[0]

            # 水位が設定値以下のノードへの経路はなしにする
            water_level = float(request.form["WaterLevel"])
            sink_list = []
            for idx, value in enumerate(elevation):
                if value < water_level:
                    sink_list.append(idx)

            # 行列の接続を切る
            graph_tmp = copy.deepcopy(graph)
            
            for sink in sink_list:
                sink_coord.append(graph_col[sink])
                for idx in range(len(graph_tmp)):
                    graph_tmp[sink][idx] = 0
                    graph_tmp[idx][sink] = 0

            graph_np = np.array(graph_tmp)
            d, p = shortest_path(graph_np, return_predecessors=True, method='D')
            order = get_path(start_idx, goal_idx, p)
            order = [graph_col[i] for i in order]
            route = order

    elif request.form["type"] == "Reset":
        route = [['', ''], ['', '']]
        start_point = ['', '']
        goal_point = ['', '']

        start_idx = -1
        goal_idx = -1
        water_level = 0
        sink_coord = []

    return render_template('index.html', route=route, start_point=start_point, goal_point=goal_point, nodes=nodes, start_nearest=graph_col[start_idx], goal_nearest=graph_col[goal_idx], water_level=water_level, sink=sink_coord)


def get_path(start, goal, pred):
    return get_path_row(start, goal, pred[start])


def get_path_row(start, goal, pred_row):
    path = []
    i = goal
    while i != start and i >= 0:
        path.append(i)
        i = pred_row[i]
    if i < 0:
        return []
    path.append(i)
    return path[::-1]


if __name__ == '__main__':
    app.run(debug=True)
