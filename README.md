## Spotify Wrapper by Dene
This script summarizes all your end-of-the-year Spotify Wrapped playlists into one playlist, which is added to your account under the name **Spotify Wrapped-up**. I need to add your Spotify-account mail address to my project on the Spotify Developer website to make it work, or you need to have your own Spotify Developer account.

The first step is to follow all the Spotify Wrapped top-100 playlists that were created for you by Spotify. To do this, follow these instructions.
    
- Find the end-of-the-year Spotify Wrapped playlists by searching for 'Your Top Songs 20..' on Spotify ('Jouw favoriete nummers van 20..' in Dutch). Make sure that the playlists are uploaded by the official Spotify-account (Made for you) and not by a user.
    
- Add the playlists to your account. Not by following them, but by selecting 'Add to other playlist' and selecting 'Add to new playlist'. Your Spotify Wrapped playlist is now a personal playlist in your account, not made for you but by you.
   
- Do this for every Spotify Wrapped playlist that you want to include.

  
**Do not change the names of the playlists. Anything other than the original Dutch or English names will not work**

No need to install Python or dependencies! The script has been packaged into an executable.

## How to Run:

1. **Download the Executable**: Download and navigate to the `your_script.exe` (Windows) or `your_script` (macOS/Linux).

2. **Run the Executable**:
   - On **Windows**, double-click `spotify_wrapper.exe` to run the program.
   - On **macOS/Linux**, open the terminal, navigate to the folder containing `spotify_wrapper`, and run:
     ```bash
     ./spotify_wrapper
     ```

3. **Spotify Login**: When the script runs, you will be prompted to log in to your Spotify account in your browser.

4. **Enjoy Your Playlist**: Once logged in, the script will create a new playlist called 'Spotify Wrapped-up' for you based on the end-of-the-year playlists that were in your account.
