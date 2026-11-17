"""Командын мөрийн прототип (XII долоо хоног) — Streamlit саатвал нөөц хувилбар.

Жишээ:
    python -m warehouse.cli --map m10_b --algo astar
    python -m warehouse.cli --map m05_a --algo vi --p 0.8 --episode
"""
from __future__ import annotations

import argparse
import random
import sys

from .astar import astar
from .maps import MAIN_MAPS, load
from .vi import run_episode, value_iteration


def main(argv: list[str] | None = None) -> None:
    # Windows консол (cp1252) кирилл үсэг хэвлэж чаддаггүй тул UTF-8 болгоно
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap =argparse.ArgumentParser(description="Агуулахын робот — A* / Value Iteration")
    ap.add_argument("--map", default="m05_a", choices=MAIN_MAPS + ["no_path"])
    ap.add_argument("--algo", default="astar", choices=["astar", "vi"])
    ap.add_argument("--p", type=float, default=1.0, help="сонгосон чиглэлд явах магадлал")
    ap.add_argument("--gamma", type=float, default=0.95)
    ap.add_argument("--episode", action="store_true", help="VI policy-гоор 1 оролдлого явуулах")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)

    env = load(args.map)
    print(f"Зураглал {env.name} ({env.width}×{env.height}), S={env.start}, G={env.goal}\n")
    if args.algo == "astar":
        r = astar(env)
        if r.path is None:
            print(env.render())
            print(f"\nЗам олдсонгүй. Нээсэн орой: {r.expanded}, {r.time_ms:.3f} мс")
            return
        print(env.render(path=r.path))
        print(f"\nA*: өртөг {r.cost}, нээсэн орой {r.expanded}, {r.time_ms:.3f} мс")
    else:
        r = value_iteration(env, p=args.p, gamma=args.gamma)
        print(env.render(policy=r.policy))
        print(f"\nVI (p={args.p}, γ={args.gamma}): {r.iterations} давталт, "
              f"нийлсэн={r.converged}, {r.plan_ms:.1f} мс, V(S)={r.V[env.start]:.3f}")
        if args.episode:
            ep = run_episode(env, r.policy, args.p, random.Random(args.seed))
            print(env.render(path=ep["trail"]))
            print(f"Оролдлого: амжилт={ep['success']}, алхам={ep['steps']}, "
                  f"нийт шагнал={ep['return']:.0f}")


if __name__ == "__main__":
    main()
