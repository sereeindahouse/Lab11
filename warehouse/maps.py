"""Зураглал ачаалах туслах функц (X долоо хоног · Ариунбилэг)."""
from __future__ import annotations

from pathlib import Path

from .env import GridWorld

MAP_DIR = Path(__file__).resolve().parents[1] / "maps"
MAIN_MAPS = ["m05_a", "m05_b", "m05_c",
             "m10_a", "m10_b", "m10_c",
             "m20_a", "m20_b", "m20_c"]


def load(name: str) -> GridWorld:
    return GridWorld.from_file(MAP_DIR / f"{name}.txt")


def load_all() -> list[GridWorld]:
    return [load(n) for n in MAIN_MAPS]
