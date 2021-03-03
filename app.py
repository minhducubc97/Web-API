from flask import Flask, url_for, request, json, Response, jsonify
from functools import wraps
import csv

app = Flask(__name__)


def make_json_list(csvFilePath):
    data = []
    with open('classics.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append({
                'title': row[3],
                'author': row[11],
                'year': row[13],
                'link': row[8]
            })
    return data


json_list = make_json_list('classics.csv')


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


def check_auth(username, password):
    return username == 'admin' and password == 'secret'


def authenticate():
    message = {
        'message': 'Authenticate'
    }
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'
    return resp


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()
        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@requires_auth
def api_root():
    return 'Welcome to Ebook free resource!'


@app.route('/books')
@requires_auth
def api_articles():
    json_list_string = json.dumps(json_list)
    return Response(json_list_string, status=200, mimetype='application/json')


@app.route('/books/<bookid>', methods=['GET'])
@requires_auth
def api_book(bookid):
    json_item = json_list[int(bookid)]
    json_item_string = json.dumps(json_item)
    return Response(json_item_string, status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
