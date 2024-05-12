import threading
from PIL import Image
import io
import os
import base64
import json
from qr_code_ai_generator import QRCodeAIGenerator
from connection.redis_connector import RedisConnector
from connection.structures import Result
from connection.structures import Task


try:
    redis_host = os.environ['REDIS_IP']
    redis_port = os.environ['REDIS_PORT']
    redis_password = os.environ['REDIS_PASSWORD']
except KeyError:
    print("All environment variables are not set: REDIS_IP, REDIS_PORT, REDIS_PASSWORD")
    quit(1)

redis_connector = RedisConnector(host=redis_host, port=redis_port, password=redis_password)
qr_code_gen = QRCodeAIGenerator()


def decode_image(image_str):
    # Decode the image data
    image_data = image_str.split(",")[1]  # Remove the base64 prefix
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))
    return image


def encode_image(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')  # Save image to byte array
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('ascii')  # Encode as base64
    return img_base64


def process():
    print("Worker started")
    while True:
        task_id = redis_connector.pop_from_queue(RedisConnector.TASK_QUEUE_ID_NAME)[1]
        task = Task.from_json(json.loads(redis_connector.get_from_set(RedisConnector.TASK_SET_DATA_NAME, task_id)))
        redis_connector.remove_from_set(RedisConnector.TASK_SET_DATA_NAME, task_id)

        print(f"Processing task for socket {task.socket_id}")
        
        # This will trigger result handler to know which sockets task is currently processing
        redis_connector.push_in_queue(redis_connector.RESULT_QUEUE_NAME, json.dumps(Result(task.socket_id, "").to_json()))

        if not redis_connector.check_in_set(redis_connector.CONNECTED_SOCKET_SET_NAME, task.socket_id):
            print(f"Socket {task.socket_id} disconnected, task removed")
            continue

        image = qr_code_gen.generate_ai_qr_code(task.qr_content, 
                                                decode_image(task.init_image), 
                                                task.prompt, 
                                                task.guidance_scale,
                                                task.controlnet_conditioning_scale, 
                                                task.strength)

        redis_connector.push_in_queue(RedisConnector.RESULT_QUEUE_NAME, json.dumps(Result(task.socket_id, encode_image(image)).to_json()))


if __name__ == "__main__":
    process()
