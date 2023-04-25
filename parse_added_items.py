from weapon_parser import new_weapons
import requests
from time import sleep, perf_counter
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3
import json


def main():
    with open('new_names.html', 'w', encoding='utf-8') as output:
        while True:
            try:
                response = requests.get(
                    f'https://github.com/SteamDatabase/GameTracking-CSGO/commits/master',
                )
            except (TimeoutError, requests.exceptions.RequestException, urllib3.exceptions.RequestError,
                    urllib3.exceptions.HTTPError, requests.exceptions.ConnectTimeout,
                    urllib3.exceptions.MaxRetryError, urllib3.exceptions.ConnectTimeoutError):
                sleep(10)
                continue
            break

        old_data = BeautifulSoup(response.text, features='lxml')
        old_id = old_data.find_all("div", "TimelineItem-body")[1].find("a", "tooltipped tooltipped-sw btn-outline btn BtnGroup-item text-mono f6").getText().strip()
        print(old_id)
        url = f'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/{old_id}/csgo/resource/csgo_english.txt'
        old_file = open('old_names.txt', 'w', encoding='utf-8')
        while True:
            try:
                sleep(1)
                response = requests.get(url)
                if isinstance(response.text, str) and len(response.text) < 1000:
                    continue
            except (TimeoutError, requests.exceptions.RequestException, urllib3.exceptions.RequestError,
                    urllib3.exceptions.HTTPError, requests.exceptions.ConnectTimeout,
                    urllib3.exceptions.MaxRetryError, urllib3.exceptions.ConnectTimeoutError):
                sleep(5)
                continue
            break
        old_file.write(response.text)
        old_file.close()
        url_items = f'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/{old_id}/csgo/scripts/items/items_game.txt'
        old_items = open('old_items.txt', 'w', encoding='utf-8')
        while True:
            try:
                sleep(1)
                response = requests.get(url_items)
                if isinstance(response.text, str) and len(response.text) < 1000:
                    continue
            except (TimeoutError, requests.exceptions.RequestException, urllib3.exceptions.RequestError,
                    urllib3.exceptions.HTTPError, requests.exceptions.ConnectTimeout,
                    urllib3.exceptions.MaxRetryError, urllib3.exceptions.ConnectTimeoutError):
                sleep(5)
                continue
            break
        old_items.write(response.text)
        old_items.close()
        old_file = open('old_names.txt', 'r', encoding='utf-8')

        old_lines = old_file.readlines()
        url = 'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/master/csgo/resource/csgo_english.txt'
        for _ in range(5):
            current_names = open('current_names.txt', 'w', encoding='utf-8')
            while True:
                try:
                    sleep(1)
                    response = requests.get(url)
                    with open('DEBUG_SHIT.txt', 'w', encoding='utf-8') as op:
                        op.write(response.text)
                    if isinstance(response.text, str) and len(response.text) < 1000:
                        continue
                except (TimeoutError, requests.exceptions.RequestException, urllib3.exceptions.RequestError,
                        urllib3.exceptions.HTTPError, requests.exceptions.ConnectTimeout,
                        urllib3.exceptions.MaxRetryError, urllib3.exceptions.ConnectTimeoutError):
                    sleep(5)
                    continue
                break
            current_names.write(response.text)
            current_names.close()
            current_names = open('current_names.txt', 'r', encoding='utf-8')
            current_names = current_names.readlines()

            current_items = open('current_items.txt', 'w', encoding='utf-8')
            url_items = f'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/master/csgo/scripts/items/items_game.txt'
            while True:
                try:
                    sleep(1)
                    response = requests.get(url_items)
                    if isinstance(response.text, str) and len(response.text) < 1000:
                        continue
                except (TimeoutError, requests.exceptions.RequestException, urllib3.exceptions.RequestError,
                        urllib3.exceptions.HTTPError, requests.exceptions.ConnectTimeout,
                        urllib3.exceptions.MaxRetryError, urllib3.exceptions.ConnectTimeoutError):
                    sleep(5)
                    continue
                break
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

        if not items:
            output.write('')
        ind = 0

        while items and 'Case' in items[ind][1]:
            output.write(f'<p><a href="https://steamcommunity.com/market/listings/730/{items[ind]}">{items[ind]}\t</a></p>')
            ind += 1
            if ind == len(items):
                break
        if 1 < len(items) != ind:

            def validate(x):
                return rarities_values[x[1]]

            items = items[:ind] + sorted(items[ind:], key=lambda x: validate(x), reverse=True)
        print(perf_counter() - t0)
        color_map = {
            'Consumer': 'C0C7D0', 'Industrial': '8FC3FF', 'Mil-Spec': '0175FA', 'Restricted': '7C19D8', 'Classified': 'EC24E6', 'Covert': 'DD5032'
        }
        for item in items[ind:]:
            output.write(f'<p><a style="font-size: 20px;color:#{color_map[item[1]]}" href="https://steamcommunity.com/market/listings/730/{item[0]}">{item[0]}\t</a>')
        print(f'{datetime.now().strftime("%H:%M:%S")} | {len(items)} New Items Added')

    current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
    old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
    current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()
    new_skins = new_weapons(current_items, old_items, current_names)
    print(json.dumps(new_skins, sort_keys=False, indent=2))


if __name__ == '__main__':
    main()
