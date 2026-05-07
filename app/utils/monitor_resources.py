# /app/utils/monitor_resources.py

import threading
import time

import psutil

from app.utils.logger_util import get_logger

logger = get_logger()


def monitor_resources(interval=10):
    process = psutil.Process()
    mem_max = 0
    cpu_max = 0
    while True:
        mem_mb = process.memory_info().rss / 1024 ** 2
        cpu_percent = process.cpu_percent(interval=1)
        is_logged = False
        if mem_mb > mem_max:
            mem_max = mem_mb
            is_logged = True
        if cpu_percent > cpu_max:
            cpu_max = cpu_percent
            is_logged = True
        if is_logged:
            logger.warning(
                f"[RESOURCE] Memory: {mem_mb:.2f}/{mem_max:.2f} (MB) | CPU: {cpu_percent:.2f}/{cpu_max:.2f}(%)")
        time.sleep(interval - 1)  # subtract the 1s used by cpu_percent
        if mem_mb > 5500:
            logger.warning("Warning: Memory usage approaching ECS limit!")


# Start the monitor in the background
def start_monitor_daemon():
    threading.Thread(target=lambda: time.sleep(5) or monitor_resources(10), daemon=True).start()
