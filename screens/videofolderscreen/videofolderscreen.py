from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.properties import ListProperty, DictProperty
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import platform
import os
from threading import Thread
from functools import partial

from utils import create_thumbnail
from components import VideoFolder, SilverTopAppBar
Builder.load_file(os.path.join(os.path.dirname(__file__), 'videofolderscreen.kv'))


class VideoFolderScreen(MDScreen):
    folders = DictProperty()
    ''' Display the  videos according to the folders they belong to'''
    def _find_index_in_motion_filter(self, type_id, widget):
        return super()._find_index_in_motion_filter(type_id, widget)
    def find_videos(self, interval):
        Thread(target=self._scan_videos, daemon=True).start()

    def _scan_videos(self):
        app = MDApp.get_running_app()
        paths = app.root.system_storage
        videos = []
        folders = {}

        for path in paths:
            for dirpath, dirname, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.mp4') or filename.endswith('.mkv') or filename.endswith('.avi'):
                        filepath = os.path.join(dirpath, filename)
                        videos.append(filepath)

        for vid in videos:
            dirs = os.path.dirname(vid).split(os.sep)[-1]
            if dirs in folders:
                continue
            metadata = {}
            metadata['files'] = [os.path.join(os.path.dirname(vid), filename) for filename in os.listdir(os.path.dirname(vid)) if self.check_video(filename)]
            metadata['count'] = len(metadata['files'])
            folders[dirs] = metadata

        Clock.schedule_once(partial(self._on_scan_complete, videos, folders), 0)

    def _on_scan_complete(self, videos, folders, interval):
        self.videos = videos
        self.folders = folders
        self.update(interval)
        Thread(target=self.create_thumb_pic, daemon=True).start()

    def on_enter(self, *args):
        Logger.info('Finding Images')
        if not self.folders:
            Clock.schedule_once(self.find_videos, 1)

    def check_video(self, filename):
        if filename.endswith('.mp4') or filename.endswith('.mkv')  or filename.endswith('.avi'):
            return True
        else:
            return False

    def get_thumb_dir(self):
        app = MDApp.get_running_app()
        if app and platform == 'android':
            return os.path.join(app.user_data_dir, 'assests', 'thumbs')
        return os.path.join('assests', 'thumbs')

    def on_folders(self, *args):
        #Clock.schedule_once(self.update, 1)
        pass 
    def create_thumb_pic(self):
        thumb_dir = self.get_thumb_dir()
        os.makedirs(thumb_dir, exist_ok=True)
        existing_thumbs = set(os.listdir(thumb_dir))

        for filename in self.videos:
            thumb_name = f"{os.path.splitext(os.path.basename(filename))[0]}.png"
            thumb_path = os.path.join(thumb_dir, thumb_name)
            if thumb_name in existing_thumbs and os.path.exists(thumb_path):
                continue

            if not os.path.exists(filename):
                continue

            try:
                create_thumbnail(filename, output_dir=thumb_dir)
                Clock.schedule_once(self.refresh_thumbnails, 0)
            except Exception as e:
                Logger.error(f"VideoFolderScreen:create_thumb_pic {e}")

    def refresh_thumbnails(self, interval):
        self.ids.rv.data = []
        self.update(interval)

    def update(self, interval):
        self.ids.rv.data = []
        thumb_dir = self.get_thumb_dir()
        for folder, count in self.folders.items():
            data = {}
            data['foldername'] = folder
            data['vid_count'] = f"{count['count']} videos"
            first_file = count['files'][0] if count['files'] else None
            if first_file:
                expected_thumb = os.path.join(thumb_dir, f"{os.path.splitext(os.path.basename(first_file))[0]}.png")
                data['folder_collect_thumb'] = expected_thumb if os.path.exists(expected_thumb) else 'assests/thumbs/rihanna.png'
            else:
                data['folder_collect_thumb'] = 'assests/thumbs/rihanna.png'
            data['files'] = count['files']
            self.ids.rv.data.append(data)
        
    
            
