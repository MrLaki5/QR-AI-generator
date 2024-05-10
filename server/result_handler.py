import threading
from flask import current_app
from connection.structures import Result
import json


class ResultHandler(threading.Thread):
    def __init__(self, socket_handler, redis_connector, app):
        super(ResultHandler, self).__init__()
        self.app_context = app.app_context()
        self.worker_lock = threading.Lock()
        self.is_running = True
        self.redis_connector = redis_connector
        self.socket_handler = socket_handler

    def stop_worker(self):
        self.redis_connector.push_in_queue(self.redis_connector.RESULT_QUEUE_NAME, json.dumps(Result().to_json()))
        with self.worker_lock:
            self.is_running = False

    def run(self):
        with self.app_context:
            current_app.logger.info(f"Result Handler started")
        while True:
            result = Result.from_json(json.loads(self.redis_connector.pop_from_queue(self.redis_connector.RESULT_QUEUE_NAME)[1]))
            with self.worker_lock:
                if not self.is_running:
                    break
            
            # Get sockets from waiting queue
            waiting_for_processing = self.redis_connector.get_all_from_queue(self.redis_connector.TASK_QUEUE_ID_NAME)

            # Check if any of waiting socket got closed
            queue_position = 1
            for socket_id in waiting_for_processing:
                self.socket_handler.emit(socket_id, "status", {"queue_position": queue_position})
                queue_position += 1

            # Emit results to connected socket
            if result.image != "":
                self.socket_handler.emit(result.socket_id, "result", {"image": result.image})
            else:
                self.socket_handler.emit(result.socket_id, "status", {"queue_position": 0})

        with self.app_context:
            current_app.logger.info(f"Result Handler stopped")
