
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ListProperty, DictProperty
from kivy.clock import Clock
import os

from components import AudioRV
from utils import get_audio_metadata
Builder.load_file(os.path.join(os.path.dirname(__file__), 'audioscreen.kv'))



class AudioScreen(MDScreen):
    music = ListProperty()
    # Use dictionaries to group tracks by category
    artists_dict = DictProperty({})
    albums_dict = DictProperty({})
    def find_music(self, interval):
        self.music = []
        app = MDApp.get_running_app()
        paths = app.root.system_storage
        for path in paths:
            if not os.path.exists(path):
                continue  
            for dirpath, dirname, filenames in os.walk(path):
                filenames = [f for f in filenames if not f[0] == '.']
                dirname[:] = [d for d in dirname if not d[0] == '.']
                for filename in filenames:
                    if filename.endswith('.mp3') or filename.endswith('.m4a'):
                        music_path = os.path.join(dirpath, filename)
                        self.music.append(music_path)
                        meta = get_audio_metadata(music_path)
                        # Group by Artist
                        artist = meta['artist']
                        if artist not in self.artists_dict:
                            self.artists_dict[artist] = []
                        self.artists_dict[artist].append(music_path)
                        # Group by Album
                        album = meta['album']
                        if album not in self.albums_dict:
                            self.albums_dict[album] = []
                        self.albums_dict[album].append(music_path)


    def on_pre_enter(self, *args):
        pass
    def on_enter(self, *args):
        Clock.schedule_once(self.find_music, 0.2)
        Clock.schedule_once(self.update, 1)
    def update(self, interval):
        for music in self.music: 
            self.ids.tracks.ids.audio_rv.music_file.append(music)
        # 2. Update Artists Tab
        
        if hasattr(self.ids, 'artist_rv'):
            self.ids.artist_rv.data = [
                {"text": artist, "secondary_text": f"{len(tracks)} Songs"} 
                for artist, tracks in self.artists_dict.items()
            ]

        # 3. Update Albums Tab
        if hasattr(self.ids, 'album_rv'):
            self.ids.album_rv.data = [
                {"text": album, "secondary_text": "View Album Contents"} 
                for album, tracks in self.albums_dict.items()
            ]
        # 4. Update Genres Tab
        if hasattr(self.ids, 'genre_rv'):
            self.ids.genre_rv.data = [
                {"text": str(genre), "secondary_text": f"{len(tracks)} Tracks"} 
                for genre, tracks in self.genres_dict.items()
            ]