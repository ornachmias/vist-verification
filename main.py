import json
import uuid

from flask import Flask, render_template, make_response, jsonify, request

import configurations
from dataLoader import DataLoader

from vistDataset import VistDataset
import base64

app = Flask(__name__)
data_loader = DataLoader(root_path=configurations.root_data)
vist_dataset = VistDataset(root_path=configurations.root_data, samples_num=configurations.samples)
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
    story_ids = vist_dataset.get_random_story_ids(configurations.number_of_questions)

    # In order to validate user's answers we want one of the question to be a duplicate
    story_ids.append(story_ids[0])

    x = 1
    for story_id in story_ids:
        question = type('Question', (object,), {})()
        question.id = story_id
        question.uuid = generate_uui()
        question.count = x

        if configurations.show_original_description:
            question.description = vist_dataset.get_story_description(story_id)

        x += 1
        question.images = []
        image_ids = vist_dataset.get_images_ids(question.id)

        image_count = 1
        for i in image_ids:
            image = type('Image', (object,), {})()
            image.id = i
            image.uuid = generate_uui()
            image.count = image_count
            image_count += 1
            image.content = base64.b64encode(data_loader.load_image(i)).decode('ascii')
            question.images.append(image)

        questions.append(question)

    resp = make_response(render_template("full-hit.html", questions=questions, worker_id=render_data["worker_id"],
                                         assignment_id=render_data["assignment_id"], hit_id=render_data["hit_id"],
                                         user_input=configurations.get_user_description,
                                         story_description=configurations.show_original_description))

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


def generate_uui():
    return str(uuid.uuid4())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
