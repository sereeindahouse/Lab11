"""Зураглал, зам, policy, утгын (V) зургийг matplotlib-ээр зурах (XII долоо хоног · хамт)."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from .env import ARROW, GridWorld, State


def draw(env: GridWorld, ax=None, path: list[State] | None = None,
         policy: dict[State, str] | None = None, values: dict[State, float] | None = None,
         expanded: list[State] | None = None, robot: State | None = None,
         trail: list[State] | None = None, title: str | None = None):
    if ax is None:
        _, ax = plt.subplots(figsize=(5, 5))
    H, W = env.height, env.width
    walls = np.array([[1 if env.grid[y][x] == "#" else 0 for x in range(W)] for y in range(H)])

    if values:
        arr = np.full((H, W), np.nan)
        for (x, y), v in values.items():
            arr[y, x] = v
        ax.imshow(arr, cmap="YlGn", origin="upper")
        ax.imshow(np.ma.masked_where(walls == 0, walls),
                  cmap=ListedColormap(["#5b4636"]), origin="upper")
    else:
        ax.imshow(walls, cmap=ListedColormap(["#f7f5ef", "#5b4636"]), origin="upper")

    if expanded:
        xs, ys = zip(*expanded)
        ax.scatter(xs, ys, s=(220 / W) ** 2, marker="s", color="#9ecae1", alpha=.55, lw=0)
    if path:
        xs, ys = zip(*path)
        ax.plot(xs, ys, color="#d7301f", lw=max(1.2, 6 - W / 5), solid_capstyle="round")
    if trail:
        xs, ys = zip(*trail)
        ax.plot(xs, ys, color="#6a51a3", lw=1.5, alpha=.8)
    if policy:
        fs = max(5, 16 - W * 0.55)
        lo = min(values.values()) if values else 0
        hi = max(values.values()) if values else 1
        for (x, y), a in policy.items():
            if (x, y) != env.goal:
                dark = values and hi > lo and (values[(x, y)] - lo) / (hi - lo) > 0.6
                ax.text(x, y, ARROW[a], ha="center", va="center", fontsize=fs,
                        color="white" if dark else "#08306b")
    if values and W <= 10:
        lo, hi = min(values.values()), max(values.values())
        for (x, y), v in values.items():
            dark = hi > lo and (v - lo) / (hi - lo) > 0.6
            ax.text(x, y + 0.32, f"{v:.1f}", ha="center", va="center", fontsize=6,
                    color="white" if dark else "#333")

    sx, sy = env.start
    gx, gy = env.goal
    ax.text(sx, sy, "S", ha="center", va="center", fontsize=max(7, 15 - W / 2), weight="bold",
            color="white", bbox=dict(boxstyle="round,pad=.2", fc="#2171b5", ec="none"))
    ax.text(gx, gy, "G", ha="center", va="center", fontsize=max(7, 15 - W / 2), weight="bold",
            color="white", bbox=dict(boxstyle="round,pad=.2", fc="#238b45", ec="none"))
    if robot:
        ax.plot(*robot, marker="o", ms=max(5, 18 - W / 2), color="#ff7f00", mec="black")

    ax.set_xticks(np.arange(-.5, W, 1), minor=True)
    ax.set_yticks(np.arange(-.5, H, 1), minor=True)
    ax.grid(which="minor", color="#cfcfcf", lw=.4)
    ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
    if title:
        ax.set_title(title, fontsize=10)
    return ax
