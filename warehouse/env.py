"""Агуулахын нүдэн орчин (Gridworld).

X долоо хоног (10.23–10.29) · Хариуцагч: Ариунбилэг

Төлөв  : роботын байрлал (x, y); x = багана (зүүнээс баруун), y = мөр (дээрээс доош).
Үйлдэл : 'U' дээш, 'D' доош, 'L' зүүн, 'R' баруун.
Дүрэм  : саад (#) эсвэл хил рүү чиглэсэн хөдөлгөөнд робот байрандаа үлдэнэ.
Шилжилт: p = 1   -> сонгосон чиглэл 100%.
         p = 0.8 -> сонгосон чиглэл 80%, хоёр хажуу чиглэл тус бүр 10%.
Шагнал : зорилгод (G) орох алхам +50, бусад алхам −1. G нь төгсгөлийн төлөв.

Зураглалын тэмдэгт: '.' чөлөөт нүд, '#' тавиур/саад, 'S' эхлэл, 'G' хүргэлтийн цэг.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random

ACTIONS = ("U", "D", "L", "R")
DELTA = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}
# Сонгосон чиглэлийн хоёр хажуу (90° эргэсэн) чиглэл
SIDES = {"U": ("L", "R"), "D": ("L", "R"), "L": ("U", "D"), "R": ("U", "D")}
ARROW = {"U": "↑", "D": "↓", "L": "←", "R": "→"}

GOAL_REWARD = 50.0
STEP_REWARD = -1.0

State = tuple[int, int]


@dataclass
class GridWorld:
    grid: list[str]
    name: str = "map"

    def __post_init__(self) -> None:
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        if any(len(row) != self.width for row in self.grid):
            raise ValueError("Бүх мөр ижил урттай байх ёстой")
        self.start = self._find("S")
        self.goal = self._find("G")

    # ---------- ачаалах ----------
    @classmethod
    def from_string(cls, text: str, name: str = "map") -> "GridWorld":
        rows = [r.strip() for r in text.strip().splitlines() if r.strip()]
        return cls(rows, name)

    @classmethod
    def from_file(cls, path: str | Path) -> "GridWorld":
        path = Path(path)
        return cls.from_string(path.read_text(encoding="utf-8"), path.stem)

    def _find(self, ch: str) -> State:
        for y, row in enumerate(self.grid):
            x = row.find(ch)
            if x >= 0:
                return (x, y)
        raise ValueError(f"Зураглалд '{ch}' алга")

    # ---------- үндсэн дүрэм ----------
    def in_bounds(self, s: State) -> bool:
        x, y = s
        return 0 <= x < self.width and 0 <= y < self.height

    def is_free(self, s: State) -> bool:
        return self.in_bounds(s) and self.grid[s[1]][s[0]] != "#"

    def states(self) -> list[State]:
        """Саад биш бүх нүд."""
        return [(x, y) for y in range(self.height) for x in range(self.width)
                if self.grid[y][x] != "#"]

    def is_terminal(self, s: State) -> bool:
        return s == self.goal

    def move(self, s: State, a: str) -> State:
        """Тодорхой (p=1) хөдөлгөөн: саад/хил бол байрандаа үлдэнэ."""
        dx, dy = DELTA[a]
        nxt = (s[0] + dx, s[1] + dy)
        return nxt if self.is_free(nxt) else s

    def reward(self, s: State, a: str, s_next: State) -> float:
        return GOAL_REWARD if s_next == self.goal else STEP_REWARD

    def transitions(self, s: State, a: str, p: float = 1.0) -> list[tuple[float, State]]:
        """P(s' | s, a)-г (магадлал, s') жагсаалтаар буцаана.
        Нэг s' рүү хоёр чиглэл хүргэвэл магадлалыг нь нэмнэ (жишээ нь хоёр тал хана)."""
        if self.is_terminal(s):
            return [(1.0, s)]
        side = (1.0 - p) / 2.0
        out: dict[State, float] = {}
        for direction, prob in ((a, p), (SIDES[a][0], side), (SIDES[a][1], side)):
            if prob <= 0:
                continue
            nxt = self.move(s, direction)
            out[nxt] = out.get(nxt, 0.0) + prob
        return [(pr, st) for st, pr in out.items()]

    def sample_step(self, s: State, a: str, p: float, rng: random.Random) -> State:
        """Магадлалт орчинд нэг алхмыг санамсаргүйгээр гүйцэтгэнэ."""
        u = rng.random()
        if u < p:
            direction = a
        elif u < p + (1 - p) / 2:
            direction = SIDES[a][0]
        else:
            direction = SIDES[a][1]
        return self.move(s, direction)

    def neighbors(self, s: State) -> list[State]:
        """Хайлтад (A*, BFS) хэрэглэх: байрандаа үлдэх хөдөлгөөнийг тооцохгүй."""
        out = []
        for a in ACTIONS:
            nxt = self.move(s, a)
            if nxt != s:
                out.append(nxt)
        return out

    def render(self, path: list[State] | None = None,
               policy: dict[State, str] | None = None) -> str:
        """ASCII зураг: зам '*' эсвэл policy-ийн сум."""
        rows = [list(r) for r in self.grid]
        if policy:
            for (x, y), a in policy.items():
                if rows[y][x] == ".":
                    rows[y][x] = ARROW[a]
        if path:
            for (x, y) in path:
                if rows[y][x] == ".":
                    rows[y][x] = "*"
        return "\n".join("".join(r) for r in rows)
