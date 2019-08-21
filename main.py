import json
import logging

from flask import Flask, render_template, make_response, jsonify, request

import configurations
import logHandler
from dataLoader import DataLoader

from vistDataset import VistDataset
import base64

app = Flask(__name__)
data_loader = DataLoader(root_path="./data")
vist_dataset = VistDataset(root_path="./data", samples_num=configurations.samples)

invalid_assignment_id = "ASSIGNMENT_ID_NOT_AVAILABLE"


@app.route('/', methods=['GET', 'POST'])
def home():
    render_data = {
        "worker_id": request.args.get("workerId"),
        "assignment_id": request.args.get("assignmentId"),
        "hit_id": request.args.get("hitId")
    }

    if render_data["assignment_id"] != invalid_assignment_id:
        print("Request parameters: {}".format(json.dumps(render_data)))

    questions = []
    for x in range(configurations.number_of_questions):
        story_id = vist_dataset.get_random_story_id()
        question = type('Question', (object,), {})()
        question.id = story_id
        question.count = x + 1
        question.images = []
        image_ids = vist_dataset.get_images_ids(question.id)

        for i in image_ids:
            image = type('Image', (object,), {})()
            image.id = i
            image.content = base64.b64encode(data_loader.load_image(i)).decode('ascii')
            question.images.append(image)

        questions.append(question)

    resp = make_response(render_template("full-hit.html", questions=questions, worker_id=render_data["worker_id"],
                                         assignment_id=render_data["assignment_id"], hit_id=render_data["hit_id"]))

    # resp.headers['x-frame-options'] = 'dummy'
    resp.headers['ContentType'] = "text/html"
    return resp


@app.route('/api/questions/results', methods=['POST'])
def submit_results():
    print("Request parameters: {}".format(request.data))
    return "true"


@app.route('/api/done', methods=['GET'])
def finish_hit():
    resp = make_response(render_template("completed-hit.html"))
    resp.headers['ContentType'] = "text/html"
    return resp

if __name__ == "__main__":
    logHandler.initialize()
    data_loader.initialize()
    vist_dataset.initialize()

    app.run(host='127.0.0.1', port=8080, debug=True)
