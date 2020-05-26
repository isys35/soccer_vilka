# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from threading import Thread
from parsers import ParserGui
from kivy.properties import StringProperty


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
    time = StringProperty()

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


if __name__ == '__main__':
    app = MainApp()
    app.run()
    app.parser.stop()




