import threading
from qr_code_ai_generator import QRCodeAIGenerator
from flask import current_app
from PIL import Image

class WorkerResult:
    def __init__(self, id: int, image: Image):
        self.id = id
        self.image = image

class Worker(threading.Thread):
    def __init__(self, id, task_queue, working_map, result_queue, app):
        super(Worker, self).__init__()
        self.id = id
        self.app_context = app.app_context()
        self.worker_lock = threading.Lock()
        self.qr_code_gen = QRCodeAIGenerator()
        self.task_queue = task_queue
        self.is_running = True
        self.working_map = working_map

    def stop_worker(self):
        with self.worker_lock:
            self.is_running = False

    def run(self):
        with self.app_context:
            current_app.logger.debug(f"Worker started, id: {self.id}")
        while True:
            task = self.task_queue.get()
            self.working_map.add(task.id, True)
            with self.worker_lock:
                if not self.is_running:
                    break
            image = self.qr_code_gen.generate_ai_qr_code(task.qr_content, 
                                                         task.init_image, 
                                                         task.prompt, 
                                                         task.guidance_scale,
                                                         task.controlnet_conditioning_scale, 
                                                         task.strength)

            self.result_queue.add(WorkerResult(task.id, image))
            self.working_map.erase(task.id)
        with self.app_context:
            current_app.logger.debug(f"Worker stopped, id: {self.id}")
