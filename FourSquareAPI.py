import pandas as pd
import requests
from pandas.io.json import json_normalize

class FourSquareAPI():
    def __init__(self, client_id, client_secret, version='20180604', limit=30):
        self.client_id = client_id
        self.client_secret = client_secret
        self.version = version
        self.limit = limit
    

    # function that extracts the category of the venue



    def get_venue_explore(self, latitude, longitude, limit=30):
        url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.\
format(self.client_id, self.client_secret, latitude, longitude, self.version, limit)
        results = requests.get(url).json()
        def get_category_type(row):
            try:
                categories_list = row['categories']
            except:
                categories_list = row['venue.categories']

            if len(categories_list) == 0:
                return None
            else:
                return categories_list[0]['name']
        explored = results['response']['groups'][0]['items']
        dataframe = json_normalize(explored) 
        filtered_columns = ['venue.name', 'venue.categories'] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ['venue.id']
        dataframe_filtered = dataframe.loc[:, filtered_columns]
        dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)
        dataframe_filtered.columns = [col.split('.')[-1] for col in dataframe_filtered.columns]
        return dataframe_filtered
        
    def get_venue_search(self, latitude, longitude, search_query, radius=500):
        url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.\
            format(self.client_id, self.client_secret, latitude, longitude, self.version, search_query, radius, self.limit)
        results = requests.get(url).json()
        venues = results['response']['venues']
        print(venues)
        df = json_normalize(venues)
        def get_category_type(row):
            try:
                categories_list = row['categories']
            except:
                categories_list = row['venue.categories']

            if len(categories_list) == 0:
                return None
            else:
                return categories_list[0]['name']
        # keep only columns that include venue name, and anything that is associated with location
        filtered_columns = ['name', 'categories'] + [col for col in df.columns if col.startswith('location.')] + ['id']
        dataframe_filtered = df.loc[:, filtered_columns]
        # filter the category for each row
        dataframe_filtered['categories'] = dataframe_filtered.apply(get_category_type, axis=1)
        dataframe_filtered['search_q'] = search_query
        # clean column names by keeping only last term
        dataframe_filtered.columns = [column.split('.')[-1] for column in dataframe_filtered.columns]

        return dataframe_filtered
    
    def get_trending_places(self, latitude, longitude):
        url = 'https://api.foursquare.com/v2/venues/trending?client_id={}&client_secret={}&ll={},{}&v={}'.\
        format(self.client_id, self.client_secret, latitude, longitude, self.version)
        results = requests.get(url).json()
        def get_category_type(row):
            try:
                categories_list = row['categories']
            except:
                categories_list = row['venue.categories']

            if len(categories_list) == 0:
                return None
            else:
                return categories_list[0]['name']
        if len(results['response']['venues']) == 0:
            trending_venues_df = 'No trending venues are available at the moment!'
        else:
            trending_venues = results['response']['venues']
            trending_venues_df = json_normalize(trending_venues)
            columns_filtered = ['name', 'categories'] + ['location.distance', 'location.city', 'location.postalCode', 'location.state', 'location.country', 'location.lat', 'location.lng']
            trending_venues_df = trending_venues_df.loc[:, columns_filtered]
            trending_venues_df['categories'] = trending_venues_df.apply(get_category_type, axis=1)
        return trending_venues_df


        