from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_cors import CORS, cross_origin
import os
import json
import subprocess

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

@app.route('/uploaduserfile', methods=['POST'])
@cross_origin(supports_credentials=True, origins='*')
def uploadUserFile():
    if request.method != 'POST':
        return 'Invalid request'
        
    f = request.files['file']
    f.save(f'uploads/users/{f.filename}')
    return 'file uploaded successfully'


    

@app.route('/convert', methods=['POST'])
@cross_origin(supports_credentials=True, origins='*')
def convert_graph():
    if request.method != 'POST':
        return 'Invalid request'

    fname = request.json['fname']
    try:
        comm_algo = request.json['comm_algo']
    except:
        comm_algo = 'louvain'
    
    try:
        influencer_algo = request.json['influencer_algo']
    except:
        influencer_algo = 'voterank'
    
    try:
        influencer_percentage = request.json['influencer_percentage']
    except:
        influencer_percentage = 0.05

    # run graph converter as subprocess so that it runs in background
    subprocess.Popen([
        'sh',
        'convert-and-run.sh',
        fname,
        fname.split('.')[0],
        comm_algo,
        influencer_algo,
        str(influencer_percentage)
    ])
    # delete file from uploads
    # os.remove(f'uploads/{fname}')
    
    # return file name as json
    return 'running graph converter'

@app.route('/convertsc', methods=['POST'])
@cross_origin(supports_credentials=True, origins='*')
def convert_graph_sc():
    # sharechat graph conversion
    if request.method != 'POST':
        return 'Invalid request'
    
    fname = request.json['fname']
    try:
        comm_algo = request.json['comm_algo']
    except:
        comm_algo = 'louvain'
    
    try:
        influencer_algo = request.json['influencer_algo']
    except:
        influencer_algo = 'voterank'
    
    try:
        influencer_percentage = request.json['influencer_percentage']
    except:
        influencer_percentage = 0.05

    # run graph converter as subprocess so that it runs in background
    subprocess.Popen([
        'sh',
        'convert-and-run-sc.sh',
        fname,
        fname.split('.')[0],
        comm_algo,
        influencer_algo,
        str(influencer_percentage)
    ])
    # delete file from uploads
    # os.remove(f'uploads/{fname}')
    
    # return file name as json
    return 'running graph converter'
    

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
    app.run(debug=True, host='0.0.0.0', port=5003)