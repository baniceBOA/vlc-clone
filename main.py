__version__ = '1.2.0'
import os
os.environ['KIVY_VIDEO'] = 'ffpyplayer'
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, ListProperty
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivymd.uix.snackbar import Snackbar

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton

if platform != 'android':
    Window.size = (400, 688)
    Window.top = 1

from plyer import storagepath


from screens import VideoFolderScreen, VideoFileScreen, AudioScreen, BrowseScreen, PlaylistScreen, Player
from components import SilverTopAppBar
from utils import check_and_request_all_files_access, has_manage_storage_permission


class VLC(MDScreen):
    toolbar = ObjectProperty()
    screen_manager = ObjectProperty()
    system_storage = ListProperty()
    screen_history = ListProperty()
    _ignore_history = False
    _back_pressed = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_storage = self.get_adaptive_paths()
        self.screen_history = []
        self._ignore_history = False
        self._back_pressed = False

    def on_kv_post(self, base_widget):
        self.screen_manager.bind(current=self.on_screen_current)
        self._prev_screen = self.screen_manager.current

    def on_screen_current(self, manager, value):
        if self._ignore_history:
            self._ignore_history = False
        else:
            if hasattr(self, '_prev_screen') and self._prev_screen and self._prev_screen != value:
                self.screen_history.append(self._prev_screen)
        self._prev_screen = value

    def go_back(self):
        if self.screen_history:
            previous = self.screen_history.pop()
            self._ignore_history = True
            self.screen_manager.current = previous
            return True

        if self._back_pressed:
            Window.close()
            return True

        self._back_pressed = True
        Snackbar(text='Press back again to exit').open()
        Clock.schedule_once(self.reset_back_pressed, 2)
        return True

    def reset_back_pressed(self, dt):
        self._back_pressed = False

    def get_adaptive_paths(self):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            # On Android, we target the root of the user's shared storage
            primary = primary_external_storage_path()
            return [primary, ]
        elif platform == 'ios':
            # iOS is highly restricted; usually you only get the app's Documents folder
            return [os.path.expanduser('~/Documents')]
        else:
            # Desktop (Windows/Linux/macOS)
            try:
                return [
                    storagepath.get_videos_dir(),
                    storagepath.get_music_dir(),
                    storagepath.get_downloads_dir()
                ]
            except Exception:
                # Fallback if plyer fails on certain Linux distros
                home = os.path.expanduser("~")
                return [os.path.join(home, d) for d in ['Videos', 'Music', 'Downloads']]

    def on_enter(self, *args):
        print(self.ids.sliverappbar.toolbar_cls)
    def tab_switch(self, instance_tabs,instance_tab,instance_tab_label,tab_text):
        print(self.system_storage)
        if instance_tab.title == 'video':
            self.screen_manager.current = 'videofolder'
        elif instance_tab.title == 'music':
            self.screen_manager.current = 'audioscreen'
        elif instance_tab.title == 'Browse':
            self.screen_manager.current = 'browse'
        elif instance_tab.title == 'playlist':
            self.screen_manager.current = 'playlist'


class MainApp(MDApp):
    dialog = None
    current_audio = None
    def build(self):
        self.theme_cls.primary_palette = 'Orange'
        self.theme_cls.primary_hue = "800"
        self.theme_cls.theme_style = 'Dark'
        if platform == 'android':
            Window.softinput_mode = "adjust_resize"
        return VLC()
    def on_start(self):
        Window.bind(on_keyboard=self.on_keyboard)
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

            try:
                from android import activity
                activity.bind(on_new_intent=self.on_new_intent)
                self.process_audio_intent(activity.getIntent())
            except Exception as e:
                print('Audio intent bind failed:', e)

            if api_version >= 30:
                if not has_manage_storage_permission():
                    self.show_permission_explanation()
    def on_pause(self):
        return True
    
            
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

    def on_keyboard(self, window, key, *args):
        if key == 27:
            if self.root:
                return self.root.go_back()
        return False

    def on_new_intent(self, intent):
        self.process_audio_intent(intent)

    def process_audio_intent(self, intent):
        if not intent:
            return
        try:
            action = intent.getStringExtra('audio_action')
            if action and self.current_audio:
                if action == 'toggle':
                    if self.current_audio.player and self.current_audio.player.state == 'play':
                        self.current_audio.toggle_playback()
                    else:
                        self.current_audio.play_from_notification()
                elif action == 'stop':
                    self.current_audio.stop_from_notification()
                elif action == 'open':
                    pass
        except Exception as e:
            print('Audio intent processing failed:', e)

    def on_pause(self):
        if platform == 'android' and self.root:
            try:
                player = self.root.screen_manager.get_screen('player')
                if getattr(player.ids.video, 'play', False):
                    player.enter_pip_mode()
            except Exception as e:
                print('Enter PIP on pause failed:', e)
        return True


if __name__ == '__main__':
    MainApp().run()