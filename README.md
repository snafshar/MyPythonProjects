# Python Projects

Practical Python exercises covering algorithms, concurrency, simulation, and networking.

## Projects

- `network_simulator.py` — reproducible graph topology, BFS routing, and network metrics
- `network_tools/network_health.py` — validates latency/loss measurements and classifies network health
- `projects/graph-bfs.py` — shortest-path reconstruction and hop distance
- `projects/task-pipeline.py` — bounded multi-worker pipeline with clean shutdown
- [AlgoKit](https://github.com/snafshar/MyPythonProjects/tree/main/python_practice/2026-10-16/algokit) — searching, counting, bracket validation, tests, and benchmark
- [Algorithm Workbench](https://github.com/snafshar/MyPythonProjects/tree/main/python_practice/2026-10-19/algorithm-workbench) — sorting, graph algorithms, dynamic programming, statistics, text tools, and disjoint-set union

The projects are dependency-light and designed to be readable, reproducible, and easy to extend.

## Run

```bash
python3 network_simulator.py
python3 network_tools/network_health.py
python3 projects/graph-bfs.py
python3 projects/task-pipeline.py
cd python_practice/2026-10-19/algorithm-workbench
python3 -m unittest discover -v
python3 benchmark_sorting.py --sizes 100 500 1000 --repeats 1
```

## Engineering practices

- Expand tests alongside features, including deterministic randomized cases.
- Keep benchmarks separate from correctness tests.
- State algorithm preconditions and complexity.
- Use CI workflows to exercise relevant project paths on supported Python versions.
