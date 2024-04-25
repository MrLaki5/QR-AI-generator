import threading
from worker import WorkerResult
from map_safe import MapSafe


class RegisterData:
    def __init__(self, result: WorkerResult):
        self.result = result
        self.timestamp = int(time.time())


class ResultRegister(threading.Thread):
    def __init__(self, result_queue, working_map, cleanup_interval_s=300, app):
        super(ResultRegister, self).__init__()
        self.app_context = app.app_context()
        self.result_queue = result_queue
        self.register = MapSafe()
        self.working_map = working_map
        self.worker_lock = threading.Lock()
        self.is_running = True
        self.cleanup_interval_s = cleanup_interval_s

    def stop_worker(self):
        with self.worker_lock:
            self.is_running = False

    def run(self):
        with self.app_context:
            current_app.logger.debug(f"Result Register started")
        while True:
            result = self.result_queue.get()
            with self.worker_lock:
                if not self.is_running:
                    break
            
            self.register.add(result.id, RegisterData(result))
            self.register.cleanup(lambda x: int(time.time()) - x.timestamp > cleanup_interval_s)

        with self.app_context:
            current_app.logger.debug(f"Result Register stopped")

    def get_result(self, id):
        still_working = self.working_map.get(id)
        result = self.register.get(id)

        if result:
            result = result.result.image

        return still_working, result
