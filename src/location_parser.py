import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from tqdm import tqdm
from geopy.geocoders import Nominatim
from time import sleep

class LocationParser:
    def __init__(self, input_paths):
        self.input_paths = input_paths
        self.output_path = None
        self.user_bios = {}
        self.user_locations = {}
        self.geolocator = Nominatim(user_agent="aegeofi")
        self.indian_states_and_union_territories = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
            'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
            'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
            'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'New Delhi',
            'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli','Daman and Diu',
            'Lakshadweep', 'Delhi', 'Puducherry'
        ]
        
        self.state_dict = {state: 0 for state in self.indian_states_and_union_territories}
        
        self.unidentified_locations = {}
    
    def extract_location(self):
        for path in self.input_paths:
            with open(path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    bio_text = row['creds']
                    bio_text = bio_text.split('|')
                    for text in bio_text:
                        if 'Lives in' in text:
                            self.user_locations[row['profile_link']] = text.split('Lives in ')[1]
                            # check if it is alphanumeric
                            if not self.user_locations[row['profile_link']].isalpha():
                                # find the index of the first non-alphabet character
                                idx = 0
                                for i in range(len(self.user_locations[row['profile_link']])):
                                    if not self.user_locations[row['profile_link']][i].isalpha():
                                        idx = i
                                        break
                                # split the string at the index
                                self.user_locations[row['profile_link']] = self.user_locations[row['profile_link']][:idx]
                            break
    
    def get_unidentified_locations(self):
        for user, loc in self.user_locations.items():
            lis = loc.split(', ')
            if len(lis) > 1:
                state = lis[1]
                if state in self.state_dict:
                    self.user_locations[user] = state
                    self.state_dict[state] += 1
                else:
                    print(">>",state)
                    self.unidentified_locations[user] = loc
            elif loc in self.state_dict:
                self.user_locations[user] = loc
                self.state_dict[loc] += 1
            else:
                print(">>",loc)
                self.unidentified_locations[user] = loc
    
    def get_state(self, loc):
    # Using try-except to handle potential exceptions
        try:
            # Getting the location information for the given city
            location = self.geolocator.geocode(loc, timeout=5)
            print(location.raw['display_name'])
            # check if location is in India
            if location.raw['display_name'].split(', ')[-1] != 'India':
                return None
            if location:
                return location.raw['display_name']
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def check_state(self, str):
        for state in self.indian_states_and_union_territories:
            if state in str:
                return state
        else:
            return None
    
    def geolocate(self):
        for user, loc in tqdm(self.unidentified_locations.items()):
            location = self.get_state(loc)
            if location is None:
                print("location not found for >>",loc)
                self.user_locations[user] = None
                continue
            state = self.check_state(location)
            if state:
                if state in self.state_dict:
                    print(state)
                    self.user_locations[user] = state
                    self.state_dict[state] += 1
                else:
                    print(">>",state)
            else:
                print("state not found for >>",loc)
                self.user_locations[user] = None
            sleep(3)
    
    def run(self):
        self.extract_location()
        self.get_unidentified_locations()
        self.geolocate()
    
    def query(self, user):
        try:
            return self.user_locations[user]
        except KeyError:
            return None

if __name__ == '__main__':
    paths = ['user_data/bjp.csv']
    parser = LocationParser(paths)
    parser.extract_location()
    print(parser.user_locations)
    parser.get_unidentified_locations()
    parser.geolocate()
    print(parser.user_locations)