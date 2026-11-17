"""A* хайлт ба BFS тулгалт.

XI долоо хоног (10.30–11.05) · Хариуцагч: Сэргэлэн

f(n) = g(n) + h(n)
  g(n) — эхлэлээс n хүртэл явсан бодит алхмын тоо (алхам бүр 1)
  h(n) — Манхэттэн зай |x−xG| + |y−yG|. Робот зөвхөн 4 чиглэлд 1 нүдээр явдаг тул
         h нь бодит үлдсэн зайг хэзээ ч хэтрүүлэхгүй (admissible) бөгөөд
         хөрш хоёр нүдний h-ийн ялгаа ≤ 1 (consistent) -> A* оновчтой замыг олно.
"""
from __future__ import annotations

import heapq
import itertools
import time
from collections import deque
from dataclasses import dataclass, field

from .env import GridWorld, State


@dataclass
class SearchResult:
    path: list[State] | None          # эхлэл..зорилго, олдоогүй бол None
    cost: float | None                # алхмын тоо
    expanded: int                     # өргөтгөсөн (нээсэн) оройн тоо
    time_ms: float
    expanded_order: list[State] = field(default_factory=list)  # демо, тайлбарт


def manhattan(a: State, b: State) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _reconstruct(parent: dict[State, State | None], goal: State) -> list[State]:
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    return path[::-1]


def astar(env: GridWorld, start: State | None = None, goal: State | None = None,
          heuristic=manhattan, tie_break: str = "h") -> SearchResult:
    """tie_break="h"   : ижил f-тэй үед h бага (зорилгод ойр) оройг түрүүлж нээнэ.
       tie_break="fifo": ижил f-тэй үед эрт орсныг нь түрүүлж нээнэ (харьцуулалтад).
    Тавиурын агуулахад олон ижил урттай зам байдаг тул f тэнцэх нь элбэг —
    "fifo" үед A* бүх ижил f-тэй нүдийг нээгээд BFS-тэй адил болдог."""
    start = start or env.start
    goal = goal or env.goal
    t0 = time.perf_counter()
    tie = itertools.count()                 # ижил f үед FIFO дарааллаар
    def key(g: int, s: State):
        h = heuristic(s, goal)
        return (g + h, h if tie_break == "h" else 0, next(tie))

    open_heap = [(*key(0, start), 0, start)]   # (f, h, дараалал, g, төлөв)
    g_best = {start: 0}
    parent: dict[State, State | None] = {start: None}
    closed: set[State] = set()
    order: list[State] = []

    while open_heap:
        *_, g, s = heapq.heappop(open_heap)
        if s in closed:                     # хуучирсан (илүү их g-тэй) бичлэг
            continue
        closed.add(s)
        order.append(s)
        if s == goal:
            path = _reconstruct(parent, goal)
            return SearchResult(path, g, len(order), (time.perf_counter() - t0) * 1000, order)
        for nxt in env.neighbors(s):
            ng = g + 1
            if nxt not in closed and ng < g_best.get(nxt, float("inf")):
                g_best[nxt] = ng
                parent[nxt] = s
                heapq.heappush(open_heap, (*key(ng, nxt), ng, nxt))

    return SearchResult(None, None, len(order), (time.perf_counter() - t0) * 1000, order)


def bfs(env: GridWorld, start: State | None = None, goal: State | None = None) -> SearchResult:
    """Өргөнөөр хайх — алхам бүр 1 үед хамгийн богино замыг олно. A*-ийг шалгах эталон."""
    start = start or env.start
    goal = goal or env.goal
    t0 = time.perf_counter()
    parent: dict[State, State | None] = {start: None}
    q = deque([start])
    order: list[State] = []
    while q:
        s = q.popleft()
        order.append(s)
        if s == goal:
            path = _reconstruct(parent, goal)
            return SearchResult(path, len(path) - 1, len(order),
                                (time.perf_counter() - t0) * 1000, order)
        for nxt in env.neighbors(s):
            if nxt not in parent:
                parent[nxt] = s
                q.append(nxt)
    return SearchResult(None, None, len(order), (time.perf_counter() - t0) * 1000, order)


def is_valid_path(env: GridWorld, path: list[State]) -> bool:
    """Зам эхлэлээс зорилго хүртэл, саадгүй, хөрш нүдээр үргэлжилсэн эсэх."""
    if not path or path[0] != env.start or path[-1] != env.goal:
        return False
    return all(env.is_free(s) for s in path) and all(
        manhattan(a, b) == 1 for a, b in zip(path, path[1:]))
