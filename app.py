"""Streamlit демо — зураглал сонгож A* зам, VI үйлдэл сонголт, роботын явцыг харах.

XII долоо хоног: A* прототип (зам, нээсэн орой)
XIII долоо хоног: Value Iteration таб нэмэгдсэн (policy, V, нэг оролдлого алхам алхмаар)

Ажиллуулах:  streamlit run app.py
"""
from __future__ import annotations

import random

import matplotlib.pyplot as plt
import streamlit as st

from warehouse.astar import astar, bfs
from warehouse.maps import MAIN_MAPS, load
from warehouse.vi import run_episode, value_iteration
from warehouse.viz import draw

st.set_page_config(page_title="Агуулахын робот", layout="wide")
st.title("Агуулахын хүргэлтийн робот — A* ба Value Iteration")

with st.sidebar:
    name = st.selectbox("Зураглал", MAIN_MAPS + ["no_path"])
    p = st.select_slider("p (сонгосон чиглэлд явах магадлал)", options=[1.0, 0.9, 0.8, 0.7], value=0.8)
    gamma = st.slider("γ (ирээдүйн шагналын жин)", 0.80, 0.99, 0.95, 0.01)
    seed = st.number_input("seed", value=42, step=1)

env = load(name)
st.caption(f"{env.name}: {env.width}×{env.height}, чөлөөт нүд {len(env.states())}, "
           f"S={env.start}, G={env.goal}")

tab_a, tab_v = st.tabs(["A* хайлт (p=1)", "Value Iteration"])

with tab_a:
    a, b = astar(env), bfs(env)
    c1, c2 = st.columns([3, 2])
    with c1:
        show_exp = st.checkbox("Нээсэн оройг харуулах", value=True)
        fig, ax = plt.subplots(figsize=(6, 6))
        draw(env, ax, path=a.path, expanded=a.expanded_order if show_exp else None)
        st.pyplot(fig, clear_figure=True)
        plt.close(fig)
    with c2:
        if a.path is None:
            st.error("Зам олдсонгүй — зорилго хаалттай.")
        # st.dataframe нь pyarrow шаарддаг; зарим Windows-д (Smart App Control) түүний DLL
        # хаагддаг тул энгийн markdown хүснэгт ашиглана.
        st.markdown(
            "| хэмжүүр | A* | BFS |\n|---|---:|---:|\n"
            f"| замын өртөг | {a.cost} | {b.cost} |\n"
            f"| нээсэн орой | {a.expanded} | {b.expanded} |\n"
            f"| хугацаа (мс) | {a.time_ms:.3f} | {b.time_ms:.3f} |")
        st.markdown("A* нь **f = g + h** хамгийн бага оройг түрүүлж нээнэ; "
                    "h = Манхэттэн зай. BFS-тэй өртөг нь тэнцүү байх ёстой.")

with tab_v:
    if a.path is None:
        st.warning("Энэ зураглалд зорилго хүрэх боломжгүй.")
    r = value_iteration(env, p=p, gamma=gamma)
    c1, c2 = st.columns([3, 2])
    with c1:
        ep = run_episode(env, r.policy, p, random.Random(int(seed)))
        step = st.slider("Оролдлогын алхам", 0, len(ep["trail"]) - 1, len(ep["trail"]) - 1)
        fig, ax = plt.subplots(figsize=(6, 6))
        draw(env, ax, policy=r.policy, values=r.V, trail=ep["trail"][:step + 1],
             robot=ep["trail"][step])
        st.pyplot(fig, clear_figure=True)
        plt.close(fig)
    with c2:
        st.metric("Давталт", r.iterations)
        st.metric("V(S)", f"{r.V[env.start]:.3f}")
        st.metric("Төлөвлөх хугацаа (мс)", f"{r.plan_ms:.1f}")
        st.write(f"Оролдлого: **{'амжилттай' if ep['success'] else 'бүтэлгүй'}**, "
                 f"{ep['steps']} алхам, нийт шагнал {ep['return']:.0f}")
        fig2, ax2 = plt.subplots(figsize=(4, 2.6))
        ax2.semilogy(range(1, len(r.deltas) + 1), [max(d, 1e-12) for d in r.deltas])
        ax2.axhline(1e-6, color="red", ls="--", lw=1)
        ax2.set_xlabel("давталт")
        ax2.set_ylabel("max|ΔV|")
        st.pyplot(fig2, clear_figure=True)
        plt.close(fig2)
