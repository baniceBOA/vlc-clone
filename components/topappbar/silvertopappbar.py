from kivymd.uix.toolbar import MDTopAppBar
from kivy.lang import Builder
from kivymd.app import MDApp
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'silvertopappbar.kv'))

class SilverTopAppBar(MDTopAppBar):
    def search_action(self, *args):
        app = MDApp.get_running_app()
        if app and app.root and hasattr(app.root, 'on_toolbar_search'):
            app.root.on_toolbar_search()