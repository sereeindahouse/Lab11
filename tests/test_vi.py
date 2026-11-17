"""XIII долоо хоногийн тест: гар тооцоо, нийлэлт, үйлдэл сонголт (Ариунбилэг).

Гар тооцооны жишээ — 1×3 коридор  S . G  (γ = 0.95)
  p = 1  : V(M) = 50,  V(S) = −1 + 0.95·50 = 46.5
  p = 0.8: дээш/доош (хажуу) чиглэл нь хана -> байрандаа үлдэнэ
           V(M) = 0.8·50 + 0.2·(−1 + 0.95·V(M))  =>  V(M) = 39.8 / 0.81 = 49.1358…
           V(S) = 0.8·(−1 + 0.95·V(M)) + 0.2·(−1 + 0.95·V(S))  =>  V(S) = 44.8682…
"""
import random

import pytest

from warehouse.astar import astar
from warehouse.env import GridWorld
from warehouse.maps import MAIN_MAPS, load
from warehouse.vi import run_episode, value_iteration

CORRIDOR = GridWorld.from_string("S.G")
S, M, G = (0, 0), (1, 0), (2, 0)


def test_1_gar_tootsoo_p1():
    r = value_iteration(CORRIDOR, p=1.0)
    assert r.V[M] == pytest.approx(50.0)
    assert r.V[S] == pytest.approx(46.5)
    assert r.V[G] == 0.0
    # давталт бүрийн max|ΔV| гараар: 50 -> 47.5 -> 0
    assert r.deltas == pytest.approx([50.0, 47.5, 0.0])


def test_1b_gar_tootsoo_p08():
    r = value_iteration(CORRIDOR, p=0.8)
    assert r.V[M] == pytest.approx(3980 / 81, abs=1e-5)
    assert r.V[S] == pytest.approx(294380 / 6561, abs=1e-5)
    # эхний 2 давталтыг гараар: 39.8, 30.058
    assert r.deltas[:2] == pytest.approx([39.8, 30.058])
    assert r.policy == {S: "R", M: "R"}


@pytest.mark.parametrize("p", [1.0, 0.8])
@pytest.mark.parametrize("name", MAIN_MAPS)
def test_2_niilelt(name, p):
    r = value_iteration(load(name), p=p)
    assert r.converged and r.deltas[-1] < 1e-6


@pytest.mark.parametrize("name", MAIN_MAPS)
def test_3_uildel_songolt_p1_ni_astar_tei_tentsuu(name):
    """p=1 үед VI-ийн policy-г дагавал A*-ийн хамгийн богино замын уртаар хүрэх ёстой,
    мөн V(S) = −Σ_{k<n−1} γ^k + γ^{n−1}·50 (n = замын урт)."""
    env = load(name)
    r = value_iteration(env, p=1.0)
    n = astar(env).cost
    ep = run_episode(env, r.policy, p=1.0, rng=random.Random(42), max_steps=500)
    assert ep["success"] and ep["steps"] == n
    g = 0.95
    expected = -sum(g ** k for k in range(n - 1)) + g ** (n - 1) * 50
    assert r.V[env.start] == pytest.approx(expected, abs=1e-5)


def test_policy_hanaas_zailshiina():
    # p=0.8 үед хананы дагуу коридорт ч зорилго руу чиглэсэн хэвээр байх ёстой
    r = value_iteration(load("m05_a"), p=0.8)
    assert r.policy[(0, 0)] in ("D", "R")
