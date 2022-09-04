import requests
from time import sleep, perf_counter
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
                print('sleeping 15 seconds')
                sleep(15)
                break
            else:
                print(f'Nothing new ({current_id})')

        old_lines = old_file.readlines()
        url = f'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/{current_id}/csgo/resource/csgo_english.txt'
        for _ in range(1):
            print('1 pos')
            current_names = open('current_names.txt', 'w', encoding='utf-8')
            while True:
                try:
                    print('1loop')
                    sleep(1)
                    response = requests.get(url)
                    with open('DEBUG_SHIT.txt', 'w', encoding='utf-8') as op:
                        op.write(response.text)
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
            url_items = f'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/{current_id}/csgo/scripts/items/items_game.txt'
            while True:
                try:
                    print('2loop')
                    sleep(1)
                    response = requests.get(url_items)
                    if isinstance(response.text, str) and len(response.text) < 1000:
                        continue
                except (requests.exceptions.RequestException, urllib3.exceptions.RequestError, urllib3.exceptions.HTTPError) as e:
                    sleep(5)
                    continue
                break
            print('2 pos')
            current_items.write(response.text)
            current_items.close()
            current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()

            items = []
            stickers_count = 0
            sticker_map = dict()
            t0 = perf_counter()
            for line in current_names:
                if line in old_lines:
                    continue
                if line.count('"') == 4:
                    ri = line.rindex('"')
                    li = line[:ri].rfind('"')
                    lli = line[:li].find('"')
                    rri = line[:li].rfind('"')
                    item_tag = line[lli + 1:rri]
                    if ('CSGO_crate_community' not in item_tag and 'StickerKit' not in item_tag) or 'desc' in item_tag:
                        continue
                    if 'CSGO_crate_community' in item_tag:
                        items.insert(0, [f'{line[li + 1:ri]}', 'Case'])
                    elif 'StickerKit' in item_tag and 'signature' not in item_tag:
                        stickers_count += 1
                        sticker_map[item_tag] = f'Sticker | {line[li + 1:ri]}'
                        items.append(item_tag)

            last_rarity = ''
            rarities = {'ancient': 'Covert', 'legendary': 'Classified', 'mythical': 'Restricted',
                        'rare': 'Mil-Spec', 'uncommon': 'Industrial', 'common': 'Consumer',
                        }
            rarities_values = {
                'Consumer': 0, 'Industrial': 1, 'Mil-Spec': 2, 'Restricted': 3, 'Classified': 4, 'Covert': 5
            }
            for line in current_items[::-1]:
                if stickers_count == 0:
                    break
                if line.count('"') == 4:
                    ri = line.rindex('"')
                    li = line[:ri].rfind('"')
                    lli = line[:li].find('"')
                    rri = line[:li].rfind('"')
                    line_name = line[lli + 1:rri]
                    if line_name == 'item_rarity':
                        last_rarity = line[li + 1:ri]
                        continue
                    if line_name == 'item_name' and line[li + 2:ri] in items:
                        stickers_count -= 1
                        items[items.index(line[li + 2:ri])] = [sticker_map[line[li + 2:ri]], rarities[last_rarity]]
            if items:
                break
        print('4 pos')

        if not items:
            output.write('')
            return items
        ind = 0

        while 'Case' in items[ind][1]:
            output.write(f'<p><a href="https://steamcommunity.com/market/listings/730/{items[ind]}">{items[ind]}\t</a></p>')
            ind += 1
            if ind == len(items):
                break
        if 1 < len(items) != ind:

            def validate(x):
                return rarities_values[x[1]]

            items = items[:ind] + sorted(items[ind:], key=lambda x: validate(x), reverse=True)
        print(perf_counter() - t0)
        if ind == len(items):
            return items
        color_map = {
            'Consumer': 'C0C7D0', 'Industrial': '8FC3FF', 'Mil-Spec': '0175FA', 'Restricted': '7C19D8', 'Classified': 'EC24E6', 'Covert': 'DD5032'
        }
        for item in items[ind:]:
            output.write(f'<p><a style="font-size: 20px;color:#{color_map[item[1]]}" href="https://steamcommunity.com/market/listings/730/{item[0]}">{item[0]}\t</a>')
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
    if box_name and box_name[0][1] == 'Case' and box_name[0][0] not in past:
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
    print(check_case_update())
