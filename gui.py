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
    value_str = StringProperty()
    commands_pari_str = StringProperty()
    champ_pari_str = StringProperty()
    commands_xbet_str = StringProperty()
    champ_xbet_str = StringProperty()
    points = StringProperty()
    kf_pari = StringProperty()
    kf_xbet = StringProperty()
    total_score = StringProperty()

    def calculate(self, *args):
        self.ids.bet1.bind(on_text_validate=self.calculate)
        self.ids.rounder.bind(on_text_validate=self.calculate)
        self.ids.check_box.bind(on_press=self.calculate)
        if not self.ids.check_box.active:
            c2 = round((float(self.ids.bet1.text) * float(self.kf_pari)) / float(self.kf_xbet), int(self.ids.rounder.text))
        else:
            c2 = round(float(self.ids.bet1.text) / (float(self.kf_xbet)-1), int(self.ids.rounder.text))
        self.ids.bet2.text = str(c2)
        self.ids.sum_c.text = str(round(c2+float(self.ids.bet1.text), int(self.ids.rounder.text)))
        self.ids.profit1.text = str(round(float(self.ids.bet1.text) * float(self.kf_pari) - (float(self.ids.bet1.text)+c2), int(self.ids.rounder.text)))
        self.ids.profit2.text = str(
            round(c2 * float(self.kf_xbet) - (float(self.ids.bet1.text) + c2),
                  int(self.ids.rounder.text)))


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

    def stop(self):
        self.parser.stop()

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
    app.parser.stop()




