from bs4 import BeautifulSoup
import requests
import sys
from threading import Thread
from widgets import VilkaWidget

# изучить регулярные выражения и поправить


def save_page(html, file_name):
    with open(file_name, 'w', encoding='utf8') as html_file:
        html_file.write(html)


class Bookmaker:
    SPORTS = {'Фут-зал': None}

    def __init__(self):
        self.name = str()
        self.main_page = str()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
        }
        self.sport = None
        self.events = list()

    def get_response(self, url):
        # print(url, self.headers)
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response
        else:
            print(response.status_code)
            print(response.text)
            sys.exit()

    def update_sport(self):
        with open('initial_data', encoding='utf8') as txt:
            sport = txt.read()
            if sport not in self.SPORTS:
                print('"{}" - данный спорт не найден'.format(sport))
                sys.exit()
            self.sport = sport

    def show_events(self):
        for event in self.events:
            event.show_event()

    def get_events(self):
        return self.events

    def update_events(self):
        events_objs = self.get_events()
        for event_new in events_objs:
            if event_new in self.events:
                self.events[self.events.index(event_new)].total_score1 = event_new.total_score1
                self.events[self.events.index(event_new)].total_score2 = event_new.total_score2
                self.events[self.events.index(event_new)].scores_1 = event_new.scores_1
                self.events[self.events.index(event_new)].scores_2 = event_new.scores_2
            else:
                self.events.append(event_new)
        for event_old in self.events:
            if event_old not in events_objs:
                self.events.remove(event_old)

    def __str__(self):
        return self.name


class Pari(Bookmaker):
    SPORTS = {'Фут-зал': 'foothall'}

    def __init__(self):
        super().__init__()
        self.update_sport()
        self.name = 'париматч'
        self.main_page = 'http://ru.parimatch.com/'

    def get_events(self):
        url = self.main_page + 'live_as.html?curs=0&curName=$&shed=0'
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')
        sport = soup.select_one('.sport.{}'.format(self.SPORTS[self.sport]))
        if not sport:
            return []
        champs = sport.select('.sport.item')
        champs_dict = {}
        for champ in champs:
            champs_dict[champ.select_one('a')['id']] = champ.text
        events = sport.select('.subitem')
        events_objs = []
        for event in events:
            name_block = event.select('.td_n')
            champ = champs_dict[event['id'].replace('Item', '')]
            for match in name_block:
                href = match.select('a')[0]['href']
                score_full = match.select('.score')[0].text
                if not score_full:
                    continue
                commands = match.text.replace(score_full, '').strip()
                command1 = commands.split(' - ')[0].strip()
                command2 = commands.split(' - ')[1].strip()
                total_score1 = int(score_full.split('(')[0].split('-')[0])
                total_score2 = int(score_full.split('(')[0].split('-')[-1])
                score_sets = score_full.split('(')[1].replace(')', '')
                scores_1 = [int(el.split('-')[0]) for el in score_sets.split(',')]
                scores_2 = [int(el.split('-')[1]) for el in score_sets.split(',')]
                event_info = Event(bookmaker=self,
                                   champ=champ,
                                   command1=command1,
                                   command2=command2,
                                   total_score1=total_score1,
                                   total_score2=total_score2,
                                   scores_1=scores_1,
                                   scores_2=scores_2,
                                   index=href.split('=')[-1])
                events_objs.append(event_info)
        return events_objs

    def get_totals(self, index):
        url = self.main_page + 'live_ar.html?hl=' + str(index) + '&hl=' + str(index) + ',&curs=0&curName=$'
        totals = {}
        response = self.get_response(url)
        #save_page(response.text, str(index) + 'pari_event.html')
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.select_one('.twp')
        thead = table.select_one('tr')
        table_headers = thead.select('th')
        row1 = soup.select('.row1')
        td_row1 = row1[0].select('td')
        id_total = None
        id_individ = None
        if len(table_headers) == len(td_row1):
            totals['main_time'] = {}
            for table_header_id in range(len(table_headers)):
                if 'title' in table_headers[table_header_id].attrs:
                    if table_headers[table_header_id]['title'] == 'Тотал матча':
                        id_total = table_header_id
                        totals['main_time']['total'] = {float(td_row1[table_header_id].text):
                                                            {'more': float(td_row1[table_header_id + 1].text),
                                                             'smaller': float(td_row1[table_header_id + 2].text)}}
                    if table_headers[table_header_id]['title'] == 'Индивидуальный тотал':
                        id_individ = table_header_id
                        points = td_row1[table_header_id].select('b')
                        more_koef = td_row1[table_header_id + 1].select('u')
                        smaller_koef = td_row1[table_header_id + 2].select('u')
                        totals['main_time']['individ_total_1'] = {float(points[0].text):
                                                                      {'more': float(more_koef[0].text),
                                                                       'smaller': float(smaller_koef[0].text)}}
                        totals['main_time']['individ_total_2'] = {float(points[1].text):
                                                                      {'more': float(more_koef[1].text),
                                                                       'smaller': float(smaller_koef[1].text)}}
        bk_row1_prop = row1[1].select('.bk')
        time_2_info = None
        for time_info in bk_row1_prop:
            tds_text = [td.text for td in time_info.select('td')]
            if '2-й тайм:' in tds_text:
                time_2_info = time_info
                break
        if time_2_info:
            totals['2_time'] = {}
            td_2_time = time_2_info.select('td')
            if id_total:
                totals['2_time']['total'] = {float(td_2_time[id_total].text):
                                                            {'more': float(td_2_time[id_total + 1].text),
                                                             'smaller': float(td_2_time[id_total + 2].text)}}
        return totals

    def get_status_game(self, index):
        url = self.main_page + 'live_ar.html?hl=' + str(index) + '&hl=' + str(index) + ',&curs=0&curName=$'
        response = self.get_response(url)
        if 'Прием ставок live в выбранных Вами матчах завершен. Пожалуйста, сделайте новый выбор' in response.text:
            return False
        else:
            return True


class Xbet(Bookmaker):
    SPORTS = {'Фут-зал': 1}

    def __init__(self):
        super().__init__()
        self.update_sport()
        self.name = '1xbet'
        self.main_page = 'https://1xstavka.ru/'

    def get_events(self):
        url = self.main_page + 'LiveFeed/BestGamesExtVZip?sports={}&count=10&antisports=188&partner=51&getEmpty=true&mode=4&country=22'.format(
            self.SPORTS[self.sport])
        response = self.get_response(url)
        data = response.json()
        events_objs = []
        for event in data['Value']:
            index = event['I']
            champ = event['L']
            if 'O1' not in event or 'O2' not in event:
                continue
            command1 = event['O1']
            command2 = event['O2']
            if not event['SC']['FS']:
                continue
            if 'S1' in event['SC']['FS']:
                total_score1 = event['SC']['FS']['S1']
            else:
                total_score1 = 0
            if 'S2' in event['SC']['FS']:
                total_score2 = event['SC']['FS']['S2']
            else:
                total_score2 = 0
            scores_1 = []
            for sc in event['SC']['PS']:
                if 'S1' in sc['Value']:
                    scores_1.append(sc['Value']['S1'])
                else:
                    scores_1.append(0)
            scores_2 = []
            for sc in event['SC']['PS']:
                if 'S2' in sc['Value']:
                    scores_2.append(sc['Value']['S2'])
                else:
                    scores_2.append(0)
            timer = event['SC']['TS']
            event_info = Event(bookmaker=self,
                               champ=champ,
                               command1=command1,
                               command2=command2,
                               total_score1=int(total_score1),
                               total_score2=int(total_score2),
                               scores_1=scores_1,
                               scores_2=scores_2,
                               index=index,
                               time=timer)
            events_objs.append(event_info)
        return events_objs

    @staticmethod
    def get_id_2_time(data):
        if 'SG' in data['Value']:  # проверяем, есть ли выбор тайма
            selecter_time = data['Value']['SG']
            for time in selecter_time:
                if 'PN' in time:
                    if time['PN'] == '2-й Тайм':
                        time_2_id = time['I']
                        return time_2_id

    @staticmethod
    def get_totals_from_json(data):
        totals = {}
        for kf in data['Value']['GE']:
            if kf['G'] == 4:
                totals['total'] = {}
                for total_jsn in kf['E'][0]:
                    totals['total'][total_jsn['P']] = {'more': total_jsn['C']}
                for total_jsn in kf['E'][1]:
                    totals['total'][total_jsn['P']]['smaller'] = total_jsn['C']
            if kf['G'] == 5:
                totals['individ_total_1'] = {}
                for total_jsn in kf['E'][0]:
                    totals['individ_total_1'][total_jsn['P']] = {'more': total_jsn['C']}
                for total_jsn in kf['E'][1]:
                    totals['individ_total_1'][total_jsn['P']]['smaller'] = total_jsn['C']
            if kf['G'] == 6:
                totals['individ_total_2'] = {}
                for total_jsn in kf['E'][0]:
                    totals['individ_total_2'][total_jsn['P']] = {'more': total_jsn['C']}
                for total_jsn in kf['E'][1]:
                    totals['individ_total_2'][total_jsn['P']]['smaller'] = total_jsn['C']
        return totals

    def get_totals(self, index):
        url = 'https://1xstavka.ru/LiveFeed/GetGameZip?id={}&lng=ru&cfview=0&isSubGames=true&GroupEvents=true' \
              '&allEventsGroupSubGames=true&countevents=250&partner=51&grMode=2'
        totals = {}
        main_time_url = url.format(index)
        response = self.get_response(main_time_url)
        data_main_time = response.json()
        try:
            totals['main_time'] = self.get_totals_from_json(data_main_time)
        except TypeError:
            print(data_main_time)
            sys.exit()
        time_2_id = self.get_id_2_time(data_main_time)
        if time_2_id:
            url_2_time = url.format(time_2_id)
            response = self.get_response(url_2_time)
            data_time_2 = response.json()
            totals['2_time'] = self.get_totals_from_json(data_time_2)
        return totals


class Event:
    def __init__(self, bookmaker,
                 champ,
                 command1,
                 command2,
                 total_score1,
                 total_score2,
                 scores_1,
                 scores_2,
                 index,
                 time=None):
        self.bookmaker = bookmaker
        self.champ = champ
        self.command1 = command1
        self.command2 = command2
        self.total_score1 = total_score1
        self.total_score2 = total_score2
        self.scores_1 = scores_1
        self.scores_2 = scores_2
        self.time = time
        self.index = index
        self.totals = {}

    def __eq__(self, other):
        if isinstance(other, Event):
            return (self.bookmaker == other.bookmaker and
                    self.champ == other.champ and
                    self.command1 == other.command1 and
                    self.command2 == other.command2 and
                    self.index == other.index)
        return NotImplemented

    def show_event(self):
        print('*****Cобытие*****')
        print('Букмекер: ' + self.bookmaker.name)
        print('Чемпионат: ' + self.champ)
        print('Команда 1: ' + self.command1)
        print('Команда 2: ' + self.command2)
        print('Счёт по таймам: {} {}'.format(self.scores_1, self.scores_2))
        print('Общий счёт: {} {}'.format(self.total_score1, self.total_score2))

    def update_totals(self):
        self.totals = self.bookmaker.get_totals(self.index)


class Match:
    def __init__(self, event1, event2):
        self.event1 = event1
        self.event2 = event2
        self.vilki = []
        self.status_in_play = True

    def __eq__(self, other):
        if isinstance(other, Match):
            return (self.event1 == other.event1 and
                    self.event2 == other.event2)
        return NotImplemented

    def show_match(self):
        print('*****Cовпадение*****')
        print('URL {}: {}'.format(self.event1.bookmaker, self.event1.bookmaker.main_page + 'bet.html?hl=' + self.event1.index))
        print('URl {}: {}')
        print('Букмекер: {} ---------- {} '.format(self.event1.bookmaker, self.event2.bookmaker))
        print('Чемпионат: {} ---------- {} '.format(self.event1.champ, self.event2.champ))
        print('Команда 1: {} ---------- {} '.format(self.event1.command1, self.event2.command1))
        print('Команда 2: {} ---------- {} '.format(self.event1.command2, self.event2.command2))
        print('Счёт по таймам: {} {}  ---------- {} {}'.format(self.event1.scores_1,
                                                               self.event1.scores_2,
                                                               self.event2.scores_1,  # уменьшить обЪём
                                                               self.event2.scores_2))
        print('Общий счёт: {} {} ---------- {} {}'.format(self.event1.total_score1,
                                                          self.event1.total_score2,
                                                          self.event2.total_score1,
                                                          self.event2.total_score2))

    def show_match_totals(self):
        print('{}  {}'.format(self.event1.bookmaker, self.event1.totals))
        print('{}  {}'.format(self.event2.bookmaker, self.event2.totals))

    def update_totals(self):
        self.event1.update_totals()
        self.event2.update_totals()

    def update_status(self):
        if not self.event1.bookmaker.get_status_game(self.event1.index):
            self.status_in_play = False

    def update_vilki(self):
        totals1 = self.event1.totals
        totals2 = self.event2.totals
        time = 'main_time'
        vilka_new = []
        if time in totals1 and time in totals2:
            print(totals1[time])
            print(totals2[time])
            total_type = 'total'
            if total_type in totals1[time] and total_type in totals2[time]:
                for point_event1 in totals1[time][total_type]:
                    for point_event2 in totals2[time][total_type]:
                        if point_event1 == point_event2:
                            vilka = Vilka(self, time, point_event1, total_type)
                            vilka_new.append(vilka)
        for vilka in vilka_new:
            if vilka in self.vilki:
                self.vilki[self.vilki.index(vilka)].update_vilka()
            else:
                self.vilki.append(vilka)
        for vilka in self.vilki:
            if vilka not in vilka_new:
                self.vilki.remove(vilka)


class Vilka:
    def __init__(self, match, time, point, total_type):
        self.koef = None
        self.value = None
        self.kf1 = None
        self.kf2 = None
        self.match = match
        self.time = time
        self.point = point
        self.total_type = total_type
        self.update_vilka()

    def __eq__(self, other):
        if isinstance(other, Vilka):
            return (self.match == other.match and
                    self.time == other.time and
                    self.point == other.point and
                    self.total_type == other.total_type)
        return NotImplemented

    def update_vilka(self):
        self.kf1 = self.match.event1.totals[self.time][self.total_type][self.point]['more']
        self.kf2 = self.match.event2.totals[self.time][self.total_type][self.point]['smaller']
        self.koef = 1/self.kf1 + 1/self.kf2
        self.value = 100*(1-self.koef)
        print(self.point)
        print(self.koef)
        print(self.value)


# поразмыслить над неймингом
class Parser:
    def __init__(self):
        self.boookmekers = [Pari(), Xbet()]
        self.matches = []
        self.vilki = []

    def run(self):
        while True:
            for bookmaker in self.boookmekers:
                bookmaker.update_events()
                bookmaker.show_events()
                self.update_match()
                print(self.matches)

    def update_match(self):
        # print('Обновление одинаковых матчей')
        for event_1 in self.boookmekers[0].events:
            for event_2 in self.boookmekers[1].events:
                if event_1.scores_1 == event_2.scores_1 and event_1.scores_2 == event_2.scores_2:
                    match = Match(event_1, event_2)
                    #match.show_match()
                    if match not in self.matches:
                        self.matches.append(match)
        for match in self.matches:
            match.update_status()
            if not match.status_in_play:
                self.matches.remove(match)
        for match in self.matches:
            match.update_totals()
            # match.show_match_totals()

    def update_vilki(self):
        self.vilki = []
        for match in self.matches:
            self.vilki.extend(match.vilki)


class ParserGui(Parser):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def run(self):
        while True:
            if self.app.root:
                for bookmaker in self.boookmekers:
                    print('Букмекер {}: получение событий'.format(str(bookmaker)))
                    bookmaker.update_events()
                    print('Букмекер {}: {} событий'.format(str(bookmaker), str(len(bookmaker.events))))
                print('Поиск совпадений')
                self.update_match()
                print('{} совпадений'.format(str(len(self.matches))))
                print('Получение коэффициентов для совпадений')
                for match in self.matches:
                    match.update_totals()
                print('Поиск вилок')
                for match in self.matches:
                    match.update_vilki()
                vilki = [vilka for match in self.matches for vilka in match.vilki]
                print('Найдено {} вилок'.format(len(vilki)))
                if vilki:
                    print('Обновление виджетов')
                    self.update_widgets(vilki)

    def update_widgets(self, vilki):
        for vilka in vilki:
            if vilka not in [widget.vilka for widget in self.app.root.ids.box.children]:
                vilka_widget = VilkaWidget(vilka)
                self.app.root.ids.box.add_widget(vilka_widget)
        for widget in self.app.root.ids.box.children:
            if widget.vilka not in vilki:
                self.app.root.ids.box.remove_widget(widget)
                continue
            widget.refresh()

    def update_match(self):
        for event_1 in self.boookmekers[0].events:
            for event_2 in self.boookmekers[1].events:
                if event_1.scores_1 == event_2.scores_1 and event_1.scores_2 == event_2.scores_2:
                    match = Match(event_1, event_2)
                    # match.show_match()
                    if match not in self.matches:
                        self.matches.append(match)
        for match in self.matches:
            match.update_status()
            if not match.status_in_play:
                self.matches.remove(match)

if __name__ == '__main__':
    app = Parser()
    app.run()