"""XI долоо хоногийн тест: замтай, замгүй, эхлэл=зорилго + BFS тулгалт (Сэргэлэн)."""
import pytest

from warehouse.astar import astar, bfs, is_valid_path, manhattan
from warehouse.env import GridWorld
from warehouse.maps import MAIN_MAPS, load


def test_1_zamtai():
    env = load("m05_a")
    r = astar(env)
    assert r.path is not None and is_valid_path(env, r.path)
    assert r.cost == 8 == len(r.path) - 1


def test_2_zamgui():
    env = load("no_path")
    r = astar(env)
    assert r.path is None and r.cost is None
    # хүрч болох бүх нүдийг нээгээд зогссон байх ёстой
    assert r.expanded == bfs(env).expanded


def test_3_ekhlel_ni_zorilgo():
    env = GridWorld.from_string("""
    S..
    .#.
    ..G
    """)
    r = astar(env, start=env.goal)
    assert r.path == [env.goal] and r.cost == 0 and r.expanded == 1


@pytest.mark.parametrize("name", MAIN_MAPS)
def test_bfs_tulgalt_9_zuraglal(name):
    env = load(name)
    a, b = astar(env), bfs(env)
    assert a.cost == b.cost                      # A* оновчтой
    assert is_valid_path(env, a.path)
    assert a.expanded <= b.expanded              # эвристик хайлтыг багасгана (≤)


def test_manhattan_hetruulehgui():
    # бүх нүдэнд h(s) <= бодит зай (BFS)  -> admissible
    env = load("m10_b")
    for s in env.states():
        real = bfs(env, start=s).cost
        if real is not None:
            assert manhattan(s, env.goal) <= real
