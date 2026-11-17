# Агуулахын хүргэлтийн робот — Gridworld MDP, A* ба Value Iteration

CSEX5064 · Компьютерын ухааны туршилт IV · Б.Сэргэлэн (s22c064b), Ариунбилэг (s22c021b)

Нэг робот, нэг хүргэлтийн цэг, хөдөлгөөнгүй тавиуртай нүдэн агуулахад
**A\*** (тодорхой орчин, p=1) болон **Value Iteration** (магадлалт орчин, p=0.8) аргуудыг
өөрсдөө хэрэгжүүлж харьцуулна.

## Суулгах, ажиллуулах

```bash
pip install -r requirements.txt
python -m pytest                 # 59 тест
python scripts/make_maps.py      # maps/*.txt дахин үүсгэх (seed=42)
python scripts/run_astar.py      # results/astar_results.csv, astar_paths.png
python scripts/run_vi.py         # results/vi_results.csv, vi_convergence.*, vi_policy_p08.png
python -m warehouse.cli --map m10_b --algo astar          # командын мөрийн хувилбар
python -m warehouse.cli --map m05_a --algo vi --p 0.8 --episode
python -m streamlit run app.py   # демо (хөтөч дээр http://localhost:8501)
```

> **Windows тэмдэглэл.** `streamlit.exe`, `jupyter.exe` зэрэг файлыг Smart App Control хаавал
> `python -m streamlit ...`, `python -m pytest` гэж `python -m`-ээр ажиллуулна.
> Монгол үсэг консолд зөв гарахын тулд CLI болон `make_maps.py` гаралтаа UTF-8 болгодог.

## Бүтэц

| Файл | Агуулга | Долоо хоног | Хариуцагч |
|---|---|---|---|
| `warehouse/env.py` | Орчин: хил/саад, p=1 ба p=0.8 шилжилт, шагнал | X | Ариунбилэг |
| `scripts/make_maps.py`, `maps/` | 9 зураглал + `no_path` | X | Ариунбилэг |
| `warehouse/astar.py` | A* (Манхэттэн h), BFS тулгалт | XI | Сэргэлэн |
| `scripts/run_astar.py` | A* хэмжилт → CSV, зураг | XI | Сэргэлэн |
| `warehouse/viz.py`, `warehouse/cli.py`, `app.py` | Зураг, CLI, Streamlit прототип | XII | Хамт |
| `warehouse/vi.py` | Value Iteration, policy, нэг оролдлого | XIII | Ариунбилэг |
| `scripts/run_vi.py`, `docs/gar_tootsoo.md` | VI хэмжилт, гар тооцоо | XIII | Ариунбилэг |
| `experiments.ipynb` | Бүх туршилтыг нэг дор | X–XIII | Хамт |
| `tests/` | env 16, A* 13, VI 30 тест | X–XIII | |

## Загвар

* Төлөв: (x, y) — x багана, y мөр (дээрээс доош). Үйлдэл: U, D, L, R.
* Саад/хил рүү чиглэвэл байрандаа үлдэнэ.
* p=1: 100% сонгосон чиглэл. p=0.8: 80% сонгосон, хоёр хажуу тус бүр 10%.
* Шагнал: G-д орох +50, бусад алхам −1; G-д хүрмэгц дуусна. γ = 0.95, θ = 10⁻⁶.
* Зураглалын тэмдэгт: `.` чөлөөт, `#` тавиур, `S` эхлэл, `G` хүргэлтийн цэг.
  `a` — тавиурын эгнээ, `b` — могой хэлбэрийн (тойрох) тавиур, `c` — seed=42 санамсаргүй 25% саад.

## Явц

- [x] X: орчин, 9 зураглал, тест
- [x] XI: A*, BFS тулгалт, 3 үндсэн тест, хэмжилт
- [x] XII: CLI + Streamlit прототип
- [x] XIII: Value Iteration, үйлдэл сонголт, гар тооцоо, нийлэлтийн график
- [ ] XIV: p=1 харьцуулалт, p=0.8 үед 900 оролдлого → CSV
- [ ] XV–XVI: тайлан, демо, эцсийн багц
