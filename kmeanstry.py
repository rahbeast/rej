import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class KMeansVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("K-Means Clustering Visualizer")
        self.root.geometry("900x650")

        self.points = np.empty((0, 2))
        self.k = tk.IntVar(value=3)
        self.max_iter = tk.IntVar(value=10)

        self.setup_ui()

        # Connect mouse click event on matplotlib canvas
        self.cid = self.canvas.mpl_connect("button_press_event", self.on_click)

    def setup_ui(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        ttk.Label(control_frame, text="Clusters (K):").pack(side=tk.LEFT)
        ttk.Entry(control_frame, textvariable=self.k, width=5).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Max Iterations:").pack(side=tk.LEFT)
        ttk.Entry(control_frame, textvariable=self.max_iter, width=5).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Generate Points", command=self.generate_points).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text="Run K-Means", command=self.run_kmeans).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)

        # Progress bar for iterations
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def generate_points(self, count=100):
        self.points = np.array([[random.uniform(0, 10), random.uniform(0, 10)] for _ in range(count)])
        self.plot_points()

    def plot_points(self, clusters=None, centroids=None, iteration=None):
        self.ax.clear()

        if clusters is None:
            self.ax.scatter(self.points[:, 0], self.points[:, 1], color='gray', label='Points')
        else:
            colors = ['red', 'green', 'blue', 'purple', 'orange', 'cyan', 'magenta']
            for i, cluster in enumerate(clusters):
                if len(cluster) > 0:
                    cluster = np.array(cluster)
                    self.ax.scatter(cluster[:, 0], cluster[:, 1], color=colors[i % len(colors)], label=f"Cluster {i}")
            if centroids is not None:
                centroids = np.array(centroids)
                self.ax.scatter(centroids[:, 0], centroids[:, 1], color='black', marker='X', s=100, label='Centroids')

        title = "K-Means Clustering"
        if iteration is not None:
            title += f" - Iteration {iteration + 1}"
        self.ax.set_title(title)

        handles, labels = self.ax.get_legend_handles_labels()
        if labels:
            self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        self.fig.tight_layout()
        self.canvas.draw()

    def clear_canvas(self):
        self.points = np.empty((0, 2))
        self.ax.clear()
        self.canvas.draw()
        self.progress["value"] = 0

    def on_click(self, event):
        # Only add point if click inside axes
        if event.inaxes != self.ax:
            return
        x, y = event.xdata, event.ydata
        self.points = np.append(self.points, [[x, y]], axis=0)
        self.plot_points()

    def run_kmeans(self):
        k = self.k.get()
        max_iter = self.max_iter.get()

        if self.points.shape[0] == 0:
            messagebox.showerror("Error", "No points to cluster. Generate points or add points by clicking.")
            return

        if k <= 0:
            messagebox.showerror("Error", "Number of clusters must be positive.")
            return

        if k > len(self.points):
            messagebox.showerror("Error", "Number of clusters cannot exceed number of points.")
            return

        centroids = random.sample(self.points.tolist(), k)

        self.progress["maximum"] = max_iter
        self.progress["value"] = 0

        for iteration in range(max_iter):
            self.progress["value"] = iteration + 1
            self.root.update_idletasks()

            clusters = [[] for _ in range(k)]

            for point in self.points:
                distances = [np.linalg.norm(point - centroid) for centroid in centroids]
                cluster_index = distances.index(min(distances))
                clusters[cluster_index].append(point)

            new_centroids = []
            for cluster in clusters:
                if cluster:
                    new_centroids.append(np.mean(cluster, axis=0))
                else:
                    new_centroids.append(random.choice(self.points))

            centroids = new_centroids
            self.plot_points(clusters, centroids, iteration)
            self.root.update()
            self.root.after(500)  # animation speed; reduce delay if you want faster

        self.progress["value"] = 0  # Reset progress bar after done


if __name__ == "__main__":
    root = tk.Tk()
    app = KMeansVisualizer(root)
    root.mainloop()
