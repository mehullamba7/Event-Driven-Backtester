from queue import Queue, Empty


class EventQueue:
    def __init__(self):
        self._q = Queue()

    def put(self, event):
        self._q.put(event)

    def get_nowait(self):
        try:
            return self._q.get_nowait()
        except Empty:
            return None

    def empty(self):
        return self._q.empty()
