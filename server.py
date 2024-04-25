from flask import Flask, render_template, request, send_file
from workers_pool import WorkersPool
from task import Task
import logging
import atexit
from PIL import Image
import io


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

workers_pool = WorkersPool(workers_count=1, queue_size=10, cleanup_interval_s=300, app=app)
workers_pool.start_workers()


def shutdown():
    workers_pool.stop_workers()
atexit.register(shutdown)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/generate", methods=['POST'])
def generate():
    qr_content=request.form['qr_content']
    prompt=request.form['prompt']
    guidance_scale=int(request.form['guidance_scale'])
    controlnet_conditioning_scale=float(request.form['controlnet_conditioning_scale'])
    strength=float(request.form['strength'])
    init_image=request.files['init_image']

    file = request.files['init_image']
    image = None
    if file:
        # Read the file data into a bytes object
        image_bytes = file.read()

        # Convert bytes to a PIL image
        image = Image.open(io.BytesIO(image_bytes))
    else:
        return {"add_status": False, "message": "No image file provided"}


    task = Task(qr_content=qr_content,
                prompt=prompt,
                guidance_scale=guidance_scale,
                controlnet_conditioning_scale=controlnet_conditioning_scale,
                strength=strength,
                init_image=image)

    task_id = task.id
    add_result_status = workers_pool.add_task(task)

    return {"add_status": add_result_status, "task_id": task_id}


@app.route("/result/<task_id>", methods=['POST'])
def result(task_id):
    working_status, image = workers_pool.get_result(task_id)

    if image:
        # Save the image to a BytesIO object
        img_io = io.BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)  # Go to the beginning of the BytesIO stream

        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='generated_qr.png')
    else:
        return {"working": working_status}


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8089)
