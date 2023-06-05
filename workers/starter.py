from bot_worker import worker
from bot_worker_direct import worker_direct
from threading import Thread
from multiprocessing import Process
from time import sleep, perf_counter
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
    game_index = 730
    webdriver = False
    mode = -1  # 0 если нужен бот на нормал скины и 2 если бот на абнормал (-1 если нужно прямо сейчас В СЛУЧАЕ КЕЙСА ИТД)
    acc = 0  # 0 main 1 twink
    # if acc != 0:
    #     list_of_items = list_of_items[::-1]
    use_proxy = False
    parallel = False  # Регулировка режима запуска воркеров
    require = input(f'Согласны ли вы с таргетами и параметрами:\nwebdriver = {webdriver}\ngame_index = {game_index}\nmode = {mode}\nparallel = {parallel}\n'
                    f'acc = {acc}\nuse_proxy = {use_proxy}\n')
    if require != '':
        return
    print('Начинаю работу')
    threads = []
    selected_worker = worker if webdriver else worker_direct
    if parallel:
        for i in range(0, len(list_of_items)):
            threads.append(Process(target=selected_worker, args=([list_of_items[i]], game_index, mode, i),
                                   kwargs={'use_proxy': use_proxy, 'acc': acc}))
    else:
        # splited_lists = [[], []]
        # for i, item in enumerate(list_of_items):
        #     splited_lists[i % 2].append(item)
        # for i, s_l in enumerate(splited_lists):
        #     if s_l:
        #         threads.append(Process(target=selected_worker, args=(s_l, game_index, mode, i)))
        #         threads[-1].start()
        load_dotenv()
        threads.append(Process(target=selected_worker, args=(list_of_items, game_index, mode),
                               kwargs={'use_proxy': use_proxy, 'acc': acc, 'slp': 0}))

    if mode == 0:
        load_dotenv()
        steam_r = os.getenv('STEAM_REFRESH_PARSER')
        steam_s = os.getenv('STEAM_SECURE_PARSER')
        proxy = {'https': 'socks5://user58497:nx0yrs@193.160.211.84:11443',
                 'http': 'socks5://user58497:nx0yrs@193.160.211.84:11443'}
        no_proxy = {
            'https': '',
            'http': ''
        }

        session = requests.session()
        session.cookies.set(steam_s[:steam_s.find('=')], steam_s[steam_s.find('=') + 1:], domain='steamcommunity.com',
                            path='/')
        session.cookies.set(steam_r[:steam_r.find('=')], steam_r[steam_r.find('=') + 1:],
                            domain='login.steampowered.com', path='/')
        session.get('https://steamcommunity.com/')
        resp = session.get('https://steamcommunity.com/workshop/browse/?appid=252490&browsesort=accepted&section=mtxitems')
        element = re.findall(r'<div class="workshopBrowsePagingInfo">.+</div>', resp.text)
        while not element:
            resp = session.get('https://steamcommunity.com/workshop/browse/?appid=252490&browsesort=accepted&section=mtxitems')
            element = re.findall(r'<div class="workshopBrowsePagingInfo">.+</div>', resp.text)
            sleep(1)
        old = element[0]
        new = old
        use_proxy = False
        proxy_switch = False
        print(new)
        while new == old:
            element = ''
            while not element:
                if use_proxy and proxy_switch:
                    session.proxies.update(proxy)
                    proxy_switch = False
                else:
                    session.proxies.update(no_proxy)
                    proxy_switch = True
                sleep(5)
                try:
                    resp = session.get('https://steamcommunity.com/workshop/browse/?appid=252490&browsesort=accepted&section=mtxitems')
                except requests.ConnectionError:
                    continue
                element = re.findall(r'<div class="workshopBrowsePagingInfo">.+</div>', resp.text)
            new = element[0]
            print(new)
        for t in threads:
            sleep(0.2)
            t.start()
            if selected_worker == worker:
                sleep(7)
            sleep(0.5)
    else:
        for t in threads:
            t.start()
            if selected_worker == worker:
                sleep(7.5)

    sleep(3)
    for t in threads:
        if t.is_alive():
            t.join()


if __name__ == '__main__':
    main()
