from flask import Flask, url_for, request, json, Response, jsonify
from tempfile import NamedTemporaryFile
from functools import wraps
import csv
import shutil

app = Flask(__name__)
filename = 'data/classics.csv'


def make_json_list(csvFilePath):
    data = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0:
                data.append({
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'year': row[3],
                    'link': row[4]
                })
    return data


json_list = make_json_list(filename)


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
    resp.headers['WWW-Authenticate'] = 'Basic realm="E-book"'
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
    return 'Welcome to Ebook free resource! This library has more than a thousand books available.'


@app.route('/books', methods=['GET'])
def api_getall():
    json_list_string = json.dumps(json_list[1:])
    return Response(json_list_string, status=200, mimetype='application/json')


@app.route('/books/<bookid>', methods=['GET'])
def api_getbook(bookid):
    bookid = int(bookid)
    if (bookid >= len(json_list) or bookid <= 0):
        return 'Error 404: Book not found'
    json_item = json_list[bookid]
    json_item_string = json.dumps(json_item)
    return Response(json_item_string, status=200, mimetype='application/json')


@app.route('/books', methods=['POST'])
@requires_auth
def api_post():
    if request.headers['Content-Type'] == 'application/json':
        json_request = request.json
        if ('title' not in json_request) or ('link' not in json_request) or ('author' not in json_request) or ('year' not in json_request):
            return "Error 400: Missing fields in POST request!"
        row = [len(json_list),
               json_request['title'],
               json_request['author'],
               json_request['year'],
               json_request['link']]
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
            json_list.append(json_request)
            return "Row added to database. Library now has " + str(len(json_list) - 1) + " books."
    return 'Error 415: Unsupported media type'


@app.route('/books/<bookid>', methods=['PUT'])
@requires_auth
def api_put(bookid):
    bookid = int(bookid)
    if (bookid >= len(json_list) or bookid <= 0):
        return 'Error 404: Book not found'
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
    fields = ['id', 'title', 'author', 'year', 'link']
    tmpFile = NamedTemporaryFile(mode='w', delete=False, newline='')
    with open(filename, 'r') as file, tmpFile:
        reader = csv.DictReader(file, fieldnames=fields)
        writer = csv.DictWriter(tmpFile, fieldnames=fields)
        for row in reader:
            if (row['id'] == 'id'):
                writer.writerow(row)
                continue
            if int(row['id']) == bookid:
                row = {
                    'id': bookid,
                    'title': json_request['title'],
                    'author': json_request['author'],
                    'year': json_request['year'],
                    'link': json_request['link']
                }
            writer.writerow(row)
            json_list[bookid] = json_request
    shutil.move(tmpFile.name, filename)
    return 'Row updated'


@app.route('/books/<bookid>', methods=['PATCH'])
@requires_auth
def api_patch(bookid):
    bookid = int(bookid)
    if (bookid >= len(json_list) or bookid <= 0):
        return 'Error 404: Book not found'
    json_request = request.json
    fields = ['id', 'title', 'author', 'year', 'link']
    tmpFile = NamedTemporaryFile(mode='w', delete=False, newline='')
    with open(filename, 'r') as file, tmpFile:
        reader = csv.DictReader(file, fieldnames=fields)
        writer = csv.DictWriter(tmpFile, fieldnames=fields)
        for row in reader:
            if (row['id'] == 'id'):
                writer.writerow(row)
                continue
            if int(row['id']) == bookid:
                if 'title' in json_request:
                    row['title'] = json_request['title']
                if 'author' in json_request:
                    row['author'] = json_request['author']
                if 'year' in json_request:
                    row['year'] = json_request['year']
                if 'link' in json_request:
                    row['link'] = json_request['link']
            writer.writerow(row)
            json_list[bookid] = row
    shutil.move(tmpFile.name, filename)
    return 'Row updated'


@app.route('/books/<bookid>', methods=['DELETE'])
@requires_auth
def api_delete(bookid):
    bookid = int(bookid)
    if (bookid >= len(json_list) or bookid <= 0):
        return 'Error 404: Book not found'
    json_request = request.json
    fields = ['id', 'title', 'author', 'year', 'link']
    tmpFile = NamedTemporaryFile(mode='w', delete=False, newline='')
    with open(filename, 'r') as file, tmpFile:
        reader = csv.DictReader(file, fieldnames=fields)
        writer = csv.DictWriter(tmpFile, fieldnames=fields)
        for row in reader:
            if (row['id'] != 'id' and int(row['id']) == bookid):
                continue
            writer.writerow(row)
        del json_list[bookid]
    shutil.move(tmpFile.name, filename)
    return 'Row deleted'


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
