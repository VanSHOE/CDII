import networkx as nx
import argparse
import time
import igraph as ig


class Graph:
    def __init__(self, path):
        self.path = path
        self.graph = None
        self.meta_graph = None
        self.communities = None
        self.influencers = None
        self.cd_algo = {
            "louvain": nx.community.louvain_communities,
            "lpa": nx.community.label_propagation_communities,
            "greedy_modularity": nx.community.greedy_modularity_communities,
            "asyn_lpa": nx.community.asyn_lpa_communities,
        }
        self.influencer_algo = {
            "voterank": self.voterank_influencers,
            "pagerank": self.pagerank_influencers,
            "betweenness": self.betweenness_influencers,
            "eigenvector": self.eigenvector_influencers,
            "closeness": self.closeness_influencers,
        }
        self.influencer_percentage = (
            0.05  # percentage of influencers to select from the graph
        )

    def set_influencer_percentage(self, percentage):
        self.influencer_percentage = percentage

    def get_graph(self):
        self.graph = nx.read_graphml(self.path)

        if nx.is_directed(self.graph):
            self.graph = self.graph.to_undirected()

    def assign_communities(self):
        community_dict = {}
        for i, community in enumerate(self.communities):
            for node in community:
                community_dict[node] = i

        nx.set_node_attributes(self.graph, community_dict, "group")
        nx.set_node_attributes(self.graph, community_dict, "label")

    def set_cd_algo(self, algo):
        if algo in self.cd_algo:
            self.cd_algo = self.cd_algo[algo]
        else:
            print("Invalid community detection algorithm")
            exit(1)

    def detect_communities(self, resolution=1.0):

        self.communities = list(self.cd_algo(self.graph))
        self.assign_communities()

    def set_influencer_algo(self, algo):
        if algo in self.influencer_algo:
            self.influencer_algo = self.influencer_algo[algo]
        else:
            print("Invalid influencer identification algorithm")
            exit(1)

    def voterank_influencers(self):
        self.influencers = nx.voterank(self.graph)

    def pagerank_influencers(self):
        self.influencers = sorted(
            nx.pagerank(self.graph).items(), key=lambda x: x[1], reverse=True
        )

    def betweenness_influencers(self):
        self.influencers = sorted(
            nx.betweenness_centrality(self.graph).items(),
            key=lambda x: x[1],
            reverse=True,
        )

    def eigenvector_influencers(self):
        self.influencers = sorted(
            nx.eigenvector_centrality(self.graph, max_iter=1000, tol=0.0001).items(),
            key=lambda x: x[1],
            reverse=True,
        )

    def closeness_influencers(self):
        self.influencers = sorted(
            nx.closeness_centrality(self.graph).items(),
            key=lambda x: x[1],
            reverse=True,
        )

    def assign_influencers(self):
        self.influencer_algo()

        if isinstance(self.influencers[0], tuple):
            self.influencers = [node for node, _ in self.influencers]
            # trim the influencers to the required percentage if needed
            if len(self.influencers) > int(
                len(self.influencers) * self.influencer_percentage
            ):
                self.influencers = self.influencers[
                    : int(len(self.influencers) * self.influencer_percentage)
                ]

        nx.set_node_attributes(
            self.graph, {node: False for node in self.graph.nodes}, "influencer"
        )
        for influencer in self.influencers:
            self.graph.nodes[influencer]["influencer"] = True

    def print_cd_stats(self):

        print("Number of communities: ", len(self.communities))
        print(
            "Modularity: ",
            nx.community.quality.modularity(self.graph, self.communities),
        )
        print(
            "Coverage, Performance: ",
            nx.community.quality.partition_quality(self.graph, self.communities),
        )

    def print_influencer_stats(self):
        print("Number of influencers: ", len(self.influencers))
        print("Influencers: ", self.influencers)

    def create_meta_graph(self):

        self.meta_graph = nx.Graph()
        for i, community in enumerate(self.communities):
            self.meta_graph.add_node(i)

        for node in self.graph.nodes:
            community = self.graph.nodes[node]["group"]
            self.meta_graph.nodes[community]["size"] = (
                self.meta_graph.nodes[community].get("size", 0) + 1
            )

        for edge in self.graph.edges:
            community1 = self.graph.nodes[edge[0]]["group"]
            community2 = self.graph.nodes[edge[1]]["group"]
            if community1 != community2:
                if self.meta_graph.has_edge(community1, community2):
                    self.meta_graph[community1][community2]["weight"] += 1
                else:
                    self.meta_graph.add_edge(community1, community2, weight=1)

    def export(self, path):
        nx.write_graphml(self.graph, path)

    def export_meta(self, path):
        nx.write_graphml(self.meta_graph, path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform community detection or influence detection on a graph"
    )

    parser.add_argument(
        "-i", "--input", dest="input", type=str, help="Input graph path"
    )
    parser.add_argument(
        "-o", "--output", dest="output", type=str, help="Output graph path"
    )
    parser.add_argument(
        "-c",
        "--communities",
        dest="communities",
        action="store_true",
        help="Perform community detection",
    )
    parser.add_argument(
        "-m", "--meta", dest="meta", action="store_true", help="Export meta graph"
    )
    parser.add_argument(
        "-r",
        "--resolution",
        dest="resolution",
        type=float,
        help="[OPTIONAL] Resolution for community detection, default=1.0",
    )
    parser.add_argument(
        "-in",
        "--influencers",
        dest="influencers",
        action="store_true",
        help="Perform influencer identification",
    )
    parser.add_argument(
        "-a",
        "--algo",
        dest="algo",
        type=str,
        help="Community detection algorithm [louvain, lpa, greedy_modularity, asyn_lpa]",
        default="louvain",
    )
    parser.add_argument(
        "-ia",
        "--inf_algo",
        dest="inf_algo",
        type=str,
        help="Influencer identification algorithm [voterank, pagerank, betweenness, eigenvector, closeness, katz]",
        default="voterank",
    )
    parser.add_argument(
        "-iap",
        "--inf_algo_percentage",
        dest="inf_algo_percentage",
        type=float,
        help="Percentage of influencers to select from the graph",
        default=0.05,
    )

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
        print("Community detection completed in ", time.time() - st, " seconds")
        graph.print_cd_stats()
        if args.meta:
            graph.create_meta_graph()
            if args.output is not None:
                graph.export_meta(args.output)
            exit(0)
    if args.influencers:
        print("Running influencer identification algorithm: ", args.inf_algo)
        graph.set_influencer_percentage(args.inf_algo_percentage)
        graph.set_influencer_algo(args.inf_algo)
        graph.assign_influencers()
        graph.print_influencer_stats()
    if args.output is not None:
        graph.export(args.output)
