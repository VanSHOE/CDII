
import networkx as nx
import pandas as pd
import csv
import os
import argparse
import sys

class GraphConverter:
    def __init__(self, input_paths):
        self.input_paths = input_paths
        self.output_path = None
        self.df = None
        self.users = []
        self.followers = []
        self.following = []
        self.edges = []
        self.graph = None
        
        csv.field_size_limit(sys.maxsize)

    
    def print_stats(self):
        print(f"Users: {len(self.users)}")
        print(f"Edges: {len(self.edges)}")
    
    
    def print_users(self):
        for user in self.users:
            print(user)
    
    def print_followers(self):
        for follower in self.followers:
            print(follower)
    
    def print_following(self):
        for following in self.following:
            print(following)
    
    def read_csv(self):
        for path in self.input_paths:
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                # get the header
                next(reader)
                for row in reader:
                    self.users.append(row['user'])
                    
                    followers = row['followers'].strip("][").split(', ')
                    followers = [x.strip("'") for x in followers]
                    self.users.extend(followers)
                    
                    following = row['following'].strip("][").split(', ')
                    following = [x.strip("'") for x in following]
                    self.users.extend(following)
                    
                    self.followers.append({
                        'user': row['user'],
                        'followers': followers,
                    })
                    
                    self.following.append({
                        'user': row['user'],
                        'following': following,
                    })
        # give each user a unique id
        self.users = list(set(self.users))
        self.users = {user: i for i, user in enumerate(self.users)}
    
    def set_edges(self):
        for row in self.followers:
            for follower in row['followers']:
                self.edges.append((self.users[follower], self.users[row['user']]))
        
        for row in self.following:
            for following in row['following']:
                self.edges.append((self.users[row['user']], self.users[following]))
        
    def create_dataframes(self):
        # edge dataframe
        self.df = pd.DataFrame(self.edges, columns=['from', 'to'])
    
    def create_graph(self):
        self.graph = nx.from_pandas_edgelist(self.df, 'from', 'to', create_using=nx.DiGraph())
        # check if graph is directed
        print(nx.is_directed(self.graph))
    
    def run(self, logs=False):
        self.read_csv()
        self.set_edges()
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