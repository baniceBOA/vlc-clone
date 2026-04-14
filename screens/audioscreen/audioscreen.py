from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ListProperty, DictProperty, StringProperty
from kivy.clock import Clock
from threading import Thread
from functools import partial
import os
import time

from components import AudioRV
from utils import get_audio_metadata
from utils.cache_utils import load_file_list_cache, sync_files_cache
Builder.load_file(os.path.join(os.path.dirname(__file__), 'audioscreen.kv'))


class AudioScreen(MDScreen):
    music = ListProperty()
    search_query = StringProperty('')
    # Use dictionaries to group tracks by category
    artists_dict = DictProperty({})
    albums_dict = DictProperty({})
    genres_dict = DictProperty({})
    _metadata_thread = None
    _metadata_thread_stop = False
    AUDIO_EXTENSIONS = ('.mp3', '.m4a', '.wav', '.flac', '.ogg')

    def find_music(self, interval):
        if hasattr(self, '_scan_thread') and self._scan_thread.is_alive():
            return
        self._scan_thread = Thread(target=self._find_music, daemon=True)
        self._scan_thread.start()

    def _find_music(self):
        app = MDApp.get_running_app()
        paths = getattr(app.root, 'system_storage', [])
        music = sync_files_cache('audio_files', paths, self.AUDIO_EXTENSIONS)
        Clock.schedule_once(partial(self._on_find_complete, music), 0)

    def _on_find_complete(self, music, dt):
        self.music = music
        self.artists_dict = {}
        self.albums_dict = {}
        self.genres_dict = {}
        self.update(0)
        if 'audio_rv_widget' in self.ids:
            self.ids.audio_rv_widget.music_file = self.music
        self._start_metadata_loader(music)

    def _start_metadata_loader(self, music):
        self._metadata_thread_stop = True
        if self._metadata_thread and self._metadata_thread.is_alive():
            self._metadata_thread.join(timeout=0.1)
        self._metadata_thread_stop = False
        self._metadata_thread = Thread(target=self._load_metadata_in_chunks, args=(music,), daemon=True)
        self._metadata_thread.start()

    def _load_metadata_in_chunks(self, music):
        chunk_size = 20
        for i in range(0, len(music), chunk_size):
            if self._metadata_thread_stop:
                return
            artists = {}
            albums = {}
            genres = {}
            chunk = music[i:i + chunk_size]
            for music_path in chunk:
                try:
                    meta = get_audio_metadata(music_path)
                    artist = meta.get('artist', 'Unknown Artist') or 'Unknown Artist'
                    album = meta.get('album', 'Unknown Album') or 'Unknown Album'
                    genre = meta.get('genre', 'Unknown Genre') or 'Unknown Genre'
                    artists.setdefault(artist, []).append(music_path)
                    albums.setdefault(album, []).append(music_path)
                    genres.setdefault(genre, []).append(music_path)
                except Exception as e:
                    print(f'Audio metadata chunk failed for {music_path}: {e}')
            Clock.schedule_once(partial(self._apply_metadata_chunk, artists, albums, genres), 0)
            time.sleep(0.05)

    def _apply_metadata_chunk(self, artists, albums, genres, dt):
        merged_artists = dict(self.artists_dict)
        for artist, tracks in artists.items():
            merged_artists.setdefault(artist, []).extend(tracks)
        self.artists_dict = merged_artists

        merged_albums = dict(self.albums_dict)
        for album, tracks in albums.items():
            merged_albums.setdefault(album, []).extend(tracks)
        self.albums_dict = merged_albums

        merged_genres = dict(self.genres_dict)
        for genre, tracks in genres.items():
            merged_genres.setdefault(genre, []).extend(tracks)
        self.genres_dict = merged_genres

        self.update(0)

    def on_pre_enter(self, *args):
        if hasattr(self.ids, 'search_field'):
            self.ids.search_field.text = ''

    def on_enter(self, *args):
        self.load_cached_music()
        Clock.schedule_once(self.find_music, 0.2)

    def load_cached_music(self):
        cached = load_file_list_cache('audio_files')
        if not cached:
            return

        music = [path for path in cached.keys() if os.path.exists(path) and path.lower().endswith(self.AUDIO_EXTENSIONS)]
        if not music:
            return

        music.sort()
        self.music = music
        self.artists_dict = {}
        self.albums_dict = {}
        self.genres_dict = {}
        if 'audio_rv_widget' in self.ids:
            self.ids.audio_rv_widget.music_file = self.music
        self.update(0)
        self._start_metadata_loader(self.music)

    def on_search(self, query):
        self.search_query = query.strip().lower()
        self.update(0)

    def update(self, interval):
        query = self.search_query
        filtered_music = [
            m for m in self.music
            if not query or query in os.path.basename(m).lower() or query in m.lower()
        ]
        if 'audio_rv_widget' in self.ids:
            self.ids.audio_rv_widget.music_file = filtered_music

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
