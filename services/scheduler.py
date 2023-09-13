import threading
import time
from typing import Callable
import numpy as np
from http import HTTPStatus


class Scheduler(threading.Thread):
    def __init__(self, interval: float, scheduler: Callable, emitter: Callable, potential: np.matrix, *args, **kwargs):
        super(Scheduler, self).__init__(*args, **kwargs)
        self.interval = interval
        self.scheduler = scheduler
        self.func_args = args
        self.stop_signal = threading.Event()  # Event flag to stop the thread
        self.potential = potential
        self.emitter = emitter
        self._lock = threading.Lock()

    def run(self, *args, **kwargs) -> None:
        while not self.stop_signal.is_set():  # Keep running until stopped
            self.job(*args, **kwargs)
            time.sleep(self.interval)

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
