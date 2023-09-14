import queue
import threading
import time
from statistics import LinearRegression

import torch
import numpy as np
from sklearn.decomposition import PCA
from scipy.sparse.csgraph import laplacian
from dockernizer import *
from sklearn.pipeline import Pipeline
from helpers.func_builder.compiler import *


class Estimator:
    def __init__(self, cluster_size):
        self.potential_tensor = np.array([])
        self.cluster_size = cluster_size
        self.potential_tensor_queue = queue.Queue()
        self.lambda_func = None

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

        stacked_tensors = torch.stack([])
        for _ in range(initial_count):
            tensor = self.potential_tensor_queue.get()
            lap = laplacian(tensor, normed=True)
            eigenvalues, eigenvectors = np.linalg.eigh(lap)
            # Use appropriate number of eigenvectors
            embedded_data = eigenvectors[:, :tensor.ndim]

            # PCA
            pca = PCA(n_components=0.95)
            reduced_data_pca = pca.fit_transform(embedded_data)
            stacked_tensors = torch.cat([stacked_tensors, reduced_data_pca])

        self.potential_tensor = torch.mean(stacked_tensors, dim=0)

        # If there are more tensors, start a new processing cycle
        if not self.potential_tensor_queue.empty():
            self.processing_tensor()
        else:
            self.processing.clear()  # Mark processing as done

    def build_estimator(self, task):
        profile = queue_task(task)
        model = Pipeline([
            ('tfidf', Compiler()),
            ('regressor', LinearRegression())
        ])

        # Build the lambda function from string
        self.lambda_func = eval(model.fit_predict(profile))
