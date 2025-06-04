import spotipy
from spotipy.oauth2 import SpotifyOAuth
from src.config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

class SpotifyClient:
    def __init__(self):
        self.scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=self.scope,
            cache_path=".spotify_cache"
        ))
        
    def play(self):
        try:
            self.sp.start_playback()
            return True
        except Exception as e:
            print(f"Error playing track: {e}")
            return False
    
    def pause(self):
        try:
            self.sp.pause_playback()
            return True
        except Exception as e:
            print(f"Error pausing track: {e}")
            return False
    
    def next_track(self):
        try:
            self.sp.next_track()
            return True
        except Exception as e:
            print(f"Error skipping to next track: {e}")
            return False
    
    def previous_track(self):
        try:
            self.sp.previous_track()
            return True
        except Exception as e:
            print(f"Error going to previous track: {e}")
            return False
    
    def increase_volume(self, step=5):
        try:
            current_playback = self.sp.current_playback()
            if current_playback and 'device' in current_playback:
                current_volume = current_playback['device']['volume_percent']
                new_volume = min(100, current_volume + step)
                self.sp.volume(new_volume)
                return True
            return False
        except Exception as e:
            print(f"Error increasing volume: {e}")
            return False
    
    def decrease_volume(self, step=5):
        try:
            current_playback = self.sp.current_playback()
            if current_playback and 'device' in current_playback:
                current_volume = current_playback['device']['volume_percent']
                new_volume = max(0, current_volume - step)
                self.sp.volume(new_volume)
                return True
            return False
        except Exception as e:
            print(f"Error decreasing volume: {e}")
            return False
            
    def get_current_track(self):
        try:
            current = self.sp.currently_playing()
            if current and current['item']:
                track = current['item']
                artists = ", ".join([artist['name'] for artist in track['artists']])
                return {
                    "name": track['name'],
                    "artist": artists,
                    "album": track['album']['name'],
                    "cover_url": track['album']['images'][0]['url'] if track['album']['images'] else None,
                    "is_playing": current['is_playing']
                }
            return None
        except Exception as e:
            print(f"Error getting current track: {e}")
            return None