import time
import tkinter as tk
from queue import PriorityQueue
from tkinter import messagebox  # <-- Import messagebox


ROWS = 40
WIDTH = 800
GAP = WIDTH // ROWS

class Node:
    def __init__(self, row, col, canvas):
        self.row = row
        self.col = col
        self.canvas = canvas
        self.x = col * GAP
        self.y = row * GAP
        self.rect = canvas.create_rectangle(self.x, self.y, self.x + GAP, self.y + GAP, fill="white", outline="gray")
        self.neighbors = []
        self.distance = float("inf")
        self.previous = None
        self.type = "empty"

    def make_start(self):
        self.canvas.itemconfig(self.rect, fill="green")
        self.type = "start"

    def make_end(self):
        self.canvas.itemconfig(self.rect, fill="red")
        self.type = "end"

    def make_wall(self):
        self.canvas.itemconfig(self.rect, fill="dark blue")
        self.type = "wall"

    def make_visited(self):
        if self.type not in ("start", "end"):
            self.canvas.itemconfig(self.rect, fill="sky blue")

    def make_path(self):
        if self.type not in ("start", "end"):
            self.canvas.itemconfig(self.rect, fill="Yellow")

    def reset(self):
        self.canvas.itemconfig(self.rect, fill="white")
        self.type = "empty"

    def __lt__(self, other):
        return False

def make_grid(canvas):
    grid = []
    for i in range(ROWS):
        grid.append([])
        for j in range(ROWS):
            node = Node(i, j, canvas)
            grid[i].append(node)
    return grid

def get_neighbors(node, grid):
    neighbors = []
    if node.row < ROWS - 1 and grid[node.row + 1][node.col].type != "wall":  # down
        neighbors.append(grid[node.row + 1][node.col])
    if node.row > 0 and grid[node.row - 1][node.col].type != "wall":  # up
        neighbors.append(grid[node.row - 1][node.col])
    if node.col < ROWS - 1 and grid[node.row][node.col + 1].type != "wall":  # right
        neighbors.append(grid[node.row][node.col + 1])
    if node.col > 0 and grid[node.row][node.col - 1].type != "wall":  # left
        neighbors.append(grid[node.row][node.col - 1])
    return neighbors

def reconstruct_path(end, canvas):
    current = end
    path = []
    while current:
        path.append(current)
        current = current.previous

    path = path[::-1]  # Reverse to go from start to end

    for node in path:
        if node.type not in ("start", "end"):
            node.make_path()
            canvas.update()
            time.sleep(0.1)

def dijkstra(grid, start, end, canvas):
    count = 0
    open_set = PriorityQueue()
    start.distance = 0
    open_set.put((0, count, start))

    while not open_set.empty():
        current = open_set.get()[2]

        if current == end:
            reconstruct_path(end, canvas)
            return True

        for neighbor in get_neighbors(current, grid):
            temp = current.distance + 1
            if temp < neighbor.distance:
                neighbor.distance = temp
                neighbor.previous = current
                count += 1
                open_set.put((neighbor.distance, count, neighbor))

        current.make_visited()
        canvas.update()
        time.sleep(0.03)
    return False

def main():
    win = tk.Tk()
    win.title("Dijkstra Pathfinding")
    canvas = tk.Canvas(win, width=WIDTH, height=WIDTH)
    canvas.pack()

    grid = make_grid(canvas)
    start = None
    end = None
    drawing = False  # for dragging to draw walls

    def get_node_at(event):
        row, col = event.y // GAP, event.x // GAP
        return grid[row][col]

    def on_mouse_down(event):
        nonlocal start, end, drawing
        node = get_node_at(event)
        drawing = True
        if not start:
            start = node
            start.make_start()
        elif not end and node != start:
            end = node
            end.make_end()
        elif node != start and node != end:
            node.make_wall()

    def on_mouse_move(event):
        if drawing:
            node = get_node_at(event)
            if node.type == "empty":
                node.make_wall()

    def on_mouse_up(event):
        nonlocal drawing
        drawing = False

    def on_key(event):
        if event.char == " " and start and end:
            found = dijkstra(grid, start, end, canvas)
            if not found:
                # Show pop-up message
                messagebox.showinfo("Pathfinding Result", "No path found! The end node is unreachable.")

    canvas.bind("<Button-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    win.bind("<Key>", on_key)

    win.mainloop()

if __name__ == "__main__":
    main()


