import argparse
from xml.etree.ElementTree import ElementTree
import json
import os
import networkx as nx

parser = argparse.ArgumentParser(description="Convert GraphML file to JSON")
parser.add_argument("filename", metavar="filename", type=str, help="File to convert from GraphML to JSON")

args = parser.parse_args()

def load_graph(filename):
    G = nx.read_graphml(filename)
    return G

def graph_to_json(G):
    nodes = []
    for node in G.nodes(data=True):
        print(node)
        id = node[0]
        group = node[1]['group'] if 'group' in node[1] else 0
        location = node[1]['location'] if 'location' in node[1] else ""
        is_influencer = node[1]['influencer'] if 'influencer' in node[1] else False
        nodes.append({
            "id": id,
            "group": group,
            "location": location,
            "is_influencer": is_influencer
        })
    
    links = []
    for link in G.edges(data=True):
        links.append({
            "source": link[0],
            "target": link[1],
            "weight": link[2].get("weight", 1)
        })
    
    return {
        "nodes": nodes,
        "links": links
    }

def save_json(graph_json, filename):
    outfilename = filename.split("/")[-1].replace(".graphml", ".json")
    outfolder = './json'
    
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    
    with open(os.path.join(outfolder, outfilename), "w") as f:
        json.dump(graph_json, f, indent=4)

if __name__ == "__main__":
    save_json(graph_to_json(load_graph(args.filename)), args.filename)