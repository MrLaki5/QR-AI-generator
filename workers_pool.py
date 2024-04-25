from queue_safe import QueueSafe
from worker import Worker
from task import Task
from result_register import ResultRegister
from map_safe import MapSafe


class WorkersPool:
    def __init__(self, workers_count: int, queue_size: int, cleanup_interval_s: int, app):
        self.workers = []
        self.working_map = MapSafe()
        self.task_queue = QueueSafe(queue_size)
        self.result_queue = QueueSafe(queue_size)

        self.result_register = ResultRegister(self.result_queue, self.working_map, cleanup_interval_s, app)
        for i in range(workers_count):
            self.workers.append(Worker(i, self.task_queue, self.working_map, self.result_queue, app))

    def start_workers(self):
        for worker in self.workers:
            worker.start()
        self.result_register.start()

    def stop_workers(self):
        for i in range(len(self.workers)):
            self.task_queue.add(None)
        self.result_queue.add(None)

        for worker in self.workers:
            worker.stop_worker()
        self.result_register.stop_worker()

        for worker in self.workers:
            worker.join()
        self.result_register.join()

    def add_task(self, task: Task):
        return self.task_queue.add(task)

    def get_result(self, id):
        return self.result_register.get_result(id)
