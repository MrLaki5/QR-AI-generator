from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
from map_safe import MapSafe
import base64
from workers_pool import WorkersPool
from socket_handler import SocketHandler
from task import Task
import logging
import atexit
from PIL import Image
import io


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
socketio = SocketIO(app)
connected_sockets = MapSafe()

socket_handler = SocketHandler(app=app, 
                              socketio=socketio, 
                              connected_sockets=connected_sockets)
socket_handler.start()

workers_pool = WorkersPool(workers_count=1,
                           queue_size=10,
                           app=app, 
                           connected_sockets=connected_sockets,
                           socket_handler=socket_handler)
workers_pool.start_workers()


def shutdown():
    workers_pool.stop_workers()
    socket_handler.stop_worker()
atexit.register(shutdown)


## WebSocket handlers
@socketio.on('connect')
def handle_connect():
    status = connected_sockets.add(request.sid, True)
    if not status:
        logging.error(f"Failed to add client {request.sid} to connected sockets list.")

@socketio.on('disconnect')
def handle_disconnect():
    status = connected_sockets.remove(request.sid)
    if not status:
        logging.error(f"Failed to remove client {request.sid} from connected sockets list.")

@socketio.on("generate_ws")
def generate_ws(json):
    client_sid = request.sid
    logging.info(f"Client {client_sid} requested to generate a QR code.")

    qr_content=json['qr_content']
    prompt=json['prompt']
    guidance_scale=int(json['guidance_scale'])
    controlnet_conditioning_scale=float(json['controlnet_conditioning_scale'])
    strength=float(json['strength'])

    image_data = json['init_image']
    # Decode the image data
    image_data = image_data.split(",")[1]  # Remove the base64 prefix
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))

    task = Task(socket_id=client_sid,
                qr_content=qr_content,
                prompt=prompt,
                guidance_scale=guidance_scale,
                controlnet_conditioning_scale=controlnet_conditioning_scale,
                strength=strength,
                init_image=image)

    queue_position = workers_pool.add_task(task)

    socket_handler.emit(client_sid, "status", {"queue_position": queue_position})


## REST API handlers
@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8089)
