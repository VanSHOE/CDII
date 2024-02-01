import networkx as nx
import pandas as pd
import csv
import os
import argparse

class GraphConverter:
    def __init__(self, input_paths):
        self.input_paths = input_paths
        self.output_path = None
        self.df = None
        self.vertex_df = None
        self.users = []
        self.comments = []
        self.upvotes = []
        self.comment_edges = []
        self.upvote_edges = []
        self.weighted_edges = []
        self.graph = None
    
    def print_stats(self):
        print(f"Users: {len(self.users)}")
        print(f"Comment Edges: {len(self.comment_edges)}")
        print(f"Upvote Edges: {len(self.upvote_edges)}")
        print(f"Unique Edges: {len(self.weighted_edges)}")
    
    
    def print_users(self):
        for user in self.users:
            print(user)
    
    def print_comments(self):
        for comment in self.comments:
            print(comment)
    def print_upvotes(self):
        for upvote in self.upvotes:
            print(upvote)
    
    def print_comment_edges(self):
        for edge in self.comment_edges:
            print(edge)
    
    def print_upvote_edges(self):
        for edge in self.upvote_edges:
            print(edge)
    
    def print_weighted_edges(self):
        for edge in self.weighted_edges:
            print(edge)
    
    def read_csv(self):
        for path in self.input_paths:
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                # skip the header
                next(reader)
                for row in reader:
                    self.users.append(row['author'])
                    
                    commenters = row['commenters'].strip("][").split(', ')
                    commenters = [x.strip("'") for x in commenters]
                    self.users.extend(commenters)
                    
                    upvoters = row['upvoters'].strip("][").split(', ')
                    upvoters = [x.strip("'") for x in upvoters]
                    self.users.extend(upvoters)
                    
                    self.comments.append({
                        'author': row['author'],
                        'commenters': commenters,
                        "csv": path.split("/")[-1].split(".")[0]
                    })
                    
                    self.upvotes.append({
                        'author': row['author'],
                        'upvoters': upvoters,
                        "csv": path.split("/")[-1].split(".")[0]
                    })
        # give each user a unique id
        self.users = list(set(self.users))
        self.users = {user: i for i, user in enumerate(self.users)}
    
    def set_comment_edges(self):
        for comment in self.comments:
            for commenter in comment['commenters']:
                self.comment_edges.append((self.users[comment['author']], self.users[commenter], comment['csv']))
    
    def set_upvote_edges(self):
        for upvote in self.upvotes:
            for upvoter in upvote['upvoters']:
                self.upvote_edges.append((self.users[upvote['author']], self.users[upvoter], upvote['csv']))
    
    def set_weighted_edges(self):
        for edge in self.comment_edges:
            self.weighted_edges.append([edge[0], edge[1], 1, edge[2]])
        for edge in self.upvote_edges:
            if [edge[0], edge[1], 1, edge[2]] in self.weighted_edges:
                index = self.weighted_edges.index([edge[0], edge[1], 1, edge[2]])
                self.weighted_edges[index][2] += 1
            else:
                self.weighted_edges.append([edge[0], edge[1], 1, edge[2]])
        # get unique edges
        self.weighted_edges = list(set(tuple(x) for x in self.weighted_edges))
        
    def create_dataframes(self):
        # edge dataframe
        self.df = pd.DataFrame(self.weighted_edges, columns=['from', 'to', 'weight', 'label'])
        
        # vertex dataframe
        # use key as label and value as id
        self.vertex_df = pd.DataFrame(list(self.users.items()), columns=['label', 'id'])
        # reverse the columns
        self.vertex_df = self.vertex_df[['id', 'label']]
    
    def create_graph(self):
        self.graph = nx.from_pandas_edgelist(self.df, 'from', 'to', ['weight', 'label'], create_using=nx.DiGraph())
        # check if graph is directed
        print(nx.is_directed(self.graph))
    
    def run(self, logs=False):
        self.read_csv()
        self.set_comment_edges()
        self.set_upvote_edges()
        self.set_weighted_edges()
        self.create_dataframes()
        self.create_graph()
        if(logs):
            self.print_stats()
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts Quora data to a graph')

    parser.add_argument('-i','--input', dest='input', type=str, help='Input folder path')
    parser.add_argument('-o','--output', dest='output', type=str, help='Output file directory')
    parser.add_argument('-n','--name', dest='name', type=str, help='Output file name')

    args = parser.parse_args()
    
    if args.input is None:
        print("Input folder path is required")
        exit(1)
    
    if args.output is None:
        print("Output folder path is required")
        exit(1)
    
    input_paths = []
    
    if args.input.endswith(".csv"):
        input_paths = [args.input]
    
    #  get paths of all csv files in input folder
    for root, dirs, files in os.walk(args.input):
        for file in files:
            if file.endswith(".csv"):
                input_paths.append(os.path.join(root, file))
    
    if len(input_paths) == 0:
        print("No valid input paths found")
        exit(1)
    
    gc = GraphConverter(input_paths)
    gc.run(logs=True)
    
    # save graphml file to output path
    nx.write_graphml(gc.graph, args.output + '/' + args.name + ".graphml")