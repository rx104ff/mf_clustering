import sys

from flask import Flask, request
import threading
import queue
import time
import numpy as np
from services.scheduler import Scheduler
from services.estimator import Estimator


app = Flask(__name__)

# Use a queue to handle incoming tasks
task_queue = queue.Queue()

estimator = None

lock = threading.Lock()


@app.route('/submit_task', methods=['POST'])
def submit_task():
    # Get binary data from request
    task_data = request.data

    # Add task to queue
    task_queue.put(task_data)

    # Start a new thread to process tasks
    threading.Thread(target=process_tasks).start()

    return "Task submitted!", 202


@app.route('/cluster', methods=['POST'])
def broadcast_cluster():
    estimator.enqueue_tensor(request.data)
    return "Submission succeeded", 200


def execute_task(task_data):
    # Simulate a task by sleeping; replace with actual task logic
    time.sleep(5)
    return f"Executed task with data: {task_data.decode('utf-8')}"


def process_tasks():
    while not task_queue.empty():
        task_data = task_queue.get()
        execute_task(task_data)


if __name__ == '__main__':
    # Initial cluster size
    estimator = Estimator(sys.argv[0])

    thread = Scheduler(interval=5,
                       emitter=broadcast_cluster,
                       estimator=estimator,
                       potential=np.empty((sys.argv[0],
                                           sys.argv[0])),
                       kwargs=sys.argv,
                       task_queue=task_queue)
    thread.run()

    app.run(debug=True, port=5000)
