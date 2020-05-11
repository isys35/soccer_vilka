from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.lang import Builder


class VilkaWidget(BoxLayout):
    value_str = StringProperty()
    commands_pari_str = StringProperty()
    champ_pari_str = StringProperty()
    commands_xbet_str = StringProperty()
    champ_xbet_str = StringProperty()
    points = StringProperty()
    kf_pari = StringProperty()
    kf_xbet = StringProperty()

    def __init__(self, vilka):
        super().__init__()
        self.vilka = vilka

    def refresh(self):
        self.value_str = str(round(self.vilka.value, 2))
        self.commands_pari_str = str(self.vilka.match.event1.command1) + ' - ' + str(self.vilka.match.event1.command2)
        self.champ_pari_str = str(self.vilka.match.event1.champ)
        self.commands_pari_str = str(self.vilka.match.event2.command1) + ' - ' + str(self.vilka.match.event2.command2)
        self.champ_pari_str = str(self.vilka.match.event2.champ)
        self.points = str(self.vilka.point)
        self.kf_pari = str(self.vilka.kf1)
        self.kf_xbet = str(self.vilka.kf2)

    with open("vilkawidget.kv", encoding='utf8') as f:
        Builder.load_string(f.read())