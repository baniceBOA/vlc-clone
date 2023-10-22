
from kivymd.uix.card import MDCard
from kivy.uix.behaviors import ButtonBehavior
from kivymd.app import MDApp
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder
import os
Builder.load_file(os.path.join(os.path.dirname(__file__), 'videofolder.kv'))

class VideoFolder(MDCard):
    folder_collect_thumb = StringProperty()
    foldername = StringProperty()
    files = ListProperty()
    vid_count = StringProperty()

    def change_screen(self):
        app = MDApp.get_running_app()
        def callback():
            app.root.toolbar.title = 'VLC'
            app.root.screen_manager.current = 'videofolder'
            app.root.toolbar.left_action_items = []
        app.root.toolbar.left_action_items = [ ['arrow-left', lambda x:callback()], ]
        app.root.screen_manager.current = 'videofilescreen'
        app.root.toolbar.title = self.foldername
        videofilescreen = app.root.screen_manager.get_screen('videofilescreen')
        videofilescreen.files = self.files
