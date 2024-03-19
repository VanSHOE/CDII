import os
import subprocess

dir = './graphs'
files = []
# get all files in the directory
for file in os.listdir(dir):
    if file.endswith(".graphml"):
        files.append(os.path.join(dir, file))

# call graphActions
for file in files:
    subprocess.call(['python3', 'graphActions.py', '-i', file, '-o', file, '-c'])

# call graphml-to-json
for file in files:
    subprocess.call(['python3', 'src/graphml-to-json.py', file, '--static'])