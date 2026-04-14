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
from utils.cache_utils import load_file_list_cache, sync_files_cache
from components import VideoFolder, SilverTopAppBar
Builder.load_file(os.path.join(os.path.dirname(__file__), 'videofolderscreen.kv'))


class VideoFolderScreen(MDScreen):
    folders = DictProperty()
    ''' Display the  videos according to the folders they belong to'''
    VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi')
    def _find_index_in_motion_filter(self, type_id, widget):
        return super()._find_index_in_motion_filter(type_id, widget)
    def find_videos(self, interval):
        Thread(target=self._scan_videos, daemon=True).start()

    def _scan_videos(self):
        app = MDApp.get_running_app()
        paths = getattr(app.root, 'system_storage', [])
        videos = sync_files_cache('video_files', paths, self.VIDEO_EXTENSIONS)
        folders = self._build_folder_index(videos)
        Clock.schedule_once(partial(self._on_scan_complete, videos, folders), 0)

    def _build_folder_index(self, videos):
        folders = {}
        for vid in videos:
            dirs = os.path.dirname(vid).split(os.sep)[-1]
            if dirs in folders:
                continue
            metadata = {}
            metadata['files'] = [os.path.join(os.path.dirname(vid), filename)
                                 for filename in os.listdir(os.path.dirname(vid))
                                 if self.check_video(filename)]
            metadata['count'] = len(metadata['files'])
            folders[dirs] = metadata
        return folders

    def _on_scan_complete(self, videos, folders, interval):
        self.videos = videos
        self.folders = folders
        self.update(interval)
        Thread(target=self.create_thumb_pic, daemon=True).start()

    def on_enter(self, *args):
        Logger.info('Finding Images')
        self.load_cached_videos()
        if not self.folders:
            Clock.schedule_once(self.find_videos, 1)

    def load_cached_videos(self):
        cached = load_file_list_cache('video_files')
        if not cached:
            return

        videos = [path for path in cached.keys() if os.path.exists(path) and self.check_video(path)]
        if not videos:
            return

        videos.sort()
        folders = self._build_folder_index(videos)
        self._on_scan_complete(videos, folders, 0)

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

    def _find_cached_thumbnail(self, file_path, thumb_dir):
        if not file_path or not os.path.isdir(thumb_dir):
            return None

        basename = os.path.splitext(os.path.basename(file_path))[0]
        for candidate in os.listdir(thumb_dir):
            if candidate.startswith(basename) and candidate.lower().endswith('.png'):
                candidate_path = os.path.join(thumb_dir, candidate)
                if os.path.exists(candidate_path):
                    return candidate_path
        return None

    def on_folders(self, *args):
        #Clock.schedule_once(self.update, 1)
        pass 
    def create_thumb_pic(self):
        thumb_dir = self.get_thumb_dir()
        os.makedirs(thumb_dir, exist_ok=True)

        for filename in self.videos:
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
                expected_thumb = self._find_cached_thumbnail(first_file, thumb_dir)
                data['folder_collect_thumb'] = expected_thumb or ''
            else:
                data['folder_collect_thumb'] = ''
            data['files'] = count['files']
            self.ids.rv.data.append(data)
        
    
            
