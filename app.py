from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_cors import CORS, cross_origin
import os
import json

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/')
@cross_origin(supports_credentials=True)
def index():
    return "Index Page"

@app.route('/upload', methods=['POST'])
@cross_origin(supports_credentials=True, origins='*')
def upload():
    if request.method != 'POST':
        return 'Invalid request'
        
    f = request.files['file']
    f.save(f'uploads/{f.filename}')
    return 'file uploaded successfully'

@app.route('/convert', methods=['POST'])
@cross_origin(supports_credentials=True, origins='*')
def convert_graph():
    if request.method != 'POST':
        return 'Invalid request'

    fname = request.json['fname']
    type = 'QP'
    # run graph converter
    os.system(f'python graphConverter.py -i uploads/{fname} -o uploads/ -t {type} -n {fname.split(".")[0]}')
    # delete file from uploads
    os.remove(f'uploads/{fname}')
    
    # return file name as json
    return {'fname': f'{fname.split(".")[0]}.graphml'}

@app.route('/community', methods=['POST'])
@cross_origin(supports_credentials=True)
def community_detection():
    if request.method != 'POST':
        return 'Invalid request'

    fname = request.json['fname']
    try:
        algo = request.json['algo']
    except:
        algo = 'louvain'
    
    # run community detection
    os.system(f'python graphActions.py -i uploads/{fname} -o uploads/{fname} -c -a {algo}')
    os.system(f'python3 src/ghraphml-to-json.py uploads/{fname}')
    return 'community detection completed'

@app.route('/influencers', methods=['POST'])
@cross_origin(supports_credentials=True)
def influencer_identification():
    if request.method != 'POST':
        return 'Invalid request'

    fname = request.json['fname']
    # run influencer identification
    os.system(f'python graphActions.py -i uploads/{fname} -o uploads/{fname} -in')
    return 'influencer identification completed'

@app.route('/export', methods=['GET'])
@cross_origin(supports_credentials=True)
def export():
    if request.method != 'GET':
        return 'Invalid request'

    fname = request.args.get('fname')
    
    # change extension to json 
    fname = f'{fname.split(".")[0]}.json'
    # send the json content of file back as json
    
    f = open(f'json/{fname}', 'r')
    content = json.load(f)
    f.close()
    
    return content

@app.route('/tojson', methods=['POST'])
@cross_origin(supports_credentials=True)
def to_json():
    if request.method != 'POST':
        return 'Invalid request'

    fname = request.json['fname']
    # run graphml-to-json
    os.system(f'python3 src/graphml-to-json.py uploads/{fname}')
    return 'converted to json'

@app.route('/list', methods=['GET'])
@cross_origin(supports_credentials=True)
def list_files():
    if request.method != 'GET':
        return 'Invalid request'

    # list the names of all available files in json folder
    files = os.listdir('json')
    return {'files': files}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)