import threading

class Queue:
    def __init__(self, max_size=10):
        self.queue = []
        self.max_size = max_size
        self.condition = threading.Condition()

    def add(self, data):
        with self.condition:
            if len(self.queue) < self.max_size:
                self.queue.append(data)
                self.condition.notify()
                return True
            return False

    def get(self):
        with self.condition:
            while len(self.queue) == 0:
                self.condition.wait()
            data = self.queue.pop(0)
            return data

    def get_queue_size(self):
        with self.condition:
            return len(self.queue)

    def is_empty(self):
        with self.condition:
            return len(self.queue) == 0

    def clear(self):
        with self.condition:
            self.queue.clear()
