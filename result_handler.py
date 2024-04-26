import threading
from flask import current_app
import io
import base64


class ResultHandler(threading.Thread):
    def __init__(self, socket_handler, task_queue, result_queue, connected_sockets, app):
        super(ResultHandler, self).__init__()
        self.app_context = app.app_context()
        self.result_queue = result_queue
        self.worker_lock = threading.Lock()
        self.is_running = True
        self.task_queue = task_queue
        self.connected_sockets = connected_sockets
        self.socket_handler = socket_handler

    def stop_worker(self):
        with self.worker_lock:
            self.is_running = False

    def _image_to_base64(self, img):
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')  # Save image to byte array
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('ascii')  # Encode as base64
        return img_base64

    def run(self):
        with self.app_context:
            current_app.logger.info(f"Result Handler started")
        while True:
            result = self.result_queue.get()
            with self.worker_lock:
                if not self.is_running:
                    break
            
            # Get sockets from waiting queue
            waiting_for_processing = self.task_queue.get_meta_lambda(lambda x: x.socket_id)

            # Check if any of waiting socket got closed
            queue_position = 1
            for socket_id in waiting_for_processing:
                if not self.connected_sockets.get(socket_id):
                    self.task_queue.remove_meta_lambda(lambda x: x.socket_id == socket_id)
                    waiting_for_processing.remove(socket_id)
                    with self.app_context:
                        current_app.logger.info(f"Socket {socket_id} disconnected, task removed")
                else:
                    self.socket_handler.emit(socket_id, "status", {"queue_position": queue_position})

            # Emit results to connected socket
            if result.image is not None:
                self.socket_handler.emit(result.socket_id, "result", {"image": self._image_to_base64(result.image)})
            else:
                self.socket_handler.emit(result.socket_id, "status", {"queue_position": 0})

        with self.app_context:
            current_app.logger.info(f"Result Handler stopped")
