from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.properties import ListProperty, DictProperty
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.lang import Builder
import os
from threading import Thread

from utils import create_thumbnail
from components import VideoFolder, SilverTopAppBar
Builder.load_file(os.path.join(os.path.dirname(__file__), 'videofolderscreen.kv'))


class VideoFolderScreen(MDScreen):
    folders = DictProperty()
    ''' Display the  videos according to the folders they belong to'''
    def _find_index_in_motion_filter(self, type_id, widget):
        return super()._find_index_in_motion_filter(type_id, widget)
    def find_videos(self, interval):
        app = MDApp.get_running_app()
        paths = app.root.system_storage
        self.videos = []
        for path in paths:  
            for dirpath, dirname, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.mp4') or filename.endswith('.mkv')  or filename.endswith('.avi'):
                        self.videos.append(os.path.join(dirpath, filename))

        for vid in self.videos:
            dirs = os.path.dirname(vid).split(os.sep)[-1]
            if dirs in self.folders:
                pass
            else:
                metadata = {}
                metadata['files'] = [os.path.join(os.path.dirname(vid), filename) for filename in os.listdir(os.path.dirname(vid)) if self.check_video(filename)]
                metadata['count'] = len(os.listdir(os.path.dirname(vid)))
                self.folders[dirs] =  metadata
        Clock.schedule_once(self.update, 1)
        Thread(target=self.create_thumb_pic, args=()).start()

        
        

    def on_enter(self, *args):
        Logger.info('Finding Images')
        if not self.folders:
            Clock.schedule_once(self.find_videos, 1)

    def check_video(self, filename):
        if filename.endswith('.mp4') or filename.endswith('.mkv')  or filename.endswith('.avi'):
            return True
        else:
            return False

    def on_folders(self, *args):
        #Clock.schedule_once(self.update, 1)
        pass 
    def create_thumb_pic(self):
        for filename in self.videos:
            name = f'{os.path.splitext(filename)[0]}.png'
            if name in os.listdir('assests/thumbs'):
                #the thumbnail was already created
                pass
            else:
                if os.path.exists(filename):
                    try:
                        create_thumbnail(filename, output_dir='assests/thumbs')
                    except Exception as e:
                        Logger.error(e)

    def update(self, interval):
        for folder, count in self.folders.items():
            data = {}
            data['foldername'] = folder
            data['vid_count'] = f"{count['count']} videos"
            data['folder_collect_thumb'] = 'assests/thumbs/rihanna.png'
            data['files'] = count['files']
            self.ids.rv.data.append(data)
        
    
            
