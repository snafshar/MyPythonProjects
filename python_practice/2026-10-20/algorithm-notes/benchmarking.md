# Repeatable Python Microbenchmarks

Separate setup from the operation being measured. Use `time.perf_counter()`, run several repeats, and report median plus spread. Benchmark realistic input sizes and data distributions. Record Python version, platform, input size, and random seed. Keep correctness checks outside timed sections where possible.

One timing run is not a universal ranking: interpreter warm-up, CPU load, caches, and allocation can affect results. Profile real workloads before optimizing.