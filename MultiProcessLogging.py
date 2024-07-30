import logging
import logging.handlers
import numpy as np
import time
import multiprocessing
import pandas as pd
log_file = 'D:\\git\\Parallel-fdc\\logs\\fdc_manager\\multiProcessLogging.log'

def listener_configurer():
    root = logging.getLogger()
    h = logging.FileHandler(log_file)
    f = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)

# This is the listener process top-level loop: wait for logging events
# (LogRecords)on the queue and handle them, quit when you get a None for a
# LogRecord.
def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:  # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)  # No level or filter logic applied - just do it!
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def worker_configurer(queue):
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    # send all messages, for demo; no other level or filter logic applied.
    root.setLevel(logging.DEBUG)


# This is the worker process top-level loop, which just logs ten events with
# random intervening delays before terminating.
# The print messages are just so you know it's doing something!
def worker_function(sleep_time, name, queue, configurer):
    configurer(queue)
    start_message = 'Worker {} started and will now sleep for {}s'.format(name, sleep_time)
    logging.info(start_message)
    time.sleep(sleep_time)
    success_message = 'Worker {} has finished sleeping for {}s'.format(name, sleep_time)
    logging.info(success_message)

def main_with_process():
    start_time = time.time()
    single_thread_time = 0.
    queue = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(target=listener_process,
                                       args=(queue, listener_configurer))
    listener.start()
    workers = []
    for i in range(10):
        name = str(i)
        sleep_time = np.random.randint(10) / 2
        single_thread_time += sleep_time
        worker = multiprocessing.Process(target=worker_function,
                                         args=(sleep_time, name, queue, worker_configurer))
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()
    queue.put_nowait(None)
    listener.join()
    end_time = time.time()
    final_message = "Script execution time was {}s, but single-thread time was {}s".format(
        (end_time - start_time),
        single_thread_time
    )
    print(final_message)

if __name__ == "__main__":
    main_with_process()