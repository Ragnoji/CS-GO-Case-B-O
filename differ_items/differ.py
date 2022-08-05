import requests
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3
from re import search


def differ():
    with open('new_names.html', 'w', encoding='utf-8') as output:
        while True:
            try:
                response = requests.get(
                    f'https://github.com/SteamDatabase/GameTracking-CSGO/commits/master',
                )
            except (requests.exceptions.RequestException, urllib3.exceptions.RequestError) as e:
                sleep(10)
                continue
            break

        old_data = BeautifulSoup(response.text, features='lxml')
        old_id = old_data.find("a", "tooltipped tooltipped-sw btn-outline btn BtnGroup-item text-mono f6").getText().strip()
        url = 'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/master/csgo/resource/csgo_english.txt'
        old_file = open('old_names.txt', 'w', encoding='utf-8')
        while True:
            try:
                sleep(1)
                response = requests.get(url)
                if isinstance(response.text, str) and len(response.text) < 1000:
                    continue
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
                sleep(1)
                response = requests.get(url_items)
                if isinstance(response.text, str) and len(response.text) < 1000:
                    continue
            except (requests.exceptions.RequestException, urllib3.exceptions.RequestError, urllib3.exceptions.HTTPError) as e:
                sleep(5)
                continue
            break
        old_items.write(response.text)
        old_items.close()
        old_file = open('old_names.txt', 'r', encoding='utf-8')
        print('Starting commit -', old_id)
        while True:
            sleep(3)
            print(f'{datetime.now().strftime("%H:%M:%S")} | Checking ...', end='')
            while True:
                try:
                    sleep(1)
                    response = requests.get(
                        f'https://github.com/SteamDatabase/GameTracking-CSGO/commits/master',
                    )
                    if isinstance(response.text, str) and len(response.text) < 1000:
                        print('here')
                        continue
                except (requests.exceptions.RequestException, urllib3.exceptions.RequestError) as e:
                    sleep(2)
                    continue
                break

            old_data = BeautifulSoup(response.text, features='lxml')
            current_id = old_data.find("a", "tooltipped tooltipped-sw btn-outline btn BtnGroup-item text-mono f6").getText().strip()
            if current_id != old_id:
                old_id = current_id
                print(f'\n{datetime.now().strftime("%H:%M:%S")} | {old_id}')
                break
            else:
                print(f'Nothing new ({current_id})')

        old_lines = old_file.readlines()
        for _ in range(1):
            current_names = open('current_names.txt', 'w', encoding='utf-8')
            while True:
                try:
                    sleep(1)
                    response = requests.get(url)
                    if isinstance(response.text, str) and len(response.text) < 1000:
                        continue
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
                    sleep(1)
                    response = requests.get(url_items)
                    if isinstance(response.text, str) and len(response.text) < 1000:
                        continue
                except (requests.exceptions.RequestException, urllib3.exceptions.RequestError, urllib3.exceptions.HTTPError) as e:
                    sleep(5)
                    continue
                break
            current_items.write(response.text)
            current_items.close()

            items = []
            for line in current_names:
                if line in old_lines:
                    continue
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


def check_case_update():
    past = ['Prisma 2 Case', 'Prisma Case', 'Fracture Case', 'Danger Zone Case', 'Snakebite Case', 'Horizon Case',
            'CS20 Case', 'Revolver Case', 'Falchion Case', 'Shadow Case', 'Clutch Case', 'Operation Wildfire Case',
            'Chroma 3 Case', 'Spectrum 2 Case', 'Gamma Case', 'Chroma 2 Case', 'Gamma 2 Case',
            'Operation Vanguard Weapon Case', 'Spectrum Case', 'Chroma Case', 'Dreams & Nightmares Case',
            'Operation Phoenix Weapon Case', 'Shattered Web Case', 'Operation Broken Fang Case',
            'Operation Riptide Case', 'Glove Case', 'Operation Breakout Weapon Case', 'eSports 2014 Summer Case',
            'Huntsman Weapon Case', 'Winter Offensive Weapon Case', 'CS:GO Weapon Case 3', 'CS:GO Weapon Case 2',
            'CS:GO Weapon Case', 'eSports 2013 Winter Case', 'Operation Hydra Case', 'eSports 2013 Case',
            'Operation Bravo Case', 'Recoil Case']
    box_name = differ()
    if box_name and 'Case' in box_name[0] and '|' not in box_name[0] and box_name[0] not in past:
        return box_name[0], box_name[1:]
    return False, box_name


def check_case_update_blog(page=1):
    response = requests.get(
        f'https://blog.counter-strike.net/index.php/category/updates/page/{page}/',
    )
    recent_post = BeautifulSoup(response.text, features='lxml')
    recent_post = recent_post.find("div", "inner_post").getText()
    text = search(r'the .*[A-Z].+Case', recent_post)
    if not text:
        text = search(r'The .*[A-Z].+Case', recent_post)
    box_name = False
    if text:
        box_name = text[0]
        box_name = box_name[:box_name.find('Case') + 4]
        box_name = box_name.replace('#038;', '')[4:]
        box_name = box_name.replace(' Weapon', '')
        box_name = ' '.join(filter(lambda w: w[0].isupper() or w[0].isdigit() or w[0] == '&', box_name.split()))
        if box_name.find('Operation') != -1:
            box_name = False

    if not box_name:
        text = search(r'the .*[A-Z].+Collection', recent_post)
        if not text:
            text = search(r'The .*[A-Z].+Collection', recent_post)
        box_name = False
        if text:
            box_name = text[0]
            box_name = box_name[:box_name.find('Collection') - 1]
            box_name += ' Case'
            box_name = box_name.replace('#038;', '')[4:]
            box_name = box_name.replace(' Weapon', '')
            box_name = ' '.join(filter(lambda w: w[0].isupper() or w[0].isdigit() or w[0] == '&', box_name.split()))
            if box_name.find('Operation') != -1:
                box_name = False
    past = ['Prisma 2 Case', 'Prisma Case', 'Fracture Case', 'Danger Zone Case', 'Snakebite Case', 'Horizon Case',
            'CS20 Case', 'Revolver Case', 'Falchion Case', 'Shadow Case', 'Clutch Case', 'Operation Wildfire Case',
            'Chroma 3 Case', 'Spectrum 2 Case', 'Gamma Case', 'Chroma 2 Case', 'Gamma 2 Case',
            'Operation Vanguard Weapon Case', 'Spectrum Case', 'Chroma Case', 'Dreams & Nightmares Case',
            'Operation Phoenix Weapon Case', 'Shattered Web Case', 'Operation Broken Fang Case',
            'Operation Riptide Case', 'Glove Case', 'Operation Breakout Weapon Case', 'eSports 2014 Summer Case',
            'Huntsman Weapon Case', 'Winter Offensive Weapon Case', 'CS:GO Weapon Case 3', 'CS:GO Weapon Case 2',
            'CS:GO Weapon Case', 'eSports 2013 Winter Case', 'Operation Hydra Case', 'eSports 2013 Case',
            'Operation Bravo Case', 'Recoil Case']
    if box_name in past:
        return False
    return box_name


if __name__ == '__main__':
    print(check_case_update_blog())
