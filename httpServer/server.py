from flask import render_template, make_response, jsonify, request
import connexion


# Create the application instance
app = connexion.App(__name__, specification_dir="./")

# create a URL route in our application for "/"
@app.route("/")
def home():
    """
    This function just responds to the browser URL
    localhost:5000/
    :return:        the rendered template "home.html"
    """
    return render_template("single-question.html")


@app.route('/api/questions/<string:question_id>', methods=['GET'])
def get_images_ids(question_id):
    return jsonify(["a", "b", "c", "d", "e"])


@app.route('/api/questions', methods=['POST'])
def create_new_question():
    return "question-id-1"


@app.route('/api/questions/<string:question_id>', methods=['POST'])
def submit_order(question_id):
    print(request.get_json());
    return "{} successfully submitted.".format(question_id), 200


@app.route('/api/images/<string:image_id>', methods=['GET'])
def get_image(image_id):
    return bytes(image_id, 'utf8')

if __name__ == "__main__":
    app.run(debug=True)