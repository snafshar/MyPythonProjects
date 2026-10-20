# Repeatable Python Microbenchmarks

- Separate setup from the operation being measured.
- Use `time.perf_counter()` for elapsed time.
- Run several repeats and report median plus spread.
- Benchmark realistic input sizes and data distributions.
- Keep correctness assertions outside timed sections where possible.
- Record Python version, platform, input size, and random seed.

Do not treat one timing run as a universal ranking. Interpreter warm-up, CPU load, caches, and allocation can change results. Prefer profiling before optimizing a real workload.
