"""MDP — утгын давталт (Value Iteration) ба үйлдэл сонголт (policy).

XIII долоо хоног (11.13–11.19) · Хариуцагч: Ариунбилэг

Bellman шинэчлэлт (бүх s-д, нэг "шүүрдэлт"):
    V_{k+1}(s) = max_a  Σ_{s'} P(s'|s,a) · [ R(s,a,s') + γ · V_k(s') ]
    V(G) = 0  (төгсгөлийн төлөв — цааш шагнал байхгүй)
Зогсох шалгуур: max_s |V_{k+1}(s) − V_k(s)| < θ  (θ = 1e-6)
Үйлдэл сонголт: π(s) = argmax_a Q(s,a)   (ижил бол U, D, L, R дарааллаар эхнийх)
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

from .env import ACTIONS, GridWorld, State


@dataclass
class VIResult:
    V: dict[State, float]
    policy: dict[State, str]
    iterations: int
    converged: bool
    deltas: list[float] = field(default_factory=list)   # давталт бүрийн max|ΔV|
    plan_ms: float = 0.0


def q_value(env: GridWorld, V: dict[State, float], s: State, a: str,
            p: float, gamma: float) -> float:
    return sum(pr * (env.reward(s, a, s2) + gamma * V[s2])
               for pr, s2 in env.transitions(s, a, p))


def greedy_policy(env: GridWorld, V: dict[State, float], p: float,
                  gamma: float) -> dict[State, str]:
    pol = {}
    for s in env.states():
        if env.is_terminal(s):
            continue
        pol[s] = max(ACTIONS, key=lambda a: q_value(env, V, s, a, p, gamma))
    return pol


def value_iteration(env: GridWorld, p: float = 1.0, gamma: float = 0.95,
                    theta: float = 1e-6, max_iter: int = 10_000) -> VIResult:
    t0 = time.perf_counter()
    states = env.states()
    V = {s: 0.0 for s in states}
    deltas: list[float] = []
    converged = False
    for _ in range(max_iter):
        V_new = {}
        for s in states:
            if env.is_terminal(s):
                V_new[s] = 0.0
                continue
            V_new[s] = max(q_value(env, V, s, a, p, gamma) for a in ACTIONS)
        delta = max(abs(V_new[s] - V[s]) for s in states)
        V = V_new                      # синхрон (бүх s-ийг хуучин V_k-аар) шинэчилнэ
        deltas.append(delta)
        if delta < theta:
            converged = True
            break
    policy = greedy_policy(env, V, p, gamma)
    return VIResult(V, policy, len(deltas), converged, deltas,
                    (time.perf_counter() - t0) * 1000)


def run_episode(env: GridWorld, policy: dict[State, str], p: float,
                rng: random.Random, max_steps: int = 200) -> dict:
    """Policy-г дагаж нэг оролдлого (эпизод) явуулна. Үйлдэл сонгох хугацааг тусад нь хэмжинэ."""
    s = env.start
    total, trail = 0.0, [s]
    choose_ns = 0
    for step in range(1, max_steps + 1):
        t = time.perf_counter_ns()
        a = policy[s]                  # хүснэгтээс уншина -> маш хурдан
        choose_ns += time.perf_counter_ns() - t
        s2 = env.sample_step(s, a, p, rng)
        total += env.reward(s, a, s2)
        trail.append(s2)
        s = s2
        if env.is_terminal(s):
            return {"success": True, "steps": step, "return": total,
                    "trail": trail, "choose_us_per_step": choose_ns / step / 1000}
    return {"success": False, "steps": max_steps, "return": total,
            "trail": trail, "choose_us_per_step": choose_ns / max_steps / 1000}
