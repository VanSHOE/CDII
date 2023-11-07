import networkx as nx
import argparse

class Graph():
    def __init__(self, path):
        self.path = path
        self.graph = None
        self.communities = None
        self.influencers = None
        
    def get_graph(self):
        self.graph = nx.read_graphml(self.path)

    def assign_communities(self):
        community_dict = {}
        for i, community in enumerate(self.communities):
            for node in community:
                community_dict[node] = i
        # assign the community as the attribute in the graph
        nx.set_node_attributes(self.graph, community_dict, "group")
        nx.set_node_attributes(self.graph, community_dict, "label")

    def detect_communities(self, resolution=1.0):
        self.communities = nx.community.louvain_communities(self.graph, resolution=resolution, weight='weight')
        self.assign_communities()
    
    def assign_influencers(self):
        self.influencers = nx.voterank(self.graph)
        # influencers is a list of node ids in descending order of influence
        # assign an attribute to each node in the graph to indicate if it is an influencer
        nx.set_node_attributes(self.graph, {node: False for node in self.graph.nodes}, "influencer")
        for influencer in self.influencers:
            self.graph.nodes[influencer]["influencer"] = True
    
    def export(self, path):
        nx.write_graphml(self.graph, path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform community detection or influence detection on a graph')
    
    parser.add_argument('-i','--input', dest='input', type=str, help='Input graph path')
    parser.add_argument('-o','--output', dest='output', type=str, help='Output graph path')
    parser.add_argument('-c','--communities', dest='communities', action='store_true', help='Perform community detection')
    parser.add_argument('-r','--resolution', dest='resolution', type=float, help='[OPTIONAL] Resolution for community detection, default=1.0')
    parser.add_argument('-in','--influencers', dest='influencers', action='store_true', help='Perform influencer identification')
    
    args = parser.parse_args()
    
    if args.input is None:
        print("Input graph path is required")
        exit(1)
    
    graph = Graph(args.input)
    graph.get_graph()
    
    if args.communities:
        if args.resolution is None:
            graph.detect_communities()
        else:
            graph.detect_communities(resolution=args.resolution)
    elif args.influencers:
        graph.assign_influencers()
    graph.export(args.output)