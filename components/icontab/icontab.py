from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivy.lang import Builder
import os
Builder.load_file(os.path.join(os.path.dirname(__file__), 'icontab.kv'))

class IconTab(MDFloatLayout, MDTabsBase):
    pass