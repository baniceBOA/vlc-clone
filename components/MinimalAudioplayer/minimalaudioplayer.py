
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.animation import Animation
from kivymd.app import MDApp
from kivy.properties import StringProperty, ObjectProperty
from kivy.lang import Builder
import os
Builder.load_file(os.path.join(os.path.dirname(__file__), 'minimalaudioplayer.kv'))

class MinimalAudioPlayer(MDBoxLayout):
    filename = StringProperty()
    name = StringProperty()
    length = StringProperty('0:00')
    min_player_btn = ObjectProperty()
    def animate_label(self, *args):
        #anim = Animation(width=0, duration=5)
        #anim.repeat=True
        #anim.bind(on_complete=self.animate_reset)
        #anim.start(self.ids.container_label)
        pass
    def on_filename(self, instance, value):
        self.name = value.split(os.sep)[-1]
    def animate_reset(self, *args):
        self.ids.container_label.width = 300
        self.animate_label()



class testApp(MDApp):
    def build(self):
        player = MinimalAudioPlayer(filename='The gospel hit of the year 2023 by the best band in the world', pos_hint={'center_x':0.5, 'center_y':0.5})
        box = MDBoxLayout(orientation='vertical')
        box.add_widget(player)
        return box
    
if __name__ == '__main__':
    testApp().run()