"""Вэб (Vercel) хувилбарт зориулсан JSON API-ийн логик.

Зөвхөн стандарт сан ашиглана (numpy/matplotlib шаардлагагүй) — serverless функцэд хөнгөн.
Зургийг хөтөч дээр SVG-ээр зурна; энд зөвхөн тоо, зам, policy-г буцаана.
"""
from __future__ import annotations

import random
from functools import lru_cache

from .astar import astar, bfs
from .maps import MAIN_MAPS, load
from .vi import run_episode, value_iteration

ALL_MAPS = MAIN_MAPS + ["no_path"]
P_OPTIONS = (1.0, 0.9, 0.8, 0.7)


class BadRequest(ValueError):
    pass


def parse_params(q: dict[str, str]) -> tuple[str, float, float, int]:
    """Query string-ийг шалгаж (map, p, gamma, seed) буцаана."""
    name = q.get("map", "m05_a")
    if name not in ALL_MAPS:
        raise BadRequest(f"map нь {ALL_MAPS}-ийн нэг байх ёстой")
    try:
        p = round(float(q.get("p", 0.8)), 2)
        gamma = round(float(q.get("gamma", 0.95)), 2)
        seed = int(q.get("seed", 42))
    except ValueError as e:
        raise BadRequest("p, gamma, seed тоо байх ёстой") from e
    if p not in P_OPTIONS:
        raise BadRequest(f"p нь {P_OPTIONS}-ийн нэг байх ёстой")
    if not 0.80 <= gamma <= 0.99:
        raise BadRequest("gamma нь 0.80–0.99 хооронд байх ёстой")
    if not 0 <= seed <= 1_000_000:
        raise BadRequest("seed нь 0–1000000 хооронд байх ёстой")
    return name, p, gamma, seed


@lru_cache(maxsize=64)
def _plan(name: str, p: float, gamma: float):
    env = load(name)
    return env, astar(env), bfs(env), value_iteration(env, p=p, gamma=gamma)


def solve(name: str, p: float, gamma: float, seed: int) -> dict:
    env, a, b, r = _plan(name, p, gamma)
    ep = run_episode(env, r.policy, p, random.Random(seed))
    return {
        "map": {"name": env.name, "width": env.width, "height": env.height,
                "grid": env.grid, "start": env.start, "goal": env.goal,
                "free_cells": len(env.states())},
        "astar": {"path": a.path, "cost": a.cost, "expanded": a.expanded,
                  "expanded_order": a.expanded_order, "time_ms": a.time_ms},
        "bfs": {"cost": b.cost, "expanded": b.expanded, "time_ms": b.time_ms},
        "vi": {"p": p, "gamma": gamma, "iterations": r.iterations, "converged": r.converged,
               "plan_ms": r.plan_ms, "V_start": r.V[env.start], "deltas": r.deltas,
               "V": [[x, y, v] for (x, y), v in r.V.items()],
               "policy": [[x, y, act] for (x, y), act in r.policy.items()]},
        "episode": {"seed": seed, "success": ep["success"], "steps": ep["steps"],
                    "return": ep["return"], "trail": ep["trail"]},
    }
