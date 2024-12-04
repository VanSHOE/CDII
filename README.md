Report: https://docs.google.com/document/d/1w1wlUfuWsaMwC-qyb4If8MQqxr3oeljf2KNLuUFUArE/edit?usp=sharing

## graphConverter.py
```
usage: graphConverter.py [-h] [-i INPUT] [-o OUTPUT] [-t TYPE] [-n NAME]

Converts Quora or ShareChat data to a graph

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input folder path for Quora or Input .json file path for ShareChat
  -o OUTPUT, --output OUTPUT
                        Output folder path
  -t TYPE, --type TYPE  quora[Q] or sharechat[S]
  -n NAME, --name NAME  Output file name
```

## graphActions.py
```
usage: graphActions.py [-h] [-i INPUT] [-o OUTPUT] [-c] [-r RESOLUTION] [-in]

Perform community detection or influence detection on a graph

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input graph path
  -o OUTPUT, --output OUTPUT
                        Output graph path
  -c, --communities     Perform community detection
  -r RESOLUTION, --resolution RESOLUTION
                        [OPTIONAL] Resolution for community detection, default=1.0
  -in, --influencers    Perform influencer identification
``` 
