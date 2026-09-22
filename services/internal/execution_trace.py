import threading


class ExecutionTrace:

    def __init__(self):
        self.events = []
        self._lock = threading.Lock()

    def add(self, event_type: str, **data):

        with self._lock:
            self.events.append({
                "step": len(self.events) + 1,
                "type": event_type,
                **data
            })

    def get_events(self):

        with self._lock:
            return list(self.events)

    def clear(self):

        with self._lock:
            self.events.clear()