from flask import Flask, request, jsonify
import threading
import queue
import time
from services.scheduler import Scheduler


app = Flask(__name__)

# Use a queue to handle incoming tasks
task_queue = queue.Queue()


@app.route('/submit_task', methods=['POST'])
def submit_task():
    # Get binary data from request
    task_data = request.data

    # Add task to queue
    task_queue.put(task_data)

    # Start a new thread to process tasks
    threading.Thread(target=process_tasks).start()

    return "Task submitted!", 202


def execute_task(task_data):
    # Simulate a task by sleeping; replace with actual task logic
    time.sleep(5)
    return f"Executed task with data: {task_data.decode('utf-8')}"


def process_tasks():
    while not task_queue.empty():
        task_data = task_queue.get()
        result = execute_task(task_data)
        # Here, you could send the result back to the requester,
        # save it to a database, etc.
        print(result)


if __name__ == '__main__':
    thread = Scheduler(interval=5)
    thread.run()

    app.run(debug=True, port=5000)
