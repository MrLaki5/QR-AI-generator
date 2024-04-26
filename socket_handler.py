from threading import Thread, Lock
from flask import current_app
from queue_safe import QueueSafe


class EmitData:
    def __init__(self, socket, channel, data):
        self.socket = socket
        self.channel = channel
        self.data = data


class SocketHandler(Thread):
    def __init__(self, app, socketio, connected_sockets):
        super(SocketHandler, self).__init__()
        self.app_context = app.app_context()
        self.socketio = socketio
        self.app = app
        self.lock = Lock()
        self.is_running = True
        self.emit_queue = QueueSafe(-1)
        self.connected_sockets = connected_sockets

    def stop_worker(self):
        with self.lock:
            self.is_running = False
        self.emit_queue.add(EmitData(None, None, None))

    def run(self):
        with self.app_context:
            current_app.logger.info(f"Socket Handler started")
        while True:
            emit_data = self.emit_queue.get()
            with self.lock:
                if not self.is_running:
                    break
            if self.connected_sockets.get(emit_data.socket):
                with self.app_context:
                    self.socketio.emit(emit_data.channel, emit_data.data, room=emit_data.socket)
            else:
                with self.app_context:
                    current_app.logger.info(f"Socket {emit_data.socket} not connected, message not sent")
        with self.app_context:
            current_app.logger.info(f"Socket Handler stopped")

    def emit(self, socket, channel, data):
        self.emit_queue.add(EmitData(socket, channel, data))
