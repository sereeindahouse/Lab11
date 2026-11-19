# Code guide: warehouse delivery robot

This project compares two ways to guide a robot from `S` to `G` through a grid
of warehouse shelves. A* finds a shortest path when movement is deterministic.
Value Iteration computes a policy that accounts for movement uncertainty.
Breadth-first search (BFS) provides a reference shortest-path cost for A*.

## Run the project

Run these commands from the repository root, with Python 3.10 or newer:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m warehouse.cli --map m10_b --algo astar
python -m warehouse.cli --map m05_a --algo vi --p 0.8 --episode --seed 42
python -m streamlit run app.py
```

The Streamlit demo opens at `http://localhost:8501` by default. It displays the
A* path, explored cells, VI values and policy arrows, and an episode step slider.
The CLI and core algorithms use only the Python standard library; plotting and
the Streamlit demo need the additional packages in `requirements.txt`.

## Where to read first

| File | Responsibility |
| --- | --- |
| [warehouse/env.py](../warehouse/env.py) | Grid loading, movement, rewards, transition probabilities, and text rendering. |
| [warehouse/maps.py](../warehouse/maps.py) | Loads the nine main maps by name. |
| [warehouse/astar.py](../warehouse/astar.py) | A*, BFS, path reconstruction, and path validation. |
| [warehouse/vi.py](../warehouse/vi.py) | Bellman updates, policy extraction, and sampled episodes. |
| [warehouse/cli.py](../warehouse/cli.py) | Command-line entry point for either algorithm. |
| [warehouse/viz.py](../warehouse/viz.py) | Matplotlib drawings shared by the demo and experiment scripts. |
| [app.py](../app.py) | Local Streamlit interface. |
| [public/index.html](../public/index.html) | Browser interface with SVG drawings and episode playback. |
| [api/solve.py](../api/solve.py) | HTTP handler for the browser interface. |
| [warehouse/web.py](../warehouse/web.py) | Request validation, cached planning, and JSON response assembly. |
| [scripts/](../scripts/) | Map generation and experiment exports. |
| [tests/](../tests/) | Checks for the environment, search, VI, and web response logic. |

The shared flow is: load a map, construct a `GridWorld`, run a planner, and
display its result. For VI, the caller can also simulate an episode using the
computed policy.

## Environment and map format

A state is an `(x, y)` coordinate: `x` is the column, `y` is the row, and `(0, 0)`
is the top-left cell. Text grids are indexed as `grid[y][x]`.

| Symbol | Meaning |
| --- | --- |
| `S` | Starting cell |
| `G` | Delivery goal |
| `.` | Free cell |
| `#` | Shelf or wall |

Actions are `U`, `D`, `L`, and `R`. A move into a shelf or outside the grid leaves
the robot in its current cell. `neighbors()` excludes these stationary moves
for A* and BFS; `transitions()` includes their probability for VI.

The parameter `p` is the probability of moving in the chosen direction. Each
perpendicular direction has probability `(1 - p) / 2`. For example, choosing
`R` with `p=0.8` means 80% right, 10% up, and 10% down. If several outcomes
land in the same cell, `transitions()` adds their probabilities together.

Entering the goal earns `+50`; every other step earns `-1`, including a blocked
move. Episodes stop on reaching the goal. VI keeps `V(G)=0` and excludes the
goal from the policy, so it does not collect the delivery reward repeatedly.

Map names use `m05`, `m10`, and `m20` for 5×5, 10×10, and 20×20 grids.
The 5×5 maps are hand-written examples. For the larger maps, `a` uses shelf
rows, `b` uses alternating gaps that force detours, and `c` uses approximately
25% random obstacles with seed 42 and a BFS reachability check.
`no_path` deliberately blocks access to the goal.

## A* and BFS

`astar()` maintains a priority queue ordered by `f = g + h`:

- `g` is the number of moves from the start to the current cell.
- `h` is the Manhattan distance, `abs(x - goal_x) + abs(y - goal_y)`.
- With the default `tie_break="h"`, equal `f` values prefer smaller `h`.
  With `tie_break="fifo"`, they prefer earlier queue entries.

`g_best` stores the lowest discovered cost for each cell. `parent` records how
to reconstruct the path. `closed` prevents processing an already expanded
cell again. The Manhattan heuristic is consistent for this four-direction,
unit-cost grid, which makes this closed-set approach valid.

On success, `SearchResult.path` includes both start and goal, and `cost` is
`len(path) - 1`. If no path exists, both fields are `None`. `expanded_order`
records processed cells, including the goal when reached, for visualization.

BFS uses a FIFO queue and no heuristic. Since all moves cost one, its optimal
path cost should match A*. A* does not model slipping: its path always assumes
`p=1`, even when the interface uses a different `p` for VI.

## Value Iteration and episodes

`value_iteration()` starts every state's value at zero and repeatedly applies:

```text
Q(s, a) = sum over s' of P(s' | s, a) * (R(s, a, s') + gamma * V(s'))
V_new(s) = max over a of Q(s, a)
```

Each sweep uses the previous value table for every state, then replaces the
whole table. This synchronous update makes the result independent of the order
in which cells are visited during a sweep. The goal remains fixed at zero.

Defaults are `gamma=0.95`, `theta=1e-6`, and `max_iter=10000`. Iteration stops
when the maximum absolute change is below `theta` or the iteration limit is
reached. Check `VIResult.converged` to distinguish those outcomes. `deltas`
stores the maximum change from every sweep for the convergence plot.

`greedy_policy()` selects the action with the greatest expected value at each
non-goal cell. Exact ties follow the action order `U`, `D`, `L`, `R`.
See the [worked calculation](gar_tootsoo.md) for a three-cell example.

`run_episode()` starts at `S`, looks up the policy action, samples the actual
movement, and accumulates rewards. It stops at the goal or after 200 steps by
default. A fixed random seed makes the sampled trail reproducible for the same
map, policy, and `p`. The returned `return` is the **undiscounted** sum of sampled
rewards; `V[start]` estimates **discounted expected** rewards. These are different
measurements and need not match.

A converged value function does not prove the goal is reachable. On `no_path`,
A* reports no path and the VI episode ends unsuccessfully at its step limit.

## Browser API

The browser requests an endpoint such as:

```text
GET /api/solve?map=m05_a&p=0.8&gamma=0.95&seed=42
```

`api/solve.py` parses the query, calls `parse_params()` and `solve()` from
`warehouse/web.py`, and returns JSON. Invalid parameters produce HTTP 400
with an `error` message.

| Parameter | Default | Accepted values |
| --- | --- | --- |
| `map` | `m05_a` | The nine main map names or `no_path`. |
| `p` | `0.8` | `1.0`, `0.9`, `0.8`, or `0.7`. |
| `gamma` | `0.95` | `0.80` through `0.99`, inclusive. |
| `seed` | `42` | An integer from `0` through `1000000`. |

`p` and `gamma` are rounded to two decimal places before validation. These
checks belong to the web layer; direct Python calls do not apply them.

The response groups results into `map`, `astar`, `bfs`, `vi`, and `episode`.
For JSON compatibility, VI values are lists of `[x, y, value]` and the policy
is a list of `[x, y, action]`. The browser draws these results as SVG.

Planning is cached in memory for up to 64 `(map, p, gamma)` combinations.
Changing only the seed reuses the plan and samples another episode. Cached
planning times describe the original computation; timing fields may vary
across uncached runs. Successful HTTP responses also request a one-day shared
cache lifetime.

`vercel.json` includes `warehouse/` and `maps/` in the Python function and sets
its maximum duration to 30 seconds. The browser page requires `/api/solve`;
opening `public/index.html` alone does not run the backend. Use the Streamlit
command above for the local demo.

## Experiments and verification

```bash
python scripts/make_maps.py
python scripts/run_astar.py
python scripts/run_vi.py
```

`make_maps.py` rewrites the map files. `run_astar.py` writes
`results/astar_results.csv` and `results/astar_paths.png`; timing columns use
the median of 30 runs. `run_vi.py` evaluates the nine maps at `p=1` and `p=0.8`,
uses the median of five planning runs, and writes `vi_results.csv`,
`vi_convergence.csv`, `vi_convergence.png`, and `vi_policy_p08.png` under
`results/`. Re-running experiments replaces these outputs and can change the
timing measurements. The VI script measures planning; the 900-episode
evaluation remains a separate milestone in the README.

Run `python -m pytest -q` to check movement and transition behavior, A* costs
against BFS, VI against worked examples, episode behavior, and web parameter
validation and JSON serialization. `tests/test_web.py` exercises the Python
response logic directly; it does not test a deployed HTTP server or browser.
