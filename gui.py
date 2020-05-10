# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.core.window import Window

Window.size = (820, 1000)


class Container(BoxLayout):
    pass


class Calculactor(BoxLayout):
    pass


class VilkaWidget(BoxLayout):
    pass


with open("Main.kv", encoding='utf8') as f:
    presentation = Builder.load_string(f.read())


class MainApp(App):
    def build(self):
        return presentation




if __name__ == '__main__':
    MainApp().run()




