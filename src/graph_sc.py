import networkx as nx
import pandas as pd
import json
import os
import argparse

class GraphConverter:
    def __init__(self, path):
        self.path = path
        self.data_list = []
        self.users = []
        self.likes = []
        self.follow = []
        self.like_edges = []
        self.follow_edges = []
        self.weighted_edges = []
        self.graph = None
    
    def get_data(self):
        # read json file
        with open('./data_sharechat/output.jsonl', 'r') as f:
            temp = f.readlines()
            data = []
            for i in temp:
                data.append(json.loads(i))
        self.data_list = data
    
    def print_stats(self):
        print(f"Users: {len(self.users)}")
        print(f"Like Edges: {len(self.like_edges)}")
        print(f"Follow Edges: {len(self.follow_edges)}")
        print(f"Unique Edges: {len(self.weighted_edges)}")
    
    def print_users(self):
        print(self.users)
    
    def print_likes(self):
        print(self.likes)
    
    def print_follow(self):
        print(self.follow)
    
    def print_weighted_edges(self):
        print(self.weighted_edges)
    
    def get_like_edges(self):
        for edge in self.likes:
            author = edge['author']
            for liker in edge['likes']:
                self.like_edges.append((self.users[liker], self.users[author]))
    
    def get_follow_edges(self):
        for edge in self.follow:
            user = edge['user']
            for follower in edge['followers']:
                self.follow_edges.append((self.users[follower], self.users[user]))
    
    def get_weighted_edges(self):
        # if same edge exists in follow, weight is 2 else 1
        for edge in self.follow_edges:
            if edge in self.like_edges:
                self.weighted_edges.append((edge[0], edge[1], 2))
            else:
                self.weighted_edges.append((edge[0], edge[1], 1))
        # get like edges which are not in follow
        for edge in self.like_edges:
            if edge not in self.follow_edges:
                self.weighted_edges.append((edge[0], edge[1], 1))
    
    def extract_info(self, data):
        # get author
        author = data['author_name']
        self.users.append(author)
        
        # get users who liked the post
        if 'users' not in data:
            return
        like_users = data['users']
        self.users.extend(like_users)
        self.likes.append({
            'author': author,
            'likes': like_users
        })
        
        # from dictionary of followers, get follow edges for every user
        follow_dict = data['followers']
        for user in follow_dict:
            followers = follow_dict[user]
            # remove @
            followers = [follower[1:] for follower in followers]
            self.users.extend(followers)
            
            # add follow edges
            self.follow.append({
                'user': user,
                'followers': followers
            })
    
    def create_dataframe(self):
        # edge dataframe
        self.df = pd.DataFrame(self.weighted_edges, columns=['from', 'to', 'weight'])
    
    def create_graph(self):
        self.graph = nx.from_pandas_edgelist(self.df, 'from', 'to', ['weight'])
    
    def run(self, logs=False):
        self.get_data()
        for data in self.data_list:
            self.extract_info(data)
        # get unique users
        self.users = list(set(self.users))
        self.users = {user: i for i, user in enumerate(self.users)}
        
        self.get_like_edges()
        self.get_follow_edges()
        
        self.get_weighted_edges()
        
        if logs:
            self.print_stats()
        
        self.create_dataframe()
        self.create_graph()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts Quora data to a graph')

    parser.add_argument('-i','--input', dest='input', type=str, help='Input .json file path')
    parser.add_argument('-o','--output', dest='output', type=str, help='Output file directory name')
    parser.add_argument('-n','--name', dest='name', type=str, help='Output file name')

    args = parser.parse_args()
    
    if args.input is None:
        print("Input file path is required")
        exit(1)
    
    if args.output is None:
        print("Output folder path is required")
        exit(1)
    
    if args.name is None:
        print("Output file name is required")
        exit(1)
    
    converter = GraphConverter(args.input)
    converter.run(logs=True)
    
    # save graph
    nx.write_graphml(converter.graph, args.output + '/' + args.name + ".graphml")