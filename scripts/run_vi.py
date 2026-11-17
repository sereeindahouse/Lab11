"""XIII долоо хоногийн хэмжилт: 9 зураглал × p∈{1, 0.8} дээр Value Iteration.

Гаралт: results/vi_results.csv          — давталт, хугацаа, V(S), policy-ийн ялгаа
        results/vi_convergence.csv      — давталт бүрийн max|ΔV|
        results/vi_convergence.png      — нийлэлтийн муруй (лог шкал)
        results/vi_policy_p08.png       — p=0.8 үеийн policy (сум) ба V (өнгө)
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt  # noqa: E402

from warehouse.maps import load_all  # noqa: E402
from warehouse.viz import draw  # noqa: E402
from warehouse.vi import value_iteration  # noqa: E402

OUT = ROOT / "results"
REPEAT = 5
GAMMA, THETA = 0.95, 1e-6


def main() -> None:
    OUT.mkdir(exist_ok=True)
    envs = load_all()
    rows, conv_rows, results = [], [], {}
    for env in envs:
        for p in (1.0, 0.8):
            r = value_iteration(env, p=p, gamma=GAMMA, theta=THETA)
            ms = statistics.median(value_iteration(env, p=p).plan_ms for _ in range(REPEAT))
            results[(env.name, p)] = r
            rows.append({"map": env.name, "size": f"{env.width}x{env.height}",
                         "states": len(env.states()), "p": p, "gamma": GAMMA, "theta": THETA,
                         "iterations": r.iterations, "converged": r.converged,
                         "plan_ms_median": round(ms, 2),
                         "V_start": round(r.V[env.start], 4),
                         "final_delta": f"{r.deltas[-1]:.2e}"})
            for k, d in enumerate(r.deltas, 1):
                conv_rows.append({"map": env.name, "p": p, "iteration": k, "max_delta": d})
        # p=1 ба p=0.8 policy хэдэн нүдэнд ялгаатай вэ
        a, b = results[(env.name, 1.0)].policy, results[(env.name, 0.8)].policy
        diff = sum(a[s] != b[s] for s in a)
        rows[-1]["policy_diff_vs_p1"] = diff
        rows[-2]["policy_diff_vs_p1"] = 0

    with open(OUT / "vi_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(OUT / "vi_convergence.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(conv_rows[0]))
        w.writeheader()
        w.writerows(conv_rows)

    # нийлэлтийн муруй
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, p in zip(axes, (1.0, 0.8)):
        for env in envs:
            d = results[(env.name, p)].deltas
            ax.semilogy(range(1, len(d) + 1), [max(x, 1e-12) for x in d], label=env.name, lw=1.3)
        ax.axhline(THETA, color="red", ls="--", lw=1)
        ax.text(1, THETA * 1.8, "θ = 10⁻⁶", color="red", fontsize=9)
        ax.set_title(f"p = {p}: давталт бүрийн max|ΔV|")
        ax.set_xlabel("давталт k")
        ax.grid(alpha=.3)
    axes[0].set_ylabel("max |V_k − V_(k−1)|  (лог)")
    axes[1].legend(fontsize=8, ncol=3)
    fig.tight_layout()
    fig.savefig(OUT / "vi_convergence.png", dpi=130)

    fig, axes = plt.subplots(3, 3, figsize=(12, 12))
    for ax, env in zip(axes.flat, envs):
        r = results[(env.name, 0.8)]
        reach = {s: v for s, v in r.V.items()}
        draw(env, ax, policy=r.policy, values=reach,
             title=f"{env.name} (p=0.8): {r.iterations} давталт, V(S)={r.V[env.start]:.2f}")
    fig.suptitle("Value Iteration: үйлдэл сонголт (сум) ба V (өнгө — их нь ногоон)", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "vi_policy_p08.png", dpi=130)

    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
