python3 graphConverter.py -i uploads/$1 -o uploads -t S -n $2
python3 graphActions.py -i uploads/$2.graphml -o uploads/$2.graphml -c -in -a $3 -ia $4 -iap $5
python3 src/graphml-to-json.py uploads/$2.graphml