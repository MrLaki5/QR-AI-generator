import threading

class QueueSafe:
    def __init__(self, max_size=10):
        self.queue = []
        self.max_size = max_size
        self.condition = threading.Condition()

    def add(self, data):
        with self.condition:
            if len(self.queue) < self.max_size or self.max_size == -1:
                self.queue.append(data)
                self.condition.notify()
                return len(self.queue)
            return -1

    def get(self):
        with self.condition:
            while len(self.queue) == 0:
                self.condition.wait()
            data = self.queue.pop(0)
            return data

    def get_meta_lambda(self, lambda_func):
        with self.condition:
            return_list = []
            for data in self.queue:
                return_list.append(lambda_func(data))
            return return_list

    def remove_meta_lambda(self, lambda_func):
        with self.condition:
            for data in self.queue:
                if lambda_func(data):
                    self.queue.remove(data)

    def get_queue_size(self):
        with self.condition:
            return len(self.queue)

    def is_empty(self):
        with self.condition:
            return len(self.queue) == 0

    def clear(self):
        with self.condition:
            self.queue.clear()
