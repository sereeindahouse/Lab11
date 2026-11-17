"""XI долоо хоногийн хэмжилт: 9 зураглал дээр A* ба BFS.

Гаралт: results/astar_results.csv, results/astar_paths.png
Хугацааг 30 удаа давтаж медианыг авна (нэг удаагийн хэмжилт хэт хэлбэлздэг).
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt  # noqa: E402

from warehouse.astar import astar, bfs, manhattan  # noqa: E402
from warehouse.maps import load_all  # noqa: E402
from warehouse.viz import draw  # noqa: E402

REPEAT = 30
OUT = ROOT / "results"


def median_ms(fn, env) -> float:
    return statistics.median(fn(env).time_ms for _ in range(REPEAT))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rows = []
    envs = load_all()
    for env in envs:
        a, b = astar(env), bfs(env)
        rows.append({
            "map": env.name,
            "size": f"{env.width}x{env.height}",
            "free_cells": len(env.states()),
            "manhattan_h0": manhattan(env.start, env.goal),
            "astar_cost": a.cost,
            "astar_expanded": a.expanded,
            "astar_ms_median": round(median_ms(astar, env), 4),
            "astar_fifo_expanded": astar(env, tie_break="fifo").expanded,
            "bfs_cost": b.cost,
            "bfs_expanded": b.expanded,
            "bfs_ms_median": round(median_ms(bfs, env), 4),
            "cost_match": a.cost == b.cost,
            "expanded_saving_pct": round(100 * (1 - a.expanded / b.expanded), 1),
        })
    with open(OUT / "astar_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    fig, axes = plt.subplots(3, 3, figsize=(12, 12))
    for ax, env, r in zip(axes.flat, envs, rows):
        res = astar(env)
        draw(env, ax, path=res.path, expanded=res.expanded_order,
             title=f"{env.name}: өртөг {r['astar_cost']}, нээсэн {r['astar_expanded']} "
                   f"(BFS {r['bfs_expanded']})")
    fig.suptitle("A* зам (улаан) ба нээсэн орой (цэнхэр)", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "astar_paths.png", dpi=130)

    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
