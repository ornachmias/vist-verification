import json
import os
import random
import uuid
from pathlib import Path

from flask import Flask, render_template, make_response, jsonify, request, send_from_directory

import configurations
from analyzeResults import AnalyzeResults
from dataLoader import DataLoader
from hitCounter import HitCounter
import numpy as np

from vistDataset import VistDataset
import base64
import time

app = Flask(__name__)
data_loader = DataLoader(root_path=configurations.root_data)
hit_counter = HitCounter(root_path=configurations.root_data, story_max_hits=configurations.max_story_submit)
vist_dataset = VistDataset(root_path=configurations.root_data, hit_counter=hit_counter, samples_num=configurations.samples)
analyze_results = AnalyzeResults(data_root=configurations.root_data, data_loader=data_loader, vist_dataset=vist_dataset)


@app.route('/api/images/<image_id>', methods=['GET'])
def serve_image(image_id):
    print("Requested image file: {}".format(image_id))
    image_path = data_loader._find_file(image_id)
    if image_path is None:
        return 'Image not found!'
    
    image_file_name = os.path.basename(image_path)
    path = Path(image_path)
    return send_from_directory(path.parent, image_file_name)


@app.route('/api/stories/<story_id>', methods=['GET'])
def get_image_ids(story_id):
    return json.dumps(vist_dataset.get_images_ids(story_id))


@app.route('/api/stories', methods=['POST'])
def submit_story_result():
    data = request.form.to_dict(flat=False)
    story_id = data['story_id'][0]
    img_ids = data['img_ids']
    captions = data['captions']
    features = data['features']
    print("Called save result for story id: {} image ids: {} with captions: {}".format(story_id, img_ids, captions))
    data_loader.save_story_result(story_id, img_ids, captions, features)
    return 'OK'


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
            if image_data is not None:
                image.content = base64.b64encode(image_data).decode('ascii')
            question.images.append(image)

        questions.append(question)

    questions.append(create_test_question(configurations.test_sequence["id"], question_count,
                                          configurations.test_sequence["image_ids"], story_ids, configurations.test_sequence["story"]))

    if configurations.use_obvious_stories:
        for s in configurations.obvious_sequences:
            question_count += 1
            questions.append(create_test_question(s["id"], question_count, s["image_ids"], story_ids, s["story"]))

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


@app.route('/manage/sequences', methods=['GET'])
def get_sequences():
    sequences_ids_str = request.args.get("search")
    resp = make_response(render_template("display-sequences.html"))
    resp.headers['ContentType'] = "text/html"

    if sequences_ids_str is None or sequences_ids_str == "":
        return resp

    sequences_ids = sequences_ids_str.split(",")

    if len(sequences_ids_str) < 1:
        return resp

    questions = []
    for story_id in sequences_ids:
        story_id = story_id.strip()
        question = type('Question', (object,), {})()
        question.id = story_id
        question.uuid = generate_uui()
        question.description = vist_dataset.get_story_description(story_id)

        question.images = []
        image_ids = vist_dataset.get_images_ids(question.id)

        for i in image_ids:
            image = type('Image', (object,), {})()
            image.id = i
            image.uuid = generate_uui()
            image_data = data_loader.load_image(i)
            if image_data is not None:
                image.content = base64.b64encode(image_data).decode('ascii')
            question.images.append(image)

        questions.append(question)

    resp = make_response(render_template("display-sequences.html", questions=questions))
    resp.headers['ContentType'] = "text/html"
    return resp


@app.route('/manage/results', methods=['GET'])
def get_results():
    result_ids = analyze_results.get_results_ids()
    result_id = request.args.get("result_id")
    resp = make_response(render_template("display-results.html", result_ids=result_ids))
    resp.headers['ContentType'] = "text/html"

    if result_id is None:
        return resp

    test_path, general_paths, hists = analyze_results.analyze(result_id)
    graphs = []

    if test_path is not None:
        general_paths.append(test_path)

    for g in general_paths:
        if not os.path.exists(g):
            continue

        in_file = open(g, "rb")
        data = in_file.read()
        in_file.close()
        graphs.append(base64.b64encode(data).decode('ascii'))

    hists_images = []
    for k in hists:
        if not os.path.exists(hists[k]["fig_path"]):
            continue

        in_file = open(hists[k]["fig_path"], "rb")
        data = in_file.read()
        in_file.close()
        hists_images.append([k, base64.b64encode(data).decode('ascii')])

    resp = make_response(render_template("display-results.html", result_ids=result_ids, graphs=graphs, hists=hists_images, result_id=result_id))
    resp.headers['ContentType'] = "text/html"
    return resp


@app.route('/manage/results/<question_id>', methods=['GET'])
def get_hist(question_id):
    result_id = request.args.get("result_id")
    hist = analyze_results.get_histogram(result_id, question_id)
    values = np.asarray(hist["values"])
    v_i = np.argsort(np.multiply(-1, values))
    values = values[v_i]
    labels = np.asarray(hist["labels"])[v_i]
    fig_path = hist["fig_path"]

    in_file = open(fig_path, "rb")
    data = in_file.read()
    in_file.close()
    fig_data = base64.b64encode(data).decode('ascii')

    sequences = []
    for i in range(len(values)):
        sequence = type('Sequence', (object,), {})()
        sequence.result_count = values[i]
        sequence.image_order = labels[i]
        sequence.images = []

        for image_id in labels[i]:
            image = type('Image', (object,), {})()
            image.id = image_id
            image_data = data_loader.load_image(image_id)
            if image_data is not None:
                image.content = base64.b64encode(image_data).decode('ascii')

            sequence.images.append(image)

        sequences.append(sequence)

    t = None
    for x in configurations.obvious_sequences:
        if x["id"] == question_id:
            t = x["story"]

    if question_id == configurations.test_sequence["id"]:
        t = configurations.test_sequence["story"]

    if t is None:
        t = vist_dataset.get_story_description(question_id)

    resp = make_response(
        render_template("display-histogram.html", fig_data=fig_data, sequences=sequences, question_id=question_id, story_text=t))
    resp.headers['ContentType'] = "text/html"
    return resp


def generate_uui():
    return str(uuid.uuid4())


def create_test_question(question_id, question_count, image_ids, story_ids, story):
    question = type('Question', (object,), {})()
    question.id = question_id
    story_ids.append(question.id)
    question.uuid = generate_uui()

    if configurations.show_original_description:
        question.description = story

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
