import requests
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3


def differ():
    with open('new_names.html', 'w', encoding='utf-8') as output:
        while True:
            try:
                response = requests.get(
                    f'https://blog.counter-strike.net/index.php/category/updates/page/1/',
                )
            except (requests.exceptions.RequestException, urllib3.exceptions.RequestError) as e:
                sleep(10)
                continue
            break
        recent_post = BeautifulSoup(response.text, features='lxml')
        recent_post = recent_post.find("div", "inner_post").getText()
        cached_id = recent_post.split('\n')[1]
        url = 'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/master/csgo/resource/csgo_english.txt'
        old_file = open('old_names.txt', 'w', encoding='utf-8')
        while True:
            try:
                response = requests.get(url)
            except (requests.exceptions.RequestException, urllib3.exceptions.RequestError, urllib3.exceptions.HTTPError) as e:
                sleep(5)
                continue
            break
        old_file.write(response.text)
        old_file.close()
        url_items = 'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/master/csgo/scripts/items/items_game.txt'
        old_items = open('old_items.txt', 'w', encoding='utf-8')
        while True:
            try:
                response = requests.get(url_items)
            except (requests.exceptions.RequestException, urllib3.exceptions.RequestError, urllib3.exceptions.HTTPError) as e:
                sleep(5)
                continue
            break
        old_items.write(response.text)
        old_items.close()
        old_file = open('old_names.txt', 'r', encoding='utf-8')
        print('Starting patch -', cached_id)
        while True:
            sleep(5)
            print(f'{datetime.now().strftime("%H:%M:%S")} | Checking ...')
            while True:
                try:
                    response = requests.get(
                        f'https://blog.counter-strike.net/index.php/category/updates/page/1/',
                    )
                except (requests.exceptions.RequestException, urllib3.exceptions.RequestError) as e:
                    sleep(10)
                    continue
                break
            recent_post = BeautifulSoup(response.text, features='lxml')
            recent_post = recent_post.find("div", "inner_post").getText()
            if recent_post.split('\n')[1] != cached_id:
                cached_id = recent_post.split('\n')[1]
                print(f'{datetime.now().strftime("%H:%M:%S")} | {cached_id}')
                break

        for _ in range(10):
            current_names = open('current_names.txt', 'w', encoding='utf-8')
            while True:
                try:
                    response = requests.get(url)
                except (requests.exceptions.RequestException, urllib3.exceptions.RequestError) as e:
                    sleep(5)
                    continue
                break
            current_names.write(response.text)
            current_names.close()
            current_names = open('current_names.txt', 'r', encoding='utf-8')
            current_names = current_names.readlines()

            current_items = open('current_items.txt', 'w', encoding='utf-8')
            while True:
                try:
                    response = requests.get(url_items)
                except (requests.exceptions.RequestException, urllib3.exceptions.RequestError, urllib3.exceptions.HTTPError) as e:
                    sleep(5)
                    continue
                break
            current_items.write(response.text)
            current_items.close()

            for line in old_file.readlines():
                try:
                    i = current_names.index(line)
                except ValueError:
                    continue
                del current_names[i]

            items = []
            for line in current_names:
                if line.count('"') == 4:
                    ri = line.rindex('"')
                    li = line[:ri].rfind('"')
                    lli = line[:li].find('"')
                    rri = line[:li].rfind('"')
                    if ('CSGO_crate_community' not in line[lli + 1:rri] and 'StickerKit' not in line[lli + 1:rri]) or 'desc' in line[lli + 1:rri]:
                        continue
                    if 'CSGO_crate_community' in line[lli + 1:rri]:
                        items.insert(0, f'{line[li + 1:ri]}')
                    else:
                        items.append(f'Sticker | {line[li + 1:ri]}')
            if items:
                break

        if not items:
            output.write('')
            return items
        ind = 0
        while 'Case' in items[ind] and '|' not in items[ind]:
            output.write(f'<p><a href="https://steamcommunity.com/market/listings/730/{items[ind]}">{items[ind]}\t</a></p>')
            ind += 1
            if ind == len(items):
                break
        if 1 < len(items) != ind:

            def validate(x):
                if x.count('|') == 2:
                    if ')' in x:
                        x = x[x.find('|') + 2:x.find('(')] + x[x.rfind('|'):]
                    else:
                        x = x[x.find('|') + 2:]
                else:
                    if ')' in x:
                        x = x[x.find('|') + 2:x.find(' (')]
                    else:
                        x = x[x.find('|') + 2:]
                return x

            items = items[:ind] + sorted(items[ind:], key=lambda x: validate(x))
        if ind == len(items):
            return items
        prev_item = items[ind]
        output.write(f'<p><a href="https://steamcommunity.com/market/listings/730/{prev_item}">{prev_item}\t</a>')
        for item in items[items.index(prev_item) + 1:]:
            def validate(x):
                if x.count('|') == 2:
                    if ')' in x:
                        x = x[x.find('|') + 2:x.find('(')] + x[x.rfind('|'):]
                    else:
                        x = x[x.find('|') + 2:]
                else:
                    if ')' in x:
                        x = x[x.find('|') + 2:x.find(' (')]
                    else:
                        x = x[x.find('|') + 2:]
                return x

            if validate(prev_item) == validate(item):
                output.write(f'......<a href="https://steamcommunity.com/market/listings/730/{item}">{item[item.find("(") + 1:item.find(")")]}</a>')
            else:
                output.write(f'<p><a href="https://steamcommunity.com/market/listings/730/{item}">{item}\t</a>')
            prev_item = item
        print(f'{datetime.now().strftime("%H:%M:%S")} | {len(items)} New Items Added')
        return items


if __name__ == '__main__':
    differ()
