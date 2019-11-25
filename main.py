import json
import random
import uuid

from flask import Flask, render_template, make_response, jsonify, request, send_from_directory

import configurations
from dataLoader import DataLoader
from hitCounter import HitCounter

from vistDataset import VistDataset
import base64
import time

app = Flask(__name__)
data_loader = DataLoader(root_path=configurations.root_data)
hit_counter = HitCounter(root_path=configurations.root_data, story_max_hits=configurations.max_story_submit)
vist_dataset = VistDataset(root_path=configurations.root_data, hit_counter=hit_counter, samples_num=configurations.samples)


@app.route('/.well-known/acme-challenge/<path:filename>', methods=['GET', 'POST'])
def serve_static_files(filename):
    print("Requested static file: {}".format(filename))
    return send_from_directory('./static/.well-known/acme-challenge/', filename)


@app.route('/', methods=['GET', 'POST'])
def home():
    render_data = {
        "worker_id": request.args.get("workerId"),
        "assignment_id": request.args.get("assignmentId"),
        "hit_id": request.args.get("hitId")
    }

    print("Request parameters: {}".format(json.dumps(render_data)))

    questions = generate_questions()

    resp = make_response(render_template("full-hit.html", questions=questions, worker_id=render_data["worker_id"],
                                         assignment_id=render_data["assignment_id"], hit_id=render_data["hit_id"],
                                         user_input=configurations.get_user_description,
                                         story_description=configurations.show_original_description))

    resp.headers['ContentType'] = "text/html"
    return resp


def generate_questions():
    questions = []
    story_ids = vist_dataset.get_random_story_ids(configurations.number_of_questions, configurations.story_ids)
    # In order to validate user's answers we want one of the question to be a duplicate
    story_ids.append(story_ids[0])
    question_count = 1
    for story_id in story_ids:
        question = type('Question', (object,), {})()
        question.id = story_id
        question.uuid = generate_uui()
        question.count = question_count

        if configurations.show_original_description:
            question.description = vist_dataset.get_story_description(story_id)

        question_count += 1
        question.images = []
        image_ids = vist_dataset.get_images_ids(question.id)
        random.shuffle(image_ids)

        image_count = 1
        for i in image_ids:
            image = type('Image', (object,), {})()
            image.id = i
            image.uuid = generate_uui()
            image.count = image_count
            image_count += 1
            image_data = data_loader.load_image(i)
            image.content = base64.b64encode(image_data).decode('ascii')
            question.images.append(image)

        questions.append(question)

    questions.append(create_test_question(configurations.test_sequence["id"], question_count,
                                          configurations.test_sequence["image_ids"], story_ids))

    if configurations.use_obvious_stories:
        for s in configurations.obvious_sequences:
            question_count += 1
            questions.append(create_test_question(s["id"], question_count, s["image_ids"], story_ids))

    return questions


@app.route('/api/questions/results', methods=['POST'])
def submit_results():
    print("Request parameters: {}".format(request.data))
    result = json.loads(request.data.decode('utf8'))
    if result["assignment_id"] == configurations.invalid_assignment_id:
        return "true"

    for q in result["question_ids"]:
        hit_counter.add_counter(q)
    return "true"


@app.route('/api/done', methods=['GET'])
def finish_hit():
    resp = make_response(render_template("completed-hit.html"))
    resp.headers['ContentType'] = "text/html"
    return resp


def generate_uui():
    return str(uuid.uuid4())


def create_test_question(question_id, question_count, image_ids, story_ids):
    question = type('Question', (object,), {})()
    question.id = question_id
    story_ids.append(question.id)
    question.uuid = generate_uui()
    question.count = question_count
    question.images = []
    image_count = 1
    random.shuffle(image_ids)
    for i in image_ids:
        image = type('Image', (object,), {})()
        image.id = i
        image.uuid = generate_uui()
        image.count = image_count
        image_count += 1
        image.content = base64.b64encode(data_loader.load_image(i)).decode('ascii')
        question.images.append(image)

    return question


def _print_log(start_time, log_message, worker_id):
    w = worker_id
    if w is None:
        w = "null"
    print("[worker_id:" + w + "][time:" + str(time.time() - start_time) + "]", log_message)
    return time.time()


if __name__ == "__main__":
    if configurations.private_key_path is not None \
            and configurations.private_key_path is not "" \
            and configurations.certificate_path is not None \
            and configurations.certificate_path is not "":
        app.run(host='0.0.0.0', port=443, debug=True, ssl_context=(configurations.certificate_path, configurations.private_key_path))
    else:
        app.run(host='0.0.0.0', port=80, debug=False)
