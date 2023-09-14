import docker
from profiler import *


def queue_task(task):
    """
    Each time this function is called, a new Docker container is created
    to run the compiled profiler code.
    """

    with Profiler(task) as profiler:

        # 1. Compile the Python script to a binary
        subprocess.check_call(['pyinstaller', '--onefile', profiler.build(), '-n', 'compiled_profiler'])

        # 2. Set up the Docker client
        client = docker.from_env()

        configurations = [
            {"memory": "25m", "cpuset_cpus": "0"},
            {"memory": "50m", "cpuset_cpus": "0"},
            {"memory": "50m", "cpuset_cpus": "0,1"},
            {"memory": "100m", "cpuset_cpus": "0,1"},
        ]

        # 3. Build the Docker image
        current_dir = os.path.dirname(os.path.realpath(__file__))

        for config in configurations:
            print(f"Building image for configuration: {config}")

            # Re-build the image for every configuration to incorporate any changes in profiler_app
            client.images.build(path=current_dir, tag="profiler_app")

            print(f"Running with configuration: {config}")

            # Run a container with the given configuration
            container = client.containers.run(
                "profiler_app",
                detach=True,
                auto_remove=True,  # Remove the container after it exits
                mem_limit=config["memory"],
                cpuset_cpus=config["cpuset_cpus"]
            )

            # Wait for the container to finish
            result = container.wait()

            output = container.logs()

            return result["StatusCode"], output.decode("utf-8")
