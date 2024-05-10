import networkx as nx
import argparse
import time
import igraph as ig

class Graph():
    def __init__(self, path):
        self.path = path
        self.graph = None
        self.meta_graph = None
        self.communities = None
        self.influencers = None
        self.cd_algo = {
            'louvain': nx.community.louvain_communities,
            'lpa': nx.community.label_propagation_communities,
            'greedy_modularity': nx.community.greedy_modularity_communities,
            'asyn_lpa': nx.community.asyn_lpa_communities,
        }
            
        
    def get_graph(self):
        self.graph = nx.read_graphml(self.path)
        # if directed, convert to undirected
        if nx.is_directed(self.graph):
            self.graph = self.graph.to_undirected()

    def assign_communities(self):
        community_dict = {}
        for i, community in enumerate(self.communities):
            for node in community:
                community_dict[node] = i
        # assign the community as the attribute in the graph
        nx.set_node_attributes(self.graph, community_dict, "group")
        nx.set_node_attributes(self.graph, community_dict, "label")

    def set_cd_algo(self, algo):
        if algo in self.cd_algo:
            self.cd_algo = self.cd_algo[algo]
        else:
            print("Invalid community detection algorithm")
            exit(1)

    def detect_communities(self, resolution=1.0):
        # if the community detection algorithm is from igraph, convert the graph to igraph
        self.communities = list(self.cd_algo(self.graph))
        self.assign_communities()
    
    def assign_influencers(self):
        self.influencers = nx.voterank(self.graph)
        # influencers is a list of node ids in descending order of influence
        # assign an attribute to each node in the graph to indicate if it is an influencer
        nx.set_node_attributes(self.graph, {node: False for node in self.graph.nodes}, "influencer")
        for influencer in self.influencers:
            self.graph.nodes[influencer]["influencer"] = True
    
    def print_cd_stats(self):
        # show statistics of the community detection algorithm run on the graph
        print("Number of communities: ", len(self.communities))
        print("Modularity: ", nx.community.quality.modularity(self.graph, self.communities))
        print("Coverage, Performance: ", nx.community.quality.partition_quality(self.graph, self.communities))
    
    def create_meta_graph(self):
        # create a new graph with the communities as nodes
        self.meta_graph = nx.Graph()
        for i, community in enumerate(self.communities):
            self.meta_graph.add_node(i)
        
        # set size of nodes in meta graph as the number of nodes in the community
        for node in self.graph.nodes:
            community = self.graph.nodes[node]['group']
            self.meta_graph.nodes[community]['size'] = self.meta_graph.nodes[community].get('size', 0) + 1
        
        # created a weighted graph with the edges as the number of edges between the communities
        for edge in self.graph.edges:
            community1 = self.graph.nodes[edge[0]]['group']
            community2 = self.graph.nodes[edge[1]]['group']
            if community1 != community2:
                if self.meta_graph.has_edge(community1, community2):
                    self.meta_graph[community1][community2]['weight'] += 1
                else:
                    self.meta_graph.add_edge(community1, community2, weight=1)
    
    def export(self, path):
        nx.write_graphml(self.graph, path)
    
    def export_meta(self, path):
        nx.write_graphml(self.meta_graph, path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform community detection or influence detection on a graph')
    
    parser.add_argument('-i','--input', dest='input', type=str, help='Input graph path')
    parser.add_argument('-o','--output', dest='output', type=str, help='Output graph path')
    parser.add_argument('-c','--communities', dest='communities', action='store_true', help='Perform community detection')
    parser.add_argument('-m','--meta', dest='meta', action='store_true', help='Export meta graph')
    parser.add_argument('-r','--resolution', dest='resolution', type=float, help='[OPTIONAL] Resolution for community detection, default=1.0')
    parser.add_argument('-in','--influencers', dest='influencers', action='store_true', help='Perform influencer identification')
    parser.add_argument('-a','--algo', dest='algo', type=str, help='Community detection algorithm [louvain, lpa, greedy_modularity, asyn_lpa]', default='louvain')
    
    args = parser.parse_args()
    
    if args.input is None:
        print("Input graph path is required")
        exit(1)
    
    graph = Graph(args.input)
    graph.get_graph()
    
    if args.resolution is None:
        args.resolution = 1.0
    
    if args.communities:
        print("Running community detection algorithm: ", args.algo)
        graph.set_cd_algo(args.algo)
        print("Starting community detection")
        st = time.time()
        graph.detect_communities(resolution=args.resolution)
        print("Community detection completed in ", time.time()-st, " seconds")
        graph.print_cd_stats()
        if args.meta:
            graph.create_meta_graph()
            if args.output is None:
                graph.export_meta(args.output)
            exit(0)
    if args.influencers:
        graph.assign_influencers()
    if args.output is not None:
        graph.export(args.output)