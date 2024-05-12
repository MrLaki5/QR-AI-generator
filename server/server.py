from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
import logging
import atexit
import json
import os
from socket_handler import SocketHandler
from result_handler import ResultHandler
from connection.redis_connector import RedisConnector
from connection.structures import Task


logging.basicConfig(level=logging.INFO)

try:
    redis_host = os.environ['REDIS_IP']
    redis_port = os.environ['REDIS_PORT']
    redis_password = os.environ['REDIS_PASSWORD']
except KeyError:
    logging.error("All environment variables are not set: REDIS_IP, REDIS_PORT, REDIS_PASSWORD")
    quit(1)

app = Flask(__name__)
socketio = SocketIO(app, max_http_buffer_size=5 * 1024 * 1024) # 5 MB
redis_connector = RedisConnector(host=redis_host, port=redis_port, password=redis_password)

socket_handler = SocketHandler(app=app, 
                              socketio=socketio, 
                              redis_connector=redis_connector)
socket_handler.start()

result_handler = ResultHandler(app=app,
                               socket_handler=socket_handler,
                               redis_connector=redis_connector)
result_handler.start()


def shutdown():
    result_handler.stop_worker()
    socket_handler.stop_worker()
atexit.register(shutdown)


## WebSocket handlers
@socketio.on('connect')
def handle_connect():
    status = redis_connector.put_in_set(RedisConnector.CONNECTED_SOCKET_SET_NAME, request.sid, "1")
    if not status:
        logging.error(f"Failed to add client {request.sid} to connected sockets list.")

@socketio.on('disconnect')
def handle_disconnect():
    status = redis_connector.remove_from_set(RedisConnector.CONNECTED_SOCKET_SET_NAME, request.sid)
    if not status:
        logging.error(f"Failed to remove client {request.sid} from connected sockets list.")

@socketio.on("generate_ws")
def generate_ws(json_data):
    client_sid = request.sid
    logging.info(f"Client {client_sid} requested to generate a QR code.")

    qr_content=json_data['qr_content']
    prompt=json_data['prompt']
    guidance_scale=int(json_data['guidance_scale'])
    controlnet_conditioning_scale=float(json_data['controlnet_conditioning_scale'])
    strength=float(json_data['strength'])
    image_data = json_data['init_image']

    task = Task(socket_id=client_sid,
                qr_content=qr_content,
                prompt=prompt,
                guidance_scale=guidance_scale,
                controlnet_conditioning_scale=controlnet_conditioning_scale,
                strength=strength,
                init_image=image_data)

    redis_connector.put_in_set(RedisConnector.TASK_SET_DATA_NAME, client_sid, json.dumps(task.to_json()))
    redis_connector.push_in_queue(redis_connector.TASK_QUEUE_ID_NAME, client_sid)
    queue_position = redis_connector.get_queue_length(RedisConnector.TASK_QUEUE_ID_NAME)

    socket_handler.emit(client_sid, "status", {"queue_position": queue_position})


## REST API handlers
@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8089)
