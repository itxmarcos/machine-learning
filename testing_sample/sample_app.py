from flask import Flask, request, Response, json

# Creating Flask application
app = Flask(__name__)

# Helper class for JSON-based response
class JsonResponse(Response):
    def __init__(self, json_dict, status=200):
        super().__init__(response=json.dumps(json_dict), status=status, mimetype="application/json")

# Defining GET and POST endpoints
@app.route('/')
def hello_world():
    return 'Hello, World!'

# The purpose of this endpoint is to return a doubled value
@app.route('/add', methods=['POST'])
def add():
    json = request.json
    return JsonResponse(json_dict={"answer": json['key'] * 2}, status=200)

# Main section that prints help message. (Alternative launching procedure can be applied)
if __name__ == '__main__':
    script_name = __file__
    print("run:\n"
          "FLASK_APP={} python -m flask run --port 8000 --host 0.0.0.0".format(script_name))
    exit(1)