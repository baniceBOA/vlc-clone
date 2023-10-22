from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.lang import Builder
import os


Builder.load_file(os.path.join(os.path.dirname(__file__), 'videocard.kv'))

class VideoCard(MDCard):
    thumb = StringProperty()
    drive = StringProperty()
    filename = StringProperty()
    time = StringProperty()
    source = StringProperty()

    def play_video(self, *args):
        app = MDApp.get_running_app()
        app.root.screen_manager.current = 'player'
        app.root.remove_widget(app.root.ids.bottom_bar)
        player = app.root.screen_manager.get_screen('player')
        player.source = self.source
        player.title = self.filename
        player.thumb = self.thumb

