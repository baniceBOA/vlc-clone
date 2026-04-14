from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ListProperty, DictProperty, StringProperty
from kivy.clock import Clock
from threading import Thread
from functools import partial
import os

from components import AudioRV
from utils import get_audio_metadata
Builder.load_file(os.path.join(os.path.dirname(__file__), 'audioscreen.kv'))


class AudioScreen(MDScreen):
    music = ListProperty()
    search_query = StringProperty('')
    # Use dictionaries to group tracks by category
    artists_dict = DictProperty({})
    albums_dict = DictProperty({})
    genres_dict = DictProperty({})

    def find_music(self, interval):
        if hasattr(self, '_scan_thread') and self._scan_thread.is_alive():
            return
        self._scan_thread = Thread(target=self._find_music, daemon=True)
        self._scan_thread.start()

    def _find_music(self):
        music = []
        artists = {}
        albums = {}
        genres = {}
        app = MDApp.get_running_app()
        paths = getattr(app.root, 'system_storage', [])
        for path in paths:
            if not os.path.exists(path):
                continue
            try:
                for dirpath, dirnames, filenames in os.walk(path):
                    filenames = [f for f in filenames if not f.startswith('.')]
                    dirnames[:] = [d for d in dirnames if not d.startswith('.')]
                    for filename in filenames:
                        if filename.lower().endswith(('.mp3', '.m4a', '.wav', '.flac', '.ogg')):
                            music_path = os.path.join(dirpath, filename)
                            music.append(music_path)
                            meta = get_audio_metadata(music_path)
                            artist = meta.get('artist', 'Unknown Artist') or 'Unknown Artist'
                            album = meta.get('album', 'Unknown Album') or 'Unknown Album'
                            genre = meta.get('genre', 'Unknown Genre') or 'Unknown Genre'
                            artists.setdefault(artist, []).append(music_path)
                            albums.setdefault(album, []).append(music_path)
                            genres.setdefault(genre, []).append(music_path)
            except Exception as e:
                print(f'Audio scan failed for {path}: {e}')

        Clock.schedule_once(partial(self._on_find_complete, music, artists, albums, genres), 0)

    def _on_find_complete(self, music, artists, albums, genres, dt):
        self.music = music
        self.artists_dict = artists
        self.albums_dict = albums
        self.genres_dict = genres
        self.update(0)

    def on_pre_enter(self, *args):
        if hasattr(self.ids, 'search_field'):
            self.ids.search_field.text = ''

    def on_enter(self, *args):
        Clock.schedule_once(self.find_music, 0.2)

    def on_search(self, query):
        self.search_query = query.strip().lower()
        self.update(0)

    def update(self, interval):
        query = self.search_query
        filtered_music = [
            m for m in self.music
            if not query or query in os.path.basename(m).lower() or query in m.lower()
        ]
        if hasattr(self.ids, 'tracks') and hasattr(self.ids.tracks.ids, 'audio_rv_widget'):
            self.ids.tracks.ids.audio_rv_widget.music_file = filtered_music

        artists = self.artists_dict
        if query:
            artists = {
                artist: tracks for artist, tracks in self.artists_dict.items()
                if query in artist.lower() or any(query in os.path.basename(p).lower() for p in tracks)
            }
        if hasattr(self.ids, 'artist_rv'):
            self.ids.artist_rv.data = [
                {"text": artist, "secondary_text": f"{len(tracks)} Songs"}
                for artist, tracks in artists.items()
            ]

        albums = self.albums_dict
        if query:
            albums = {
                album: tracks for album, tracks in self.albums_dict.items()
                if query in album.lower() or any(query in os.path.basename(p).lower() for p in tracks)
            }
        if hasattr(self.ids, 'album_rv'):
            self.ids.album_rv.data = [
                {"text": album, "secondary_text": "View Album Contents"}
                for album, tracks in albums.items()
            ]

        genres = self.genres_dict
        if query:
            genres = {
                genre: tracks for genre, tracks in self.genres_dict.items()
                if query in genre.lower() or any(query in os.path.basename(p).lower() for p in tracks)
            }
        if hasattr(self.ids, 'genre_rv'):
            self.ids.genre_rv.data = [
                {"text": str(genre), "secondary_text": f"{len(tracks)} Tracks"}
                for genre, tracks in genres.items()
            ]
