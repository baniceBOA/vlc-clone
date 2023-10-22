from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase
from kivy.lang import Builder
import os
Builder.load_file(os.path.join(os.path.dirname(__file__), 'screentab.kv'))

class ScreenTab(MDBoxLayout, MDTabsBase):
    pass