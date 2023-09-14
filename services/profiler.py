import psutil
import subprocess
import time
import pandas as pd
import os
import tempfile


class Profiler:
    def __init__(self, byte_arr):
        self.binary_tmp = tempfile.NamedTemporaryFile(delete=False)
        self.script_tmp = tempfile.NamedTemporaryFile(delete=False)

        # Save binary to a path
        self.binary_tmp.write(byte_arr)
        self.binary_path = self.binary_tmp.name

        self.result = ''

    def __exit__(self, exc_type, exc_value, traceback):
        # Delete the temporary file upon exiting the context
        os.remove(self.binary_tmp.name)
        os.remove(self.script_tmp.name)

    def build(self):
        with open(__file__,
                  'r') as current_file:  # __file__ is a built-in variable that contains the script's own filename
            content = current_file.read()

        with open(self.script_tmp, 'w') as output_file:
            output_file.write(content)

    def execute_and_profile(self, duration=5):
        # Start the binary executable as a subprocess
        process = subprocess.Popen(self.binary_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pid = process.pid

        # Initial metrics
        cpu_percentages = []
        memory_usages = []
        io_data = {'read_bytes': [], 'write_bytes': []}
        net_io = {'sent': [], 'received': []}

        start_time = time.time()
        end_time = start_time + duration

        try:
            while time.time() < end_time:
                # Check if process is still running
                if psutil.pid_exists(pid):
                    proc = psutil.Process(pid)

                    # Gather profiling data
                    cpu_percentages.append(proc.cpu_percent(interval=0.1))
                    memory_usages.append(proc.memory_info().rss)
                    io_data['read_bytes'].append(proc.io_counters().read_bytes)
                    io_data['write_bytes'].append(proc.io_counters().write_bytes)
                    net_io_counters = psutil.net_io_counters()
                    net_io['sent'].append(net_io_counters.bytes_sent)
                    net_io['received'].append(net_io_counters.bytes_recv)
                else:
                    # If process ends before the profiling duration, break out of the loop
                    break
        finally:
            # Terminate the process if still running
            if psutil.pid_exists(pid):
                process.terminate()

        data = {
            'avg_cpu': sum(cpu_percentages) / len(cpu_percentages) if cpu_percentages else 0,
            'peak_cpu': max(cpu_percentages) if cpu_percentages else 0,
            'std_cpu': pd.Series(cpu_percentages).std(),
            'avg_memory': sum(memory_usages) / len(memory_usages) if memory_usages else 0,
            'peak_memory': max(memory_usages) if memory_usages else 0,
            'std_memory': pd.Series(memory_usages).std(),
            'total_io_read': sum(io_data['read_bytes']),
            'total_io_write': sum(io_data['write_bytes']),
            'total_net_sent': sum(net_io['sent']),
            'total_net_received': sum(net_io['received']),
            'binary_size': os.path.getsize(self.binary_path),
            'system_ram': psutil.virtual_memory().total,
            'system_cpu_cores': psutil.cpu_count(),
            'system_load_avg': sum(psutil.getloadavg()) / 3,  # Average of 1, 5, and 15 minute load averages
            'python_version': os.sys.version_info.major,  # Capturing Python major version
        }

        # Convert to DataFrame
        df = pd.DataFrame([data])
        self.result = df.to_csv(index=False, path_or_buf=None)
