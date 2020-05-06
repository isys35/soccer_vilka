from bs4 import BeautifulSoup
import requests
import sys


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


class Match:
    def __init__(self, event1, event2):
        self.event1 = event1
        self.event2 = event2

    def __eq__(self, other):
        if isinstance(other, Match):
            return (self.event1 == other.event1 and
                    self.event2 == other.event2)
        return NotImplemented

    def show_match(self):
        print('*****Cовпадение*****')
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


# поразмыслить над неймингом
class MainApp:
    def __init__(self):
        self.boookmekers = [Pari(), Xbet()]
        self.matches = []

    def run(self):
        while True:
            for bookmaker in self.boookmekers:
                bookmaker.update_events()
                bookmaker.show_events()
                self.update_match()

    def update_match(self):
        print('Обновление одинаковых матчей')
        for event_1 in self.boookmekers[0].events:
            for event_2 in self.boookmekers[1].events:
                if event_1.scores_1 == event_2.scores_1 and event_1.scores_2 == event_2.scores_2:
                    match = Match(event_1, event_2)
                    print(match.show_match())
                    if match in self.matches:
                        pass
                    else:
                        self.matches.append(match)


if __name__ == '__main__':
    app = MainApp()
    app.run()
    # xbet.update_events()
    # print(pari.events, xbet.events)
