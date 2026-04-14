from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.properties import ListProperty, StringProperty
from kivy.lang import Builder
from kivy.clock import Clock
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'searchscreen.kv'))


class SearchScreen(MDScreen):
    search_query = StringProperty('')
    search_mode = StringProperty('video')
    results = ListProperty()
    context_screen = StringProperty('')

    def set_search_context(self, current_screen_name):
        if current_screen_name == 'audioscreen':
            self.search_mode = 'audio'
        elif current_screen_name in ['videofolder', 'videofilescreen']:
            self.search_mode = 'video'
        else:
            self.search_mode = 'video'
        self.context_screen = current_screen_name
        self.search_query = ''
        self.results = []

    def on_enter(self, *args):
        self.ids.search_field.text = ''
        self.ids.search_field.hint_text = 'Search audio' if self.search_mode == 'audio' else 'Search videos'
        Clock.schedule_once(lambda dt: setattr(self.ids.search_field, 'focus', True), 0.1)
        self.render_results()

    def on_search(self, query):
        self.search_query = query.strip().lower()
        self.render_results()

    def render_results(self):
        self.results = []
        query = self.search_query
        app = MDApp.get_running_app()
        if self.search_mode == 'audio':
            audio_screen = app.root.screen_manager.get_screen('audioscreen')
            audio_files = getattr(audio_screen, 'music', []) or []
            for file in audio_files:
                basename = os.path.basename(file)
                if query and query not in basename.lower() and query not in file.lower():
                    continue
                self.results.append({
                    'text': basename,
                    'secondary_text': file,
                })
        else:
            video_screen = app.root.screen_manager.get_screen('videofilescreen')
            video_files = getattr(video_screen, 'all_files', []) or []
            for file in video_files:
                basename = os.path.basename(file)
                if query and query not in basename.lower() and query not in file.lower():
                    continue
                self.results.append({
                    'text': basename,
                    'secondary_text': file,
                })
        if not self.results and query:
            self.results = [{'text': 'No results found', 'secondary_text': ''}]
