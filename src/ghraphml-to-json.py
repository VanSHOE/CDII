import argparse
from xml.etree.ElementTree import ElementTree
import json

parser = argparse.ArgumentParser(description="Convert GraphML file to JSON")
parser.add_argument("--static", action="store_true", default=False, required=False, help="Specify whether you would to include static properties from source file")


parser.add_argument("filename", metavar="filename", type=str, help="File to convert from GraphML to JSON")

args = parser.parse_args()

tree = ElementTree()
tree.parse(open(args.filename, "r"))

# tree.find("{http://graphml.graphdrawing.org/xmlns}graph/{http://graphml.graphdrawing.org/xmlns}node")

graphml = {
	"graph": "{http://graphml.graphdrawing.org/xmlns}graph",
	"node": "{http://graphml.graphdrawing.org/xmlns}node",
	"edge": "{http://graphml.graphdrawing.org/xmlns}edge",
	"data": "{http://graphml.graphdrawing.org/xmlns}data",
	"label": "{http://graphml.graphdrawing.org/xmlns}data[@key='label']",
	"x": "{http://graphml.graphdrawing.org/xmlns}data[@key='x']",
	"y": "{http://graphml.graphdrawing.org/xmlns}data[@key='y']",
	"size": "{http://graphml.graphdrawing.org/xmlns}data[@key='size']",
	"r": "{http://graphml.graphdrawing.org/xmlns}data[@key='r']",
	"g": "{http://graphml.graphdrawing.org/xmlns}data[@key='g']",
	"b": "{http://graphml.graphdrawing.org/xmlns}data[@key='b']",
	"weight": "{http://graphml.graphdrawing.org/xmlns}data[@key='weight']",
	"edgeid": "{http://graphml.graphdrawing.org/xmlns}data[@key='edgeid']",
}

# print dir(graphml)
graph = tree.find(graphml.get("graph"))
nodes = graph.findall(graphml.get("node"))
edges = graph.findall(graphml.get("edge"))

out = {"nodes":[], "edges":[]}

print("Nodes: ", len(nodes))
print("Edges: ", len(edges))
for node in nodes[:]:
    node_id = node.get("id")
    # print elements within node
    data = node.findall(graphml.get("data"))
    group_id = data[0].text
    out["nodes"].append({"id": node_id, "group": group_id, "label": node_id})

count = 0
for edge in edges[:]:
    edgeid = count
    count += 1
    data = edge.findall(graphml.get("data"))
    weight = data[0].text
    group = data[1].text
    out["edges"].append(
        {
            "source": edge.get("source"),
            "target": edge.get("target"),
            "id": edgeid,
            "weight": weight,
            "group": group
        })
outfilename = args.filename.split(".")[-2] + ".json" if len(args.filename.split(".")) >= 2 else args.filename + ".json"
open(outfilename, "w").write(json.dumps(out))