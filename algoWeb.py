from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from queue import PriorityQueue
import random
import numpy as np

app = Flask(__name__)
CORS(app)

ROWS = 40


class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.neighbors = []
        self.distance = float("inf")
        self.g_score = float("inf")
        self.f_score = float("inf")
        self.previous = None
        self.type = "empty"

    def __lt__(self, other):
        return False


def make_grid():
    grid = []
    for i in range(ROWS):
        grid.append([])
        for j in range(ROWS):
            node = Node(i, j)
            grid[i].append(node)
    return grid


def get_neighbors(node, grid):
    neighbors = []
    if node.row < ROWS - 1 and grid[node.row + 1][node.col].type != "wall":
        neighbors.append(grid[node.row + 1][node.col])
    if node.row > 0 and grid[node.row - 1][node.col].type != "wall":
        neighbors.append(grid[node.row - 1][node.col])
    if node.col < ROWS - 1 and grid[node.row][node.col + 1].type != "wall":
        neighbors.append(grid[node.row][node.col + 1])
    if node.col > 0 and grid[node.row][node.col - 1].type != "wall":
        neighbors.append(grid[node.row][node.col - 1])
    return neighbors


def heuristic(a, b):
    return abs(a.row - b.row) + abs(a.col - b.col)


def reconstruct_path(end):
    current = end
    path = []
    while current:
        path.append({"row": current.row, "col": current.col})
        current = current.previous
    return path[::-1]


def dijkstra_algorithm(grid_data, start_pos, end_pos):
    grid = make_grid()
    walls = grid_data.get('walls', [])
    for wall in walls:
        if 0 <= wall['row'] < ROWS and 0 <= wall['col'] < ROWS:
            grid[wall['row']][wall['col']].type = "wall"

    start = grid[start_pos['row']][start_pos['col']]
    end = grid[end_pos['row']][end_pos['col']]
    start.type = "start"
    end.type = "end"

    count = 0
    open_set = PriorityQueue()
    start.distance = 0
    open_set.put((0, count, start))
    visited_order = []

    while not open_set.empty():
        current = open_set.get()[2]
        if current == end:
            path = reconstruct_path(end)
            return {"success": True, "path": path, "visited": visited_order, "message": "Path found!"}

        for neighbor in get_neighbors(current, grid):
            temp = current.distance + 1
            if temp < neighbor.distance:
                neighbor.distance = temp
                neighbor.previous = current
                count += 1
                open_set.put((neighbor.distance, count, neighbor))

        if current.type not in ("start", "end"):
            visited_order.append({"row": current.row, "col": current.col})

    return {"success": False, "path": [], "visited": visited_order, "message": "No path found!"}


def a_star_algorithm(grid_data, start_pos, end_pos):
    grid = make_grid()
    walls = grid_data.get('walls', [])
    for wall in walls:
        if 0 <= wall['row'] < ROWS and 0 <= wall['col'] < ROWS:
            grid[wall['row']][wall['col']].type = "wall"

    start = grid[start_pos['row']][start_pos['col']]
    end = grid[end_pos['row']][end_pos['col']]
    start.type = "start"
    end.type = "end"

    count = 0
    open_set = PriorityQueue()
    start.g_score = 0
    start.f_score = heuristic(start, end)
    open_set.put((start.f_score, count, start))
    open_set_hash = {start}
    visited_order = []

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path = reconstruct_path(end)
            return {"success": True, "path": path, "visited": visited_order, "message": "Path found!"}

        for neighbor in get_neighbors(current, grid):
            temp_g_score = current.g_score + 1
            if temp_g_score < neighbor.g_score:
                neighbor.previous = current
                neighbor.g_score = temp_g_score
                neighbor.f_score = temp_g_score + heuristic(neighbor, end)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((neighbor.f_score, count, neighbor))
                    open_set_hash.add(neighbor)

        if current.type not in ("start", "end"):
            visited_order.append({"row": current.row, "col": current.col})

    return {"success": False, "path": [], "visited": visited_order, "message": "No path found!"}


def kmeans_algorithm(points, k, max_iterations):
    if len(points) < k:
        return {"success": False, "message": "Not enough points for clustering"}

    # Initialize centroids randomly
    centroids = random.sample(points, k)
    iterations_data = []

    for iteration in range(max_iterations):
        # Assign points to clusters
        clusters = [[] for _ in range(k)]
        for point in points:
            distances = [np.sqrt((point['x'] - c['x']) ** 2 + (point['y'] - c['y']) ** 2) for c in centroids]
            cluster_idx = distances.index(min(distances))
            clusters[cluster_idx].append(point)

        # Update centroids
        new_centroids = []
        for i, cluster in enumerate(clusters):
            if cluster:
                avg_x = sum(p['x'] for p in cluster) / len(cluster)
                avg_y = sum(p['y'] for p in cluster) / len(cluster)
                new_centroids.append({'x': avg_x, 'y': avg_y})
            else:
                new_centroids.append(centroids[i])

        iterations_data.append({
            'clusters': clusters,
            'centroids': new_centroids.copy()
        })

        # Check for convergence
        converged = True
        for i in range(k):
            if abs(centroids[i]['x'] - new_centroids[i]['x']) > 1 or abs(centroids[i]['y'] - new_centroids[i]['y']) > 1:
                converged = False
                break

        centroids = new_centroids
        if converged:
            break

    return {"success": True, "iterations": iterations_data,
            "message": f"K-Means completed in {len(iterations_data)} iterations"}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/dijkstra', methods=['POST'])
def run_dijkstra():
    try:
        data = request.get_json()
        if not data or 'start' not in data or 'end' not in data:
            return jsonify({"success": False, "message": "Missing start or end position"}), 400
        result = dijkstra_algorithm(data.get('grid', {}), data['start'], data['end'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "message": "Error running algorithm"}), 500


@app.route('/api/astar', methods=['POST'])
def run_astar():
    try:
        data = request.get_json()
        if not data or 'start' not in data or 'end' not in data:
            return jsonify({"success": False, "message": "Missing start or end position"}), 400
        result = a_star_algorithm(data.get('grid', {}), data['start'], data['end'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "message": "Error running algorithm"}), 500


@app.route('/api/kmeans', methods=['POST'])
def run_kmeans():
    try:
        data = request.get_json()
        if not data or 'points' not in data:
            return jsonify({"success": False, "message": "No points provided"}), 400

        points = data['points']
        k = data.get('k', 3)
        max_iterations = data.get('max_iterations', 10)

        result = kmeans_algorithm(points, k, max_iterations)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "message": "Error running K-Means"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
