
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.animation import Animation
from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.lang import Builder
import os
Builder.load_file(os.path.join(os.path.dirname(__file__), 'minimalaudioplayer.kv'))

class MinimalAudioplayer(MDBoxLayout):
    filename = StringProperty()
    def animate_label(self):
        anim = Animation(text_size=(20,self.ids.animated_label.height), duration=5)
        anim.start(self.ids.animated_label)



class testApp(MDApp):
    def build(self):
        player = MinimalAudioplayer(filename='The gospel hit of the year 2023 by the best band in the world', pos_hint={'center_x':0.5, 'center_y':0.5})
        box = MDBoxLayout(orientation='vertical')
        box.add_widget(player)
        return box
    
if __name__ == '__main__':
    testApp().run()