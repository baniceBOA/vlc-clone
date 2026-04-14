from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineIconListItem, IconLeftWidget
from kivymd.uix.bottomsheet import MDBottomSheet, MDBottomSheetDragHandle, MDBottomSheetDragHandleTitle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.snackbar import Snackbar
from kivymd.app import MDApp
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from ..MinimalAudioplayer import MinimalAudioPlayer
from utils.get_audio_metadata import get_audio_metadata
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'audiofileview.kv'))

class AudioFileView(TwoLineAvatarIconListItem):
    file_path = StringProperty()
    player = ObjectProperty(None)
    min_player = ObjectProperty(None)
    open_blocked = BooleanProperty(False)
    dialog = None

    def on_release(self):
        if self.open_blocked:
            self.open_blocked = False
            return
        self.open_audio_player()

    def open_audio_player(self):
        app = MDApp.get_running_app()
        if not app or not hasattr(app.root, 'screen_manager'):
            return

        app.current_audio = self
        try:
            app.root.screen_manager.current = 'audioscreen'
        except Exception:
            pass

        if self.player and getattr(self.player, 'state', None) == 'play':
            return

        self.player = SoundLoader.load(self.file_path)
        if not self.player:
            Snackbar(text='Unable to load audio file.').open()
            return

        if self.min_player and self.min_player.parent:
            self.min_player.parent.remove_widget(self.min_player)

        self.min_player = MinimalAudioPlayer(filename=self.file_path, pos_hint={'bottom': 0.9})
        self.min_player.min_player_btn.bind(on_release=self.pause_play)
        try:
            audio_screen = app.root.screen_manager.get_screen('audioscreen')
            audio_screen.add_widget(self.min_player)
        except Exception:
            pass

        self.player.play()
        self.min_player.min_player_btn.icon = 'pause-circle-outline'

    def pause_play(self, instance):
        if not self.player:
            return
        if self.player.state == 'play':
            self.player.stop()
            instance.icon = 'play-circle-outline'
        else:
            self.player.play()
            instance.icon = 'pause-circle-outline'

    def show_options(self, *args):
        self.open_blocked = True
        self.bottom_sheet = MDBottomSheet(type='standard')
        content = MDBoxLayout(
            orientation='vertical',
            spacing='8dp',
            padding='12dp',
            adaptive_height=True,
        )

        content.add_widget(MDBottomSheetDragHandle())
        content.add_widget(
            MDBottomSheetDragHandleTitle(
                text='Audio options',
                halign='center',
                size_hint_y=None,
                height='32dp',
            )
        )

        def add_option(title, icon, callback):
            item = OneLineIconListItem(text=title)
            item.add_widget(IconLeftWidget(icon=icon))
            item.bind(on_release=lambda instance, cb=callback: self._bottom_sheet_action(cb))
            content.add_widget(item)

        add_option('Delete', 'trash-can-outline', self.delete_audio)
        add_option('Add to playlist', 'playlist-music', self.add_to_playlist)
        add_option('Info / Metadata', 'information-outline', self.show_metadata)

        self.bottom_sheet.add_widget(content)
        app = MDApp.get_running_app()
        if app and app.root:
            app.root.add_widget(self.bottom_sheet)
            Clock.schedule_once(lambda dt: self.bottom_sheet.open(), 0)

    def _bottom_sheet_action(self, callback):
        if self.bottom_sheet:
            self.bottom_sheet.dismiss()
            self.bottom_sheet = None
        if callback:
            callback()

    def delete_audio(self):
        try:
            os.remove(self.file_path)
            Snackbar(text='Audio file deleted.').open()
            app = MDApp.get_running_app()
            if app and hasattr(app.root, 'screen_manager'):
                try:
                    audio_screen = app.root.screen_manager.get_screen('audioscreen')
                    if hasattr(audio_screen, 'music'):
                        audio_screen.music = [f for f in audio_screen.music if f != self.file_path]
                        audio_screen.update(0)
                except Exception:
                    pass
        except Exception as exc:
            Snackbar(text=f'Unable to delete file: {exc}').open()

    def add_to_playlist(self):
        app = MDApp.get_running_app()
        playlist = getattr(app, 'user_playlist', [])
        if self.file_path not in playlist:
            playlist.append(self.file_path)
            app.user_playlist = playlist
            Snackbar(text='Added to playlist.').open()
        else:
            Snackbar(text='Already in playlist.').open()

    def show_metadata(self):
        metadata = get_audio_metadata(self.file_path)
        content = [
            f"Title: {metadata.get('title', os.path.basename(self.file_path))}",
            f"Artist: {metadata.get('artist', 'Unknown Artist')}",
            f"Album: {metadata.get('album', 'Unknown Album')}",
            f"Genre: {metadata.get('genre', 'Unknown Genre')}",
            f"Duration: {int(metadata.get('duration', 0))} sec",
            f"Path: {self.file_path}",
        ]
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title='Audio metadata',
            text='\n'.join(content),
            size_hint=(0.8, None),
            buttons=[MDFlatButton(text='CLOSE', on_release=self.close_dialog)],
        )
        self.dialog.open()

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
