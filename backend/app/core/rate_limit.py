import time
from collections import defaultdict, deque
from threading import Lock


MAX_REQUESTS = 5
WINDOW_SECONDS = 60


_request_history: dict[str, deque[float]] = defaultdict(deque)

_lock = Lock()


def check_rate_limit(key: str) -> bool:
    now = time.time()

    with _lock:
        timestamps = _request_history[key]

        while timestamps and now - timestamps[0] > WINDOW_SECONDS:
            timestamps.popleft()

        if len(timestamps) >= MAX_REQUESTS:
            return False

        timestamps.append(now)

        return True