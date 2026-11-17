"""Вэб API-ийн (warehouse/web.py) тест."""
import json

import pytest

from warehouse.web import ALL_MAPS, BadRequest, parse_params, solve


@pytest.mark.parametrize("name", ALL_MAPS)
def test_solve_json_bolno(name):
    out = solve(*parse_params({"map": name, "p": "0.8", "gamma": "0.95", "seed": "42"}))
    json.dumps(out)                                   # JSON болгож чадах ёстой
    m = out["map"]
    assert len(out["vi"]["V"]) == m["free_cells"]
    assert out["episode"]["trail"][0] == m["start"]
    if name == "no_path":
        assert out["astar"]["path"] is None and not out["episode"]["success"]
    else:
        assert out["astar"]["cost"] == out["bfs"]["cost"]


@pytest.mark.parametrize("q", [{"map": "nope"}, {"p": "0.5"}, {"gamma": "2"},
                               {"seed": "abc"}, {"seed": "-1"}])
def test_buruu_oroltyg_tatgalzana(q):
    with pytest.raises(BadRequest):
        parse_params(q)
