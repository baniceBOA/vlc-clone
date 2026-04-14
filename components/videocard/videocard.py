from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import Snackbar
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
        try:
            if not self.source or not os.path.exists(self.source):
                raise FileNotFoundError(f"Video file not found: {self.source}")

            app = MDApp.get_running_app()
            player = app.root.screen_manager.get_screen('player')
            player.source = self.source
            player.title = self.filename
            player.thumb = self.thumb
            try:
                player.ids.video.preview = self.thumb
            except Exception:
                pass

            if app.root.screen_manager.current != 'player':
                app.root.screen_manager.current = 'player'
            if hasattr(app.root, 'ids') and app.root.ids.get('bottom_bar'):
                try:
                    app.root.remove_widget(app.root.ids.bottom_bar)
                except Exception:
                    pass
        except Exception as exc:
            print(f"Video playback failed for {self.source}: {exc}")
            Snackbar(
                text=f"Cannot play video: {exc}",
                duration=4,
            ).open()

