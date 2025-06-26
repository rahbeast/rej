import time
import tkinter as tk
from queue import PriorityQueue
from tkinter import messagebox

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
        self.rect = canvas.create_rectangle(self.x, self.y, self.x + GAP, self.y + GAP, fill="white", outline="lightblue")
        self.neighbors = []
        self.previous = None
        self.type = "empty"
        self.circle=None
        self.dot=None

    def make_start(self):
        self.type = "start"
        self.canvas.create_text(self.x + GAP // 2, self.y + GAP // 2, text=">", font=("Arial", 25), fill="black")

    def make_end(self):
        self.type = "end"
        circle_radius = GAP // 3
        dot_radius = GAP // 8
        x_center = self.x + GAP // 2
        y_center = self.y + GAP // 2
        self.circle = self.canvas.create_oval(
            x_center - circle_radius, y_center - circle_radius,
            x_center + circle_radius, y_center + circle_radius,
            fill="", outline="black", width=2
        )
        self.dot = self.canvas.create_oval(
            x_center - dot_radius, y_center - dot_radius,
            x_center + dot_radius, y_center + dot_radius,
            fill="black"
        )

    def make_wall(self):
        self.type = "wall"
        steps = 6
        delay = 35
        expansion_step = GAP // (2 * steps)
        x_center = self.x + GAP // 2
        y_center = self.y + GAP // 2
        fill_rect = self.canvas.create_rectangle(
            x_center, y_center, x_center, y_center, fill="black", outline=""
        )

        def expand_fill(step=0):
            if step < steps:
                x1 = x_center - step * expansion_step
                y1 = y_center - step * expansion_step
                x2 = x_center + step * expansion_step
                y2 = y_center + step * expansion_step
                self.canvas.coords(fill_rect, x1, y1, x2, y2)
                self.canvas.after(delay, expand_fill, step + 1)
            else:
                self.canvas.itemconfig(self.rect, fill="black")

        expand_fill()

    def make_visited(self, next_node=None):
        if self.type in ("start", "end"):
            return
        steps = 5
        delay = 25
        expansion_step = GAP // (2 * steps)

        x_center = self.x + GAP // 2
        y_center = self.y + GAP // 2

        fill_rect = self.canvas.create_rectangle(
            x_center, y_center, x_center, y_center, fill="lightblue", outline=""
        )

        def expand_fill(step=0):

            if step < steps:
                x1 = x_center - step * expansion_step
                y1 = y_center - step * expansion_step
                x2 = x_center + step * expansion_step
                y2 = y_center + step * expansion_step

                self.canvas.coords(fill_rect, x1, y1, x2, y2)
                self.canvas.after(delay, expand_fill, step + 1)
            else:

                self.canvas.delete(fill_rect)
                start_blue_animation()

        def start_blue_animation(step=0):

            if step == 0:
                self.final_fill = self.canvas.create_rectangle(
                    x_center, y_center, x_center, y_center, fill="#4e7ecc", outline=""
                )

            if step < steps:
                x1 = x_center - step * expansion_step
                y1 = y_center - step * expansion_step
                x2 = x_center + step * expansion_step
                y2 = y_center + step * expansion_step

                self.canvas.coords(self.final_fill, x1, y1, x2, y2)
                self.canvas.after(delay, start_blue_animation, step + 1)
            else:

                self.canvas.itemconfig(self.rect, fill="#52bce3")
                self.canvas.delete(self.final_fill)

                if next_node:
                    self.canvas.after(delay, next_node.make_visited)

        expand_fill()

    def make_path(self):
        if self.type in ("start", "end"):
            return
        colors = ["#FFFACD", "#FFD700", "#FFC107", "#FFA500", "yellow"]
        steps = len(colors)
        delay = 50

        def animate_path(step=0):
            if step < steps:
                self.canvas.itemconfig(self.rect, fill=colors[step])
                self.canvas.after(delay, animate_path, step )

        animate_path()

    def reset(self):
        self.canvas.itemconfig(self.rect, fill="white")
        self.type = "empty"

    def __lt__(self, other):
        return False

def make_grid(canvas):
    return [[Node(i, j, canvas) for j in range(ROWS)] for i in range(ROWS)]

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

def heuristic(a, b):
    # Manhattan distance
    return abs(a.row - b.row) + abs(a.col - b.col)

def reconstruct_path(end, canvas):
    current = end
    while current.previous:
        if current.type not in ("start", "end"):
            current.make_path()
        current = current.previous
        canvas.update()
        time.sleep(0.05)

def a_star(grid, start, end, canvas):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    g_score = {node: float("inf") for row in grid for node in row}
    f_score = {node: float("inf") for row in grid for node in row}

    g_score[start] = 0
    f_score[start] = heuristic(start, end)

    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(end, canvas)
            return True

        for neighbor in get_neighbors(current, grid):
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                neighbor.previous = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, end)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

        if current != start:
            current.make_visited()

        canvas.update()
        time.sleep(0.02)
    return False

def main():
    win = tk.Tk()
    win.title("A* Pathfinding Algorithm")
    canvas = tk.Canvas(win, width=WIDTH, height=WIDTH)
    canvas.pack()

    grid = make_grid(canvas)
    start = None
    end = None
    drawing = False

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
              found = a_star(grid, start, end, canvas)
              if not found:
                # show pop-up message
                messagebox.showinfo("Pathfinding Result","No path found! The end node is unreachable.")

    canvas.bind("<Button-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    win.bind("<Key>", on_key)

    win.mainloop()

if __name__ == "__main__":
    main()
