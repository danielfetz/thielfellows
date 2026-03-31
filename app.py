import json
import os
from flask import Flask, request, jsonify, Response
from server.search import search, all as all_fellows, all_names_desc, all_years

_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
        static_url_path='/',
        static_folder=os.path.join(_dir, 'static'),
        template_folder=os.path.join(_dir, 'static'))
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
    return Response('\n'.join([years, names]), mimetype='application/javascript')


@app.route('/disabled-endpoint', methods=['GET'])
def disabled_endpoint():
    # Legacy bundles may request this endpoint when expanding a fellow card.
    # Return an empty payload instead of 404 so the UI doesn't surface an error.
    return jsonify({})

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')
