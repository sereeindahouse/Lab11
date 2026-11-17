"""X долоо хоногийн тест: хил, саад, магадлал, зураглал (Ариунбилэг)."""
import random

import pytest

from warehouse.env import GridWorld
from warehouse.maps import MAIN_MAPS, load

SMALL = GridWorld.from_string("""
S.#
...
..G
""")


def test_hil_ruu_yvbal_bairandaa_uldene():
    # (0,0)-оос дээш, зүүн тийш явбал хил -> байрандаа
    assert SMALL.move((0, 0), "U") == (0, 0)
    assert SMALL.move((0, 0), "L") == (0, 0)
    assert SMALL.move((0, 0), "R") == (1, 0)


def test_saad_ruu_yvbal_bairandaa_uldene():
    # (1,0)-ийн баруун талд '#' (2,0)
    assert SMALL.move((1, 0), "R") == (1, 0)
    assert not SMALL.is_free((2, 0))


def test_shiljiltiin_magadlal_p08():
    # (1,1) төвөөс 'U' -> 0.8 дээш (1,0), 0.1 зүүн (0,1), 0.1 баруун (2,1)
    tr = dict((s, pr) for pr, s in SMALL.transitions((1, 1), "U", p=0.8))
    assert tr == pytest.approx({(1, 0): 0.8, (0, 1): 0.1, (2, 1): 0.1})
    # нийлбэр 1 — бүх нүд, бүх үйлдэлд
    for s in SMALL.states():
        for a in "UDLR":
            assert sum(pr for pr, _ in SMALL.transitions(s, a, 0.8)) == pytest.approx(1.0)


def test_hoyr_tal_hana_bol_magadlal_niilne():
    # (0,0)-оос 'D': 0.8 доош (0,1); зүүн=хил (0.1 байрандаа), баруун (1,0) 0.1
    tr = dict((s, pr) for pr, s in SMALL.transitions((0, 0), "D", p=0.8))
    assert tr == pytest.approx({(0, 1): 0.8, (0, 0): 0.1, (1, 0): 0.1})


def test_p1_bol_todorhoi():
    assert SMALL.transitions((1, 1), "R", p=1.0) == [(1.0, (2, 1))]


def test_sanamsargui_alham_davtamj():
    # seed=42, 20 000 алхамд давтамж онолын 0.8/0.1/0.1-д ойр байх ёстой
    rng = random.Random(42)
    n = 20_000
    counts = {}
    for _ in range(n):
        s2 = SMALL.sample_step((1, 1), "U", 0.8, rng)
        counts[s2] = counts.get(s2, 0) + 1
    assert counts[(1, 0)] / n == pytest.approx(0.8, abs=0.01)
    assert counts[(0, 1)] / n == pytest.approx(0.1, abs=0.01)
    assert counts[(2, 1)] / n == pytest.approx(0.1, abs=0.01)


def test_shagnal():
    assert SMALL.reward((2, 1), "D", (2, 2)) == 50
    assert SMALL.reward((0, 0), "R", (1, 0)) == -1


@pytest.mark.parametrize("name", MAIN_MAPS)
def test_9_zuraglal_achaalagdana(name):
    env = load(name)
    size = int(name[1:3])
    assert (env.width, env.height) == (size, size)
    assert env.is_free(env.start) and env.is_free(env.goal)
