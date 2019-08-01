import json
import logging

from flask import Flask, render_template, make_response, jsonify, request
import logHandler
from dataLoader import DataLoader
from databaseAccess import DatabaseAccess
from vistDataset import VistDataset
import base64

app = Flask(__name__)
data_loader = DataLoader(root_path="./data")
vist_dataset = VistDataset(root_path="./data")
database_access = DatabaseAccess(scripts_root="./mysql")



@app.route('/', methods=['GET', 'POST'])
def home():
    render_data = {
        "worker_id": request.args.get("workerId"),
        "assignment_id": request.args.get("assignmentId"),
        "amazon_host": "https://workersandbox.mturk.com/mturk/externalSubmit",
        "hit_id": request.args.get("hitId"),
        "some_info_to_pass": request.args.get("someInfoToPass")
    }

    print("Request parameters: {}".format(json.dumps(render_data)))

    resp = make_response(render_template("single-question.html"))
    resp.headers['x-frame-options'] = 'dummy'
    resp.headers['ContentType'] = "text/html"
    return resp


@app.route('/api/questions/<string:question_id>', methods=['GET'])
def get_images_ids(question_id):
    return jsonify(["180526609", "180526610", "181482729", "181602777", "181603598"])


@app.route('/api/questions', methods=['POST'])
def create_new_question():
    return "question-id-1"


@app.route('/api/questions/<string:question_id>', methods=['POST'])
def submit_order(question_id):
    print(request.get_json());
    return "{} successfully submitted.".format(question_id), 200


@app.route('/api/images/<string:image_id>', methods=['GET'])
def get_image(image_id):
    return base64.b64encode(data_loader.load_image(image_id))


if __name__ == "__main__":
    logHandler.initialize()
    data_loader.initialize()
    vist_dataset.initialize()
    database_access.initialize(vist_dataset)

    app.run(host='127.0.0.1', port=8080, debug=True)