"""9 зураглалыг (5×5, 10×10, 20×20 тус бүр 3) үүсгэж maps/ хавтаст бичнэ.

X долоо хоног · Ариунбилэг
  a — ердийн тавиурын эгнээ (босоо тавиур, хөндлөн гарц)
  b — хөндлөн гарцын нэг хэсэг хаагдсан, тойрч явах шаардлагатай "төөрдөг"
  c — seed=42 санамсаргүй тархсан саад (~25%), зам байгааг BFS-ээр баталгаажуулна
Нэмэлт: no_path.txt — зорилго бүрэн хаагдсан, тестэд ашиглана.
"""
from __future__ import annotations

import random
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "maps"

HAND_5 = {
    "m05_a": ["S....",
              ".##..",
              ".##..",
              "...#.",
              "....G"],
    "m05_b": ["S.#.G",
              "..#.#",
              "..#..",
              "..#..",
              "....."],
    "m05_c": ["S....",
              "####.",
              "...#.",
              ".#G#.",
              "....."],
}

NO_PATH = ["S..#.",
           "...#.",
           "...##",
           "....#",
           "...#G"]  # G-ийн дээр болон зүүн тал хаалттай -> зам байхгүй


def shelves(n: int) -> list[list[str]]:
    """Агуулахын тавиурын загвар: 2 нүд өргөн тавиур, 1 нүд гарц, төвд хөндлөн гарц."""
    g = [["." for _ in range(n)] for _ in range(n)]
    for x in range(1, n - 1):
        if x % 3 == 0:          # гарц багана
            continue
        for y in range(1, n - 1):
            if y != n // 2:     # төв хөндлөн гарц
                g[y][x] = "#"
    g[0][0] = "S"
    g[n - 1][n - 1] = "G"
    return g


def serpentine(n: int) -> list[list[str]]:
    """Могой хэлбэрийн тавиур: босоо ханын нүх ээлжлэн доод/дээд талд.
    Эхлэл зүүн дээд, зорилго баруун дээд -> Манхэттэн зай нь бодит замаас хамаагүй богино,
    тиймээс эвристик "төөрөгдөнө" — A* ба BFS-ийн ялгаа энд харагдана."""
    g = [["." for _ in range(n)] for _ in range(n)]
    walls = [x for x in range(2, n - 1, 3)]
    for i, x in enumerate(walls):
        gap = n - 1 if i % 2 == 0 else 0
        for y in range(n):
            if y != gap:
                g[y][x] = "#"
    g[0][0] = "S"
    g[0][n - 1] = "G"
    return g


def random_map(n: int, density: float, seed: int) -> list[list[str]]:
    rng = random.Random(seed)
    while True:
        g = [["#" if rng.random() < density else "." for _ in range(n)] for _ in range(n)]
        g[0][0], g[n - 1][n - 1] = "S", "G"
        if bfs_len(g) is not None:
            return g


def bfs_len(g) -> int | None:
    n_y, n_x = len(g), len(g[0])
    start = next((x, y) for y in range(n_y) for x in range(n_x) if g[y][x] == "S")
    goal = next((x, y) for y in range(n_y) for x in range(n_x) if g[y][x] == "G")
    dist = {start: 0}
    q = deque([start])
    while q:
        s = q.popleft()
        if s == goal:
            return dist[s]
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            x, y = s[0] + dx, s[1] + dy
            if 0 <= x < n_x and 0 <= y < n_y and g[y][x] != "#" and (x, y) not in dist:
                dist[(x, y)] = dist[s] + 1
                q.append((x, y))
    return None


def write(name: str, rows) -> None:
    text = "\n".join("".join(r) for r in rows) + "\n"
    # newline="\n": Windows дээр ч LF хэвээр -> дахин үүсгэхэд файл өөрчлөгдөхгүй
    (MAPS / f"{name}.txt").write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):   # Windows консолд кирилл хэвлэх
        sys.stdout.reconfigure(encoding="utf-8")
    MAPS.mkdir(exist_ok=True)
    for name, rows in HAND_5.items():
        write(name, rows)
    for n in (10, 20):
        write(f"m{n}_a", shelves(n))
        write(f"m{n}_b", serpentine(n))
        write(f"m{n}_c", random_map(n, 0.25, seed=42))
    write("no_path", NO_PATH)
    for f in sorted(MAPS.glob("*.txt")):
        rows = f.read_text(encoding="utf-8").split()
        print(f"{f.stem:8s} {len(rows[0])}x{len(rows)}  BFS богино зам = {bfs_len(rows)}")


if __name__ == "__main__":
    sys.exit(main())
