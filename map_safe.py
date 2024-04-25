from threading import Lock

class MapSafe:
    def __init__(self):
        self.data = {}
        self.lock = Lock()

    def add(self, key, value):
        with self.lock:
            if key in self.data:
                return False
            self.data[key] = value
            return True

    def get(self, key):
        with self.lock:
            if key in self.data:
                return self.data[key]
            return None

    def cleanup(self, lambda_delete_func):
        with self.lock:
            for key in list(self.data.keys()):
                if lambda_delete_func(self.data[key]):
                    del self.data[key]

    def remove(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                return True
            return False
