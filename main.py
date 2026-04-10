__version__ = '1.2.0'
import os
os.environ['KIVY_VIDEO'] = 'ffpyplayer'
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, ListProperty
from kivy.core.window import Window
from kivy.utils import platform

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton

if platform != 'android':
    Window.size = (400, 688)
    Window.top = 1

from plyer import storagepath


from screens import VideoFolderScreen, VideoFileScreen, AudioScreen, Player
from components import SilverTopAppBar
from utils import check_and_request_all_files_access


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
    dialog = None
    def build(self):
        self.theme_cls.primary_palette = 'Orange'
        self.theme_cls.primary_hue = "800"
        self.theme_cls.theme_style = 'Dark'
        return VLC()
    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            from android import api_version
            # Request the modern media permissions required for API 33+
            request_permissions([
                Permission.READ_MEDIA_VIDEO,
                Permission.READ_MEDIA_AUDIO,
                Permission.READ_EXTERNAL_STORAGE, # Still needed for older phones
                Permission.WRITE_EXTERNAL_STORAGE
            ])

            
            if api_version >= 30:
                self.show_permission_explanation()
            
    def show_permission_explanation(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Storage Access Required",
                text=(
                    "To index and play your media files, this application requires access to "
                    "the device's storage. On the next screen, please find this app in the list "
                    "and toggle 'Allow access to manage all files' to ON."
                ),
                buttons=[
                    MDFlatButton(
                        text="LATER",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="OPEN SETTINGS",
                        on_release=self.proceed_to_settings
                    ),
                ],
            )
        self.dialog.open()

    def proceed_to_settings(self, *args):
        self.dialog.dismiss()
        # Call the JNI function we defined previously
        check_and_request_all_files_access()
    
    
if __name__ == '__main__':
    MainApp().run()