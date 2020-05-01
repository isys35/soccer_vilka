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
        print(url, self.headers)
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


class Pari(Bookmaker):
    SPORTS = {'Фут-зал': 'foothall'}

    def __init__(self):
        super().__init__()
        self.update_sport()
        self.name = 'париматч'
        self.main_page = 'http://ru.parimatch.com/'

    def update_events(self):
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
        events_info = []
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
                event_info = {
                    'id': href.split('=')[-1],
                    'champ': champ,
                    'command1': command1,
                    'command2': command2,
                    'total_score1': total_score1,
                    'total_score2': total_score2,
                    'scores_1': scores_1,
                    'scores_2': scores_2
                }
                events_info.append(event_info)
        self.events = events_info


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


class Xbet(Bookmaker):
    SPORTS = {'Фут-зал': 1}

    def __init__(self):
        super().__init__()
        self.update_sport()
        self.name = '1xbet'
        self.main_page = 'https://1xstavka.ru/'

    def update_events(self):
        url = self.main_page + 'LiveFeed/BestGamesExtVZip?sports={}&count=10&antisports=188&partner=51&getEmpty=true&mode=4&country=22'.format(self.SPORTS[self.sport])
        response = self.get_response(url)
        data = response.json()
        events = []
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
            event_info = {'champ': champ, 'command1': command1, 'command2': command2,
                          'total_score1': int(total_score1), 'total_score2': int(total_score2), 'scores_1': scores_1,
                          'scores_2': scores_2, 'time': timer, 'id': index}
            events.append(event_info)
        self.events = events


if __name__ == '__main__':
    pari = Pari()
    pari.update_events()
    xbet = Xbet()
    xbet.update_events()
    print(pari.events, xbet.events)
