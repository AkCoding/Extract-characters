from flask import Flask, request , jsonify
from main import emoji
app = Flask(__name__)

@app.route('/', methods =['GET'])
def home():
    if request.method == 'GET':
        resp =  jsonify({"data" : "Connected"})
        resp.status_code = 200
        return resp

@app.route('/uploader', methods =['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        output = emoji(file)
        resp = jsonify({"data": output})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({"Error": "Bed request"})
        resp.status_code = 404
        return resp
if __name__ == '__main__':
    app.run(debug=True)
