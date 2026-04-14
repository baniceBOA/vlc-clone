
from kivymd.uix.screen import  MDScreen
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.snackbar import Snackbar
from mutagen.mp4 import MP4
from kivy.clock import Clock
from kivy.utils import platform
from kivymd.app import MDApp
from datetime import timedelta
from plyer import accelerometer

from ffpyplayer.player import MediaPlayer
import time

import os
import subprocess

Builder.load_file(os.path.join(os.path.dirname(__file__), 'vplayer.kv'))


class Player(MDScreen):
    title = StringProperty()
    source = StringProperty()
    duration = NumericProperty(0)
    thumb = StringProperty()
    time_duration = StringProperty('00:00')
    is_landscape = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.late_init,1)
        self._accel_event = None

    def late_init(self, interval):
        self.ids.video.bind(position=self.change_slider_value)

    def on_enter(self, *args):
        if platform == 'android':
            try:
                accelerometer.enable()
            except Exception as e:
                print('Accelerometer enable failed:', e)
            self._accel_event = Clock.schedule_interval(self.check_device_orientation, 0.5)
        self.apply_orientation()

    def on_pre_enter(self, *args):
        self.ids.video.preview = self.thumb

    def on_leave(self, *args):
        self.ids.video.play = False
        self.ids.video.unload()
        app = MDApp.get_running_app()
        if app and app.root and hasattr(app.root, 'ids') and app.root.ids.get('bottom_bar'):
            try:
                if not app.root.ids.bottom_bar.parent:
                    app.root.add_widget(app.root.ids.bottom_bar)
            except Exception:
                pass
        if platform == 'android':
            try:
                accelerometer.disable()
            except Exception:
                pass
            if self._accel_event:
                self._accel_event.cancel()
                self._accel_event = None
            self.is_landscape = False
            self.apply_orientation()

    def apply_orientation(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                ActivityInfo = autoclass('android.content.pm.ActivityInfo')
                activity = PythonActivity.mActivity
                orientation = ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE if self.is_landscape else ActivityInfo.SCREEN_ORIENTATION_SENSOR_PORTRAIT
                activity.setRequestedOrientation(orientation)
            except Exception as e:
                print('Orientation apply failed:', e)

        if self.ids.get('top_bar'):
            self.ids.top_bar.opacity = 0 if self.is_landscape else 1
            self.ids.top_bar.disabled = self.is_landscape
        if self.ids.get('control_bar'):
            self.ids.control_bar.opacity = 0 if self.is_landscape else 1
            self.ids.control_bar.disabled = self.is_landscape

    def toggle_landscape(self):
        self.is_landscape = not self.is_landscape
        self.apply_orientation()

    def enter_pip_mode(self):
        if platform != 'android':
            return
        try:
            from jnius import autoclass
            Build = autoclass('android.os.Build')
            if Build.VERSION.SDK_INT >= 26:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                activity.enterPictureInPictureMode()
        except Exception as e:
            print('PIP failed:', e)

    def close_player(self, *args):
        app = MDApp.get_running_app()
        if app and app.root:
            if hasattr(app.root, 'ids') and app.root.ids.get('bottom_bar'):
                try:
                    if not app.root.ids.bottom_bar.parent:
                        app.root.add_widget(app.root.ids.bottom_bar)
                except Exception:
                    pass
            if hasattr(app.root, 'go_back') and app.root.go_back():
                return True
            if hasattr(app.root, 'screen_manager') and app.root.screen_manager.has_screen('videofolder'):
                app.root.screen_manager.current = 'videofolder'
                return True
        return False

    def check_device_orientation(self, dt):
        try:
            acc = accelerometer.acceleration
        except Exception:
            return
        if not acc or len(acc) < 2:
            return
        x, y, _ = acc
        if x is None or y is None:
            return
        if abs(x) > abs(y) and abs(x) > 3:
            desired = True
        elif abs(y) > abs(x) and abs(y) > 3:
            desired = False
        else:
            return
        if desired != self.is_landscape:
            self.is_landscape = desired
            self.apply_orientation()

    def on_source(self, instance, value):
        try:
            if not value or not os.path.exists(value):
                raise FileNotFoundError(f"Video file not found: {value}")

            if value.endswith('.mp4'):
                self.duration = MP4(value).info.length
                delta = timedelta(seconds=self.duration)
                h, m, s = str(delta).split(':')
                self.time_duration = f'{h}:{m}:{round(float(s))}'
            elif value.endswith('.mkv') or value.endswith('.avi'):
                self.duration = self.get_length(value)
                delta = timedelta(seconds=self.duration)
                h, m, s = str(delta).split(':')
                self.time_duration = f'{h}:{m}:{round(float(s))}'
            else:
                # prevent division by zero error
                self.duration = 1
        except Exception as exc:
            print(f"Video on_source failed for {value}: {exc}")
            self.duration = 1
            self.time_duration = '00:00'
            Snackbar(
                text=f"Cannot load video metadata: {exc}",
                duration=4,
            ).open()

            
        

    
    def play_video(self, instance):
        try:
            if instance.icon == 'play':
                self.ids.video.play = True
                instance.icon = 'pause'
            elif instance.icon == 'pause':
                self.ids.video.play = False
                instance.icon = 'play'
        except Exception as exc:
            print(f"Video playback control failed: {exc}")
            Snackbar(
                text=f"Cannot play/pause video: {exc}",
                duration=4,
            ).open()
    def seek_video(self, value):
        self.ids.video.seek(value/100, precise=True)

    def change_slider_value(self, instance, value):
       
        time = str(timedelta(seconds=self.duration) - timedelta(seconds=value)).zfill(3)
        h, m, s = time.split(':')
        self.time_duration = f'{h}:{m}:{round(float(s))}'
        position = (value/self.duration)*100
        self.ids.video_progressbar.value = position
    
    def get_length(self, filename):
        if platform == 'android':
            try:
                player = MediaPlayer(filename, ff_opts={'nodisp': True, 'an': True})
                
                # Wait a moment for the player to initialize and read metadata
                timeout = time.time() + 2
                while time.time() < timeout:
                    metadata = player.get_metadata()
                    if metadata and 'duration' in metadata:
                        return float(metadata['duration'])
                    time.sleep(0.1)
                
                player.close_player()
            except Exception as e:
                print(f"Error getting duration: {e}")
            
            return 0
        else:
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                    "format=duration", "-of",
                                    "default=noprint_wrappers=1:nokey=1", filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            return float(result.stdout)

        
        # Instead of subprocess.run(['ffprobe', ...])

