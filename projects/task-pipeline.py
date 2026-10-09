"""Bounded worker pipeline with back-pressure, stable results, and clean shutdown."""

from queue import Queue
from threading import Thread


def run(values, workers=2):
    if workers < 1:
        raise ValueError("workers must be positive")
    queue, output = Queue(maxsize=max(4, workers * 2)), []
    lock = __import__("threading").Lock()

    def worker():
        while True:
            value = queue.get()
            try:
                if value is None:
                    return
                result = value * value
                with lock:
                    output.append((value, result))
            finally:
                queue.task_done()

    threads = [Thread(target=worker, name=f"worker-{i+1}") for i in range(workers)]
    for thread in threads:
        thread.start()
    for value in values:
        queue.put(value)
    for _ in threads:
        queue.put(None)
    queue.join()
    for thread in threads:
        thread.join()
    return [result for _, result in sorted(output)]


if __name__ == "__main__":
    print(run(range(10), workers=3))
