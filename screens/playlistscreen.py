from kivy.lang import Builder
from kivy.properties import ListProperty
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'playlistscreen.kv'))


class PlaylistScreen(MDScreen):
    playlist = ListProperty()

    def on_enter(self, *args):
        self.load_playlist()

    def load_playlist(self):
        app = MDApp.get_running_app()
        self.playlist = []
        try:
            user_playlist = getattr(app, 'user_playlist', None)
            if user_playlist is not None:
                self.playlist = list(user_playlist)
            else:
                audio_screen = app.root.screen_manager.get_screen('audioscreen')
                self.playlist = list(getattr(audio_screen, 'music', []))
        except Exception as exc:
            print(f'Unable to load playlist: {exc}')
        self.render_playlist()

    def render_playlist(self):
        self.ids.rv.data = []
        for entry in self.playlist:
            self.ids.rv.data.append({
                'text': os.path.basename(entry),
            })
