import json
from flask import Flask, request, jsonify, send_from_directory
from server.search import search, all as all_fellows, all_names_desc, all_years

app = Flask(__name__,
        static_url_path='/',
        static_folder='static',
        template_folder='static')
app.config['JSON_AS_ASCII'] = False

@app.route('/search', methods=['GET'])
def semantic_search():
    text = request.args.get('text')
    year = request.args.get('year')
    n = 25
    try:
        n = int(request.args.get('n'))
    except:
        pass

    if not text:
        fellows = all_fellows()
    else:
        fellows = search(text)

    if year:
        fellows = [f for f in fellows if f['year'] == year]

    return jsonify(fellows[:n])

@app.route('/preloads.js', methods=['GET'])
def get_preloads_js():
    years = f'const TF_YEARS = {json.dumps(all_years())};'
    names = f'const TF_NAMES_DESC = {json.dumps(all_names_desc())};'
    return '\n'.join([years, names])

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')
