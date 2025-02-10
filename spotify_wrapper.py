import subprocess
import sys

def install_requirements():
    print('Installing required packages...')
    print()
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Installed the required packages.")
    except subprocess.CalledProcessError as e:
        print("An error occurred during the installation of the required packages. Please check the requirements.txt file and manually install the packages.")
        sys.exit(1)
        
install_requirements()
print()

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
import re
import glob
import numpy as np
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
CACHE_PATH = ".spotify_cache"

SCOPE = "playlist-read-private playlist-modify-private playlist-modify-public" 

auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    open_browser=True,
    cache_path=CACHE_PATH,
)

sp = spotipy.Spotify(auth_manager=auth_manager)

auth_url = auth_manager.get_authorize_url()
print(f"Please visit this URL to authenticate:\n{auth_url}")

user_id = sp.current_user()['id']
user_id_name_first = user_id[:3]
user_id_name_last = user_id[-3:]
output_dir = f"{user_id_name_first}_{user_id_name_last}_csv_files" ## folder where the .csv files are stored per user

def fetch_all_playlists():
    limit = 50  ## max number playlists to fetch per request
    offset = 0  ## starting point for fetching playlists
    all_playlists = []

    while True:
        playlists = sp.current_user_playlists(limit=limit, offset=offset)
        all_playlists.extend(playlists['items'])
        
        if len(playlists['items']) < limit: 
            break
        
        offset += limit

    return all_playlists 
  
        
def filter_for_eoty_playlists():
    eoty_playlists = [
        playlist for playlist in all_playlists if playlist['name'].startswith('Your Top Songs 20') ## filter for playlists that start with 20
    ]

    if eoty_playlists:
        for playlist in eoty_playlists:
            print(f"Name: {playlist['name']}, ID: {playlist['id']}") ## print list of eoty playlists
    else:
        print("No playlists starting with 'Your Top Songs 20..' were found. Searching in Dutch: 'Jouw topnummers van 20..'")
        eoty_playlists = [
            playlist for playlist in all_playlists if playlist['name'].startswith('Jouw topnummers van 20') ## filter for playlists that start with 20 in dutch
        ]
    print()
    
    return eoty_playlists


def save_playlist_tracks_to_csv(playlist, output_dir):
    playlist_id = playlist['id']
    playlist_name = playlist['name']
    
    tracks = sp.playlist_tracks(playlist_id) ## fetch the tracks for the current playlist
    track_data = []

    for item in tracks['items']:
        track = item['track']
        track_name = track['name']
        track_artists = ', '.join([artist['name'] for artist in track['artists']])
        track_album = track['album']['name']
        track_id = track['id']

        track_data.append({
            "id": track_id,
            "title": track_name,
            "artist": track_artists,
            "album": track_album
        }) ## append track details to a list

    if track_data:
        df = pd.DataFrame(track_data)

        dutch_to_english = {"Jouw topnummers van":"Your Top Songs"}

        for dutch_prefix, english_translation in dutch_to_english.items():
            if playlist_name.startswith(dutch_prefix):
                english_name = playlist_name.replace(dutch_prefix, english_translation, 1)
                break
        else:
            english_name = playlist_name

        file_name = f"{english_name.replace(' ', '_')}_tracks.csv" ## replace the space with underscores
        file_path = os.path.join(output_dir, file_name)

        df.to_csv(file_path, index=False)
        print(f"Saved tracks of '{english_name}' to {file_path}")
    else:
        print(f"No tracks found for playlist: {playlist_name}")


def merge_and_rank_csv(years):
    for year in years:    
        file_pattern = f"{output_dir}/Your_Top_Songs_{year}*.csv"
        matching_files = glob.glob(file_pattern)
        
        for file in matching_files:
            playlist = pd.read_csv(file)
            
            playlist['year'] = year
            playlist['rank'] = range(1, len(playlist) + 1)
        
            if 'Album' in playlist.columns: ## remove album column
                playlist.drop(columns=['Album'], inplace=True)
            
            playlist[f'{year}'] = playlist['rank']
            playlist = playlist[['id','rank']] ## only save the id and rank
            
            rank_year_diff = (int(current_year)-int(year))*0.01
            playlist['rank'] = playlist['rank'] + rank_year_diff ## earlier years now weigh less
            
            playlist = playlist.rename(columns={'rank':f'{year}'})
            
            playlist.set_index('id', inplace=True)
            playlist.to_csv(f'{output_dir}/{year}_tracks.csv', index='id')


def fill_na_per_row(row):  ## this function fills empty cells per row with 101 and larger numbers
    counter = 101
    for i in range(len(row)):
        if pd.isna(row.iloc[i]):  # Use iloc to access values in the row
            row.iloc[i] = counter
            counter += 1
    return row


# def fetch_track_details(spotify_id):
#     try:
#         track_info = sp.track(spotify_id)
        
#         track_name = track_info['name']
#         artist_name = ', '.join(artist['name'] for artist in track_info['artists'])
#         return track_name, artist_name
#     except Exception as e:
#         print(f"Error fetching details for Spotify ID {spotify_id}: {e}")
#         return None, None


# def merge_duplicate_tracks(df): ## is not fully working yet
#     df = df.reset_index()

#     df['track'], df['artist'] = zip(*df['id'].apply(lambda x: fetch_track_details(x))) ## get track names and artists from spotify ID's

#     track_counts = df.groupby(['track', 'artist']).size()
#     duplicates = track_counts[track_counts > 1].index
#     duplicate_rows = df[df.set_index(['track', 'artist']).index.isin(duplicates)]

#     if len(duplicates) == 0:
#         print("No duplicates found.")
#         return df

#     merged_duplicates = duplicate_rows.groupby(['track', 'artist']).min().reset_index() ## takes the minimum value
#     non_duplicate_rows = df[~df.set_index(['track', 'artist']).index.isin(duplicates)]

#     results_df = pd.concat([non_duplicate_rows, merged_duplicates], ignore_index=True)
    
#     print(results_df.columns)
#     print(results_df)
    
#     for index, row in merged_duplicates.iterrows(): 
#         print(f"Merged track: {row['track']} by {row['artist']} with values: {row.to_dict()}")

#     return results_df


def create_playlist(user_id, playlist_name, playlist_description):
    playlist = sp.user_playlist_create(user_id, playlist_name, description=playlist_description)
    return playlist['id']


def add_tracks_to_playlist(playlist_id, track_ids):
    batch_size = 100  ## maximum number of track IDs per request
    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i:i+batch_size]
        sp.playlist_add_items(playlist_id, batch)
        print(f"Added {len(batch)} tracks to the playlist.")    



if __name__ == "__main__":
    
    all_playlists = fetch_all_playlists() ## all playlists of the user (authetication through webpage)
    print(f"Total number of playlists found on your account: {len(all_playlists)}")
    print()
    
    eoty_playlists = filter_for_eoty_playlists() ## filter for EOTY playlists
    
    if not eoty_playlists:
        print('No playlists were found starting with "Your Top Songs 20.." or "Jouw topnummers van 20..". Please make sure the playlists are in your account and change the names accordingly.')
    print(f"Total number of EOTY playlists found: {len(eoty_playlists)}")
    print()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir) ## make sure to input a directory to store the .csv files

    for playlist in eoty_playlists: ## stores all EOTY playlists in .csv format
        save_playlist_tracks_to_csv(playlist, output_dir=output_dir)

    files = os.listdir(output_dir)
    
    years = {
        re.search(r'(\d{4})', filename).group()
        for filename in files if filename.startswith('Your_Top_Songs') and filename.endswith('.csv')
        and re.search(r'(\d{4})', filename)
        }

    years = sorted(years) ## sort the years in order from low to high
    current_year = years[-1]
    oldest_year = years[0]

    print('Files were created for the years', years) 
           
    all_playlists = merge_and_rank_csv(years=years)
    
    csv_files = []

    for year in years:
        csv_files_path = f"{output_dir}/{year}_tracks.csv"
        csv_files.extend(glob.glob(csv_files_path))

    dataframes = [pd.read_csv(file, index_col='id') for file in csv_files]
    
    all_playlists = pd.concat(dataframes, axis=1) ## add all years together
    all_playlists = all_playlists.apply(fill_na_per_row, axis=1) ## filling uncharted tracks with values >100 for other years
    all_playlists = all_playlists[sorted(all_playlists.columns)] ## order columns

    # all_playlists = merge_duplicate_tracks(df=all_playlists) ## find and merge duplicates
    # print(all_playlists) ## not fully working yet
    
    all_playlists['total_rank'] = all_playlists.prod(axis=1) ## create total rank product
    all_playlists = all_playlists.sort_values('total_rank', ascending=True)
    all_playlists = all_playlists.reset_index()

    all_playlists.to_csv(f'{output_dir}/wrapped_{oldest_year}_{current_year}.csv')
    
    track_ids = all_playlists['id'].tolist()
    # print(track_ids)

    playlist_name = "Spotify Wrapped-up"  ## the playlist name
    playlist_description = f"A wrap-up of all your Spotify Wrapped playlists from {oldest_year} to {current_year} created with Python by Dene!"  ## playlist description
    new_playlist_id = create_playlist(user_id, playlist_name, playlist_description)
    
    add_tracks_to_playlist(new_playlist_id, track_ids) ## creating the playlist in the users account