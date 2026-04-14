from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.properties import ListProperty, StringProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
import os

from components import VideoCard
Builder.load_file(os.path.join(os.path.dirname(__file__), 'videofilescreen.kv'))


class VideoFileScreen(MDScreen):
    ''' Display the Video file according to the files '''
    files = ListProperty()
    all_files = ListProperty()
    search_query = StringProperty('')

    def on_pre_enter(self, *args):
        ''' perform cleaning of the data before changing the data'''
        self.ids.rv.data = []
        self.all_files = self.files
        self.search_query = ''

    def on_enter(self,*args):
        Clock.schedule_once(self.get_files, 1)
    def on_search(self, query):
        self.search_query = query.strip().lower()
        self.render_files()
    def get_files(self, invterval):
        self.ids.rv.data = []
        self.all_files = self.files
        self.render_files()
    def render_files(self):
        self.ids.rv.data = []
        thumb_dir = os.path.join('assests', 'thumbs')
        app = MDApp.get_running_app()
        if app and platform == 'android':
            thumb_dir = os.path.join(app.user_data_dir, 'assests', 'thumbs')

        query = self.search_query
        for file in self.all_files:
            if query and query not in os.path.basename(file).lower() and query not in file.lower():
                continue
            data = {}
            data['thumb'] = os.path.join(thumb_dir, f'{os.path.splitext(os.path.split(file)[1])[0]}.png')
            data['drive'] = os.path.splitdrive(file)[0]
            data['filename'] = os.path.split(file)[1]
            data['source'] = file
            self.ids.rv.data.append(data)

    