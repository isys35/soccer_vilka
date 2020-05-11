# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.core.window import Window
from threading import Thread
import time
from parsers import ParserGui
from kivy.properties import StringProperty
import sys


Window.size = (820, 1000)


class Container(BoxLayout):
    pass


class Calculactor(BoxLayout):
    pass


with open("Main.kv", encoding='utf8') as f:
    presentation = Builder.load_string(f.read())


class MainApp(App):
    def __init__(self):
        super().__init__()
        self.parser = ParserThread(self)
        self.parser.start()

    def build(self):
        return presentation


class ParserThread(Thread):
    def __init__(self, app):
        super().__init__()
        self.parser = ParserGui(app)

    def run(self):
        self.parser.run()

# class AppParser(Thread):
#     def __init__(self, app, parser):
#         super().__init__()
#         self.app = app
#         self.parser = parser
#
#     def run(self):
#         while True:
#             if self.app.root:
#                 vilki_new = self.parser.parser.vilki
#                 if vilki_new:
#                     vilki_widgets_old = self.app.root.ids.box.children
#                     vilki_old = [widget.vilka for widget in vilki_widgets_old]
#                     for vilka_id in range(len(vilki_old)):
#                         if vilki_old[vilka_id] not in vilki_new:
#                             self.app.root.ids.box.remove_widget(vilki_widgets_old[vilka_id])
#                     for vilka in vilki_new:
#                         if vilka not in vilki_old:
#                             self.app.root.ids.box.add_widget(VilkaWidget(vilka))
#                     for vilka_widget in self.app.root.ids.box.children:
#                         vilka_widget.refresh()
            # event1 = Event(Pari(), 'чемпионат', 'тигры', 'волки', 4, 5, [1, 3], [3, 2], 412414214)
            # event2 = Event(Xbet(), 'чемпионат', 'Tigers', 'Wolf', 4, 5, [1, 3], [3, 2], 412414214)
            # match = Match(event1, event2)
            # match.vilki = [Vilka(match, '2_time', 3, 'total'),
            #                Vilka(match, '2_time', 5, 'total'),
            #                Vilka(match, '2_time', 6, 'total')]
            # vilki = match.vilki
            # vilki[0].value = 13
            # vilki[1].value = 3
            # vilki[2].value = 1
            # vilka_widget = VilkaWidget(vilki[0])
            # vilka_widget.refresh()
            # if self.app.root:
            #     online_vilki = [widget.vilka for widget in self.app.root.ids.box.children]
            #     if vilka_widget.vilka not in online_vilki:
            #         self.app.root.ids.box.add_widget(vilka_widget)
            #     print(vilka_widget.vilka)
            # time.sleep(5)


if __name__ == '__main__':
    app = MainApp()
    app.run()




