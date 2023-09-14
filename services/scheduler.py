import queue
import threading
from typing import Callable
import numpy as np
from http import HTTPStatus
from dockernizer import *


class Scheduler(threading.Thread):
    def __init__(self, interval: float, task_queue: queue, scheduler: Callable, emitter: Callable, estimator: Callable,
                 potential: np.matrix, **kwargs):
        super(Scheduler, self).__init__(**kwargs)
        self.interval = interval
        self.scheduler = scheduler
        self.stop_signal = threading.Event()  # Event flag to stop the thread
        self.potential = potential
        self.emitter = emitter
        self.estimator = estimator
        self.task_queue = task_queue
        self._lock = threading.Lock()

    def run(self, *args, **kwargs) -> None:
        self.estimator.processing_tensor()
        while not self.stop_signal.is_set():  # Keep running until stopped
            self.job(*args, **kwargs)
            queue_task(self.task_queue.get())

    def job(self, *args, **kwargs) -> None:
        # Execute the assessing_func
        self.scheduler(*args, **kwargs)

    def stop(self) -> None:
        self.stop_signal.set()

    async def send_broadcast(self) -> None:
        retry_counter = 0
        with self._lock:
            result = None
            while retry_counter < 5 and result != HTTPStatus.ACCEPTED:
                result = await self.emitter(self.potential)

    def receive_broadcast(self, potential) -> None:
        with self._lock:
            self.potential = potential
