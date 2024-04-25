from flask import Flask, render_template, request, send_file
from workers_pool import WorkersPool
from task import Task
import logging
import atexit


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
    task = Task(qr_content=request.form['qr_content'],
                prompt=request.form['prompt'],
                guidance_scale=request.form['guidance_scale'],
                controlnet_conditioning_scale=request.form['controlnet_conditioning_scale'],
                strength=request.form['strength'],
                init_image=request.files['init_image'])

    task_id = task.id
    add_result_status = workers_pool.add_task()

    return {"add_status": add_result_status, "task_id": task_id}


@app.route("/result/<task_id>", methods=['POST'])
def result(task_id):
    working_status, image = workers_pool.get_result(task_id)

    if result:
        # Save the image to a BytesIO object
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)  # Go to the beginning of the BytesIO stream

        return send_file(img_io, mimetype='image/png', as_attachment=True, attachment_filename='generated_qr.png')
    else:
        return {"working": working_status}


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8089)
