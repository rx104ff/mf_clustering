import docker
import os
import subprocess


def queue_task(task):
    """
    Simulate queuing a task. Here, the task is the profiler app.
    Each time this function is called, a new Docker container is created
    to run the compiled profiler code.
    """
    # 1. Compile the Python script to a binary
    subprocess.check_call(['pyinstaller', '--onefile', 'profiler_app.py', '-n', 'compiled_profiler'])

    # 2. Set up the Docker client
    client = docker.from_env()

    # 3. Build the Docker image
    current_dir = os.path.dirname(os.path.realpath(__file__))
    client.images.build(path=current_dir, tag="profiler_app")

    # 4. Run the Docker container
    container = client.containers.run(
        "profiler_app",
        detach=True,
        auto_remove=True
    )
    container.wait()


# Example: Queue a task
queue_task('some_task')
