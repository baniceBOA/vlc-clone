import os
os.environ['KIVY_VIDEO'] = 'ffpyplayer'
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, ListProperty
from kivy.core.window import Window

Window.size = (400, 688)
Window.top = 1

from plyer import storagepath


from screens import VideoFolderScreen, VideoFileScreen, AudioScreen, Player
from components import SilverTopAppBar


class VLC(MDScreen):
    toolbar = ObjectProperty()
    screen_manager = ObjectProperty()
    system_storage = ListProperty([storagepath.get_videos_dir(), storagepath.get_music_dir(), storagepath.get_downloads_dir()])

    def on_enter(self, *args):
        print(self.ids.sliverappbar.toolbar_cls)
    def tab_switch(self, instance_tabs,instance_tab,instance_tab_label,tab_text):
        print(self.system_storage)
        if instance_tab.title == 'video':
            self.screen_manager.current = 'videofolder'
        elif instance_tab.title == 'music':
            self.screen_manager.current = 'audioscreen'


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Orange'
        self.theme_cls.primary_hue = "800"
        self.theme_cls.theme_style = 'Dark'
        return VLC()
    
if __name__ == '__main__':
    MainApp().run()