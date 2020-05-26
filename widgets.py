from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivy.lang import Builder
import sys


class VilkaWidget(ButtonBehavior, BoxLayout):
    value_str = StringProperty()
    commands_pari_str = StringProperty()
    champ_pari_str = StringProperty()
    commands_xbet_str = StringProperty()
    champ_xbet_str = StringProperty()
    points = StringProperty()
    kf_pari = StringProperty()
    kf_xbet = StringProperty()
    time = StringProperty()

    def __init__(self, vilka, calculator):
        super().__init__()
        self.vilka = vilka
        self.calculator = calculator

    def refresh(self):
        self.value_str = str(round(self.vilka.value, 2))
        self.commands_pari_str = str(self.vilka.match.event1.command1) + ' - ' + str(self.vilka.match.event1.command2)
        self.champ_pari_str = str(self.vilka.match.event1.champ)
        self.commands_xbet_str = str(self.vilka.match.event2.command1) + ' - ' + str(self.vilka.match.event2.command2)
        self.champ_xbet_str = str(self.vilka.match.event2.champ)
        self.points = str(self.vilka.point)
        self.kf_pari = str(self.vilka.kf1)
        self.kf_xbet = str(self.vilka.kf2)
        if self.vilka.time == 'main_time':
            self.time = 'Общее время'
        elif self.vilka.time == '1_time':
            self.time = '1-й тайм'
        elif self.vilka.time == '2_time':
            self.time = '2-й тайм'

    def on_press(self):
        self.calculator.value_str = self.value_str
        self.calculator.commands_pari_str = self.commands_pari_str
        self.calculator.champ_pari_str = self.champ_pari_str
        self.calculator.commands_xbet_str = self.commands_xbet_str
        self.calculator.champ_xbet_str = self.champ_xbet_str
        self.calculator.points = self.points
        self.calculator.kf_pari = self.kf_pari
        self.calculator.kf_xbet = self.kf_xbet
        self.calculator.time = self.time
        self.calculator.calculate()


    with open("vilkawidget.kv", encoding='utf8') as f:
        Builder.load_string(f.read())