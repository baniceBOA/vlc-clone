from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'browsescreen.kv'))


class BrowseScreen(MDScreen):
    entries = ListProperty()
    search_query = StringProperty('')

    def on_enter(self, *args):
        Clock.schedule_once(self.load_entries, 0.2)

    def on_search(self, query):
        self.search_query = query.strip().lower()
        self.render_entries()

    def load_entries(self, interval):
        app = MDApp.get_running_app()
        storage_paths = getattr(app.root, 'system_storage', [])
        entries = []
        for storage_path in storage_paths:
            if not os.path.exists(storage_path):
                continue
            try:
                for item in sorted(os.listdir(storage_path)):
                    if item.startswith('.'):
                        continue
                    item_path = os.path.join(storage_path, item)
                    if os.path.isdir(item_path):
                        entries.append({
                            'text': item,
                            'secondary_text': 'Folder',
                            'path': item_path,
                        })
                    else:
                        ext = os.path.splitext(item)[1].lower()
                        if ext in ('.mp4', '.mkv', '.avi', '.mp3', '.m4a', '.wav', '.flac', '.ogg'):
                            entries.append({
                                'text': item,
                                'secondary_text': f'{ext[1:].upper()} file',
                                'path': item_path,
                            })
            except Exception as exc:
                print(f'Browse load failed for {storage_path}: {exc}')

        self.entries = entries
        self.render_entries()

    def render_entries(self):
        query = self.search_query
        self.ids.rv.data = []
        for entry in self.entries:
            if query and query not in entry['text'].lower() and query not in entry['secondary_text'].lower():
                continue
            self.ids.rv.data.append({
                'text': entry['text'],
                'secondary_text': entry['secondary_text'],
            })
