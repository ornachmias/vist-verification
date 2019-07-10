from flask import render_template, make_response, jsonify, request
import connexion
import logHandler
from dataLoader import DataLoader
from databaseAccess import DatabaseAccess
from vistDataset import VistDataset
import base64

app = connexion.App(__name__, specification_dir="./")

@app.route("/")
def home():
    return render_template("single-question.html")


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
    data_loader = DataLoader(root_path="../data")
    vist_dataset = VistDataset(root_path="../data")
    database_access = DatabaseAccess(scripts_root="../mysql")

    data_loader.initialize()
    vist_dataset.initialize()
    database_access.initialize(vist_dataset)
    app.run(debug=True)