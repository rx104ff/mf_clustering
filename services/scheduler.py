import threading
import time


class Scheduler(threading.Thread):
    def __init__(self, interval, scheduler, *args, **kwargs):
        super(Scheduler, self).__init__(*args, **kwargs)
        self.interval = interval
        self.scheduler = scheduler
        self.func_args = args
        self.stop_signal = threading.Event()  # Event flag to stop the thread

    def run(self, *args, **kwargs):
        while not self.stop_signal.is_set():  # Keep running until stopped
            self.job(*args, **kwargs)
            time.sleep(self.interval)

    def job(self, *args, **kwargs):
        # Execute the assessing_func
        self.scheduler(*args, **kwargs)

    def stop(self):
        self.stop_signal.set()

    def broadcast(self):
        return
