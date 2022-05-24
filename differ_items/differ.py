import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime


def differ():
    with open('new_names.html', 'w', encoding='utf-8') as output:
        response = requests.get(
            f'https://blog.counter-strike.net/index.php/category/updates/page/1/',
        )
        recent_post = BeautifulSoup(response.text, features='lxml')
        recent_post = recent_post.find("div", "inner_post").getText()
        cached_id = recent_post.split('\n')[1]
        url = 'https://raw.githubusercontent.com/SteamDatabase/GameTracking-CSGO/master/csgo/resource/csgo_english.txt'
        old_file = open('old_names', 'w', encoding='utf-8')
        old_file.write(requests.get(url).text)
        old_file.close()
        old_file = open('old_names', 'r', encoding='utf-8')
        print('Starting patch -', cached_id)
        while True:
            sleep(2)
            print(f'{datetime.now().strftime("%H:%M:%S")} | Checking ...')
            response = requests.get(
                f'https://blog.counter-strike.net/index.php/category/updates/page/1/',
            )
            recent_post = BeautifulSoup(response.text, features='lxml')
            recent_post = recent_post.find("div", "inner_post").getText()
            if recent_post.split('\n')[1] != cached_id:
                cached_id = recent_post.split('\n')[1]
                print(f'{datetime.now().strftime("%H:%M:%S")} | {cached_id}')
                break

        current_names = open('current_names.txt', 'w', encoding='utf-8')
        current_names.write(requests.get(url).text)
        current_names.close()
        current_names = open('current_names.txt', 'r', encoding='utf-8')
        current_names = current_names.readlines()
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
        if len(items) > 1:
            items = [items[0]] + sorted(items[1:], reverse=True) if 'Case' in items[0] else sorted(items, reverse=True)
        prev_item = items[0]
        output.write(f'<p><a href="https://steamcommunity.com/market/listings/730/{prev_item}">{prev_item}\t</a>')
        for item in items[items.index(prev_item) + 1:]:
            if prev_item.split()[2] == item.split()[2]:
                output.write(f'......<a href="https://steamcommunity.com/market/listings/730/{item}">{item[item.find("(") + 1:item.find(")")]}</a>')
            else:
                output.write(f'<p><a href="https://steamcommunity.com/market/listings/730/{item}">{item}\t</a>')
            prev_item = item
        print(f'{datetime.now().strftime("%H:%M:%S")} | {len(items)} New Items Added')
        return items


if __name__ == '__main__':
    differ()
