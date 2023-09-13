import queue
import threading
import time
import numpy as np


class Estimator:
    def __init__(self, cluster_size):
        self.potential_tensor = np.array([])
        self.cluster_size = cluster_size
        self.potential_tensor_queue = queue.Queue()

        self.processing = threading.Event()  # An event to track if processing is ongoing

    def enqueue_tensor(self, potential_tensor):
        self.potential_tensor_queue.put(potential_tensor)

        # If processing is not ongoing, start processing
        if not self.processing.is_set():
            threading.Thread(target=self.processing_tensor).start()

    def processing_tensor(self):
        self.processing.set()  # Mark processing as ongoing

        # Wait for 5 seconds to accumulate tensors
        time.sleep(5)

        initial_count = self.potential_tensor_queue.qsize()  # Number of tensors at the start of processing
        for _ in range(initial_count):
            tensor = self.potential_tensor_queue.get()

        # If there are more tensors, start a new processing cycle
        if not self.potential_tensor_queue.empty():
            self.processing_tensor()
        else:
            self.processing.clear()  # Mark processing as done
