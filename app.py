from flask import Flask, url_for, request, json, Response, jsonify
from functools import wraps
import csv

app = Flask(__name__)


def make_json_list(csvFilePath):
    data = []
    with open('classics.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0:
                data.append({
                    'title': row[0],
                    'author': row[2],
                    'year': row[3],
                    'link': row[1]
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
def api_root():
    return 'Welcome to Ebook free resource!'


@app.route('/books', methods=['GET'])
def api_getall():
    json_list_string = json.dumps(json_list)
    return Response(json_list_string, status=200, mimetype='application/json')


@app.route('/books', methods=['POST'])
@requires_auth
def api_post():
    if request.headers['Content-Type'] == 'application/json':
        json_request = request.json
        row = [json_request['title'], json_request['link'],
               json_request['author'], json_request['year']]
        with open('classics.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
            json_list.append(json_request)
            return "Row added to database"
    else:
        return 'Error 415: Unsupported media type'


@app.route('/books/<bookid>', methods=['PUT'])
@requires_auth
def api_put(bookid):
    bookid = int(bookid)
    if (bookid >= len(json_list) or bookid < 0):
        return 'Error 404: Book not found'
    else:
        json_request = request.json
        # prevent missing properties
        if 'title' not in json_request:
            json_request['title'] = ''
        if 'link' not in json_request:
            json_request['link'] = ''
        if 'author' not in json_request:
            json_request['author'] = ''
        if 'year' not in json_request:
            json_request['year'] = ''
        with open('classics.csv', newline='') as f:
            read_data = [row for row in csv.DictReader(f)]
            json_list[bookid] = json_request
        return 'Row updated'


@app.route('/books/<bookid>', methods=['GET'])
def api_getbook(bookid):
    json_item = json_list[int(bookid)]
    json_item_string = json.dumps(json_item)
    return Response(json_item_string, status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
