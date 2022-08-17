from bot_worker import worker
from bot_worker_direct import worker_direct
from threading import Thread
from time import sleep
import os
from dotenv import load_dotenv
import requests
import re


def main():
    list_of_items = open('target_items.txt', 'r', encoding='utf-8')
    list_of_items = list_of_items.readlines()

    if not list_of_items:
        print('create "target_items.txt" file with inputs')
        return

    list_of_items = [item_line.strip().split() for item_line in list_of_items]
    count_map = dict()
    for i in range(len(list_of_items)):
        tmp = list_of_items[i]
        for g, v in enumerate(tmp):
            if v.endswith('"'):
                list_of_items[i] = [''.join(' '.join(tmp[:g + 1])[1:-1])] + tmp[g + 1:]
                count_map[list_of_items[i][0]] = 0
    print(*list_of_items)
    game_index = 252490
    webdriver = False
    mode = 1  # 0 если нужен бот на нормал скины и 1 если бот на абнормал (-1 если нужно прямо сейчас В СЛУЧАЕ КЕЙСА ИТД)
    parallel = True  # Регулировка режима запуска воркеров
    require = input(f'Согласны ли вы с таргетами и параметрами:\nwebdriver = {webdriver}\ngame_index = {game_index}\nmode = {mode}\nparallel = {parallel}\n')
    if require != '':
        return
    print('Начинаю работу')
    threads = []
    selected_worker = worker if webdriver else worker_direct
    if parallel:
        for i in range(0, len(list_of_items)):
            threads.append(Thread(target=selected_worker, args=([list_of_items[i]], game_index, mode, i)))
    else:
        # splited_lists = [[], []]
        # for i, item in enumerate(list_of_items):
        #     splited_lists[i % 2].append(item)
        # for i, s_l in enumerate(splited_lists):
        #     if s_l:
        #         threads.append(Thread(target=selected_worker, args=(s_l, game_index, mode, i)))
        #         threads[-1].start()
        threads.append(Thread(target=selected_worker, args=(list_of_items, game_index, mode)))

    if mode == 0:
        load_dotenv()
        steam_m = os.getenv('STEAM_AUTH_MAIN')
        steam_r = os.getenv('STEAM_REMEMBER_MAIN')
        headers = {'Host': 'steamcommunity.com',
                   'Origin': 'https://steamcommunity.com',
                   'Referer': 'https://steamcommunity.com/market', 'Connection': 'keep-alive',
                   'Accept-Language': 'en;q=0.9,zh;q=0.8', 'Accept-Encoding': 'gzip, deflate, br',
                   'Accept': '*/*',
                   'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.134 YaBrowser/22.7.1.806 Yowser/2.5 Safari/537.36',
                   'Cookie': f'{steam_m};{steam_r};steamCurrencyId=5'
                   }
        session = requests.session()
        session.headers.update(headers)
        resp = session.get('https://steamcommunity.com/workshop/browse/?appid=252490&browsesort=accepted&section=mtxitems')
        element = re.findall(r'<div class="workshopBrowsePagingInfo">.+</div>', resp.text)
        while not element:
            resp = session.get('https://steamcommunity.com/workshop/browse/?appid=252490&browsesort=accepted&section=mtxitems')
            element = re.findall(r'<div class="workshopBrowsePagingInfo">.+</div>', resp.text)
            sleep(1)
        old = element[0]
        new = old
        while new == old:
            element = ''
            while not element:
                sleep(2)
                resp = session.get('https://steamcommunity.com/workshop/browse/?appid=252490&browsesort=accepted&section=mtxitems')
                element = re.findall(r'<div class="workshopBrowsePagingInfo">.+</div>', resp.text)
            new = element[0]
        for t in threads:
            t.start()
            sleep(3)
    else:
        for t in threads:
            t.start()
            if selected_worker == worker:
                sleep(7.5)
            sleep(0.5)

    sleep(3)
    for t in threads:
        if t.is_alive():
            t.join()


if __name__ == '__main__':
    main()
