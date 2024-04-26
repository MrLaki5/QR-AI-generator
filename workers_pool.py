from queue_safe import QueueSafe
from worker import Worker
from task import Task
from result_handler import ResultHandler
from map_safe import MapSafe
from socket_handler import SocketHandler


class WorkersPool:
    def __init__(self, workers_count: int, queue_size: int, app, 
                 connected_sockets: MapSafe, socket_handler: SocketHandler):
        self.workers = []
        self.task_queue = QueueSafe(queue_size)
        self.result_queue = QueueSafe(queue_size)
        self.connected_sockets = connected_sockets
        self.socket_handler = socket_handler

        self.result_handler = ResultHandler(socket_handler=self.socket_handler,
                                            task_queue=self.task_queue,
                                            result_queue=self.result_queue,
                                            connected_sockets=self.connected_sockets,
                                            app=app)
        for i in range(workers_count):
            self.workers.append(Worker(id=i,
                                       task_queue=self.task_queue, 
                                       result_queue=self.result_queue,
                                       connected_sockets=self.connected_sockets,
                                       app=app))

    def start_workers(self):
        for worker in self.workers:
            worker.start()
        self.result_handler.start()

    def stop_workers(self):
        for i in range(len(self.workers)):
            self.task_queue.add(None)
        self.result_queue.add(None)

        for worker in self.workers:
            worker.stop_worker()
        self.result_handler.stop_worker()

        for worker in self.workers:
            worker.join()
        self.result_handler.join()

    def add_task(self, task: Task):
        return self.task_queue.add(task)
