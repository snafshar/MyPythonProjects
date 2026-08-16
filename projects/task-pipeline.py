"""I implemented a bounded worker pipeline with explicit shutdown."""
from queue import Queue
from threading import Thread

def run(values, workers=2):
    queue, output = Queue(4), []
    def worker():
        while True:
            value = queue.get()
            if value is None: queue.task_done(); return
            output.append(value * value); queue.task_done()
    threads=[Thread(target=worker) for _ in range(workers)]
    for thread in threads: thread.start()
    for value in values: queue.put(value)
    for _ in threads: queue.put(None)
    queue.join()
    for thread in threads: thread.join()
    return sorted(output)

if __name__ == '__main__': print(run(range(10)))