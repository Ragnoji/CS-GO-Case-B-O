from time import sleep
from selenium.webdriver.common.keys import Keys
import vlc
import requests
from datetime import datetime
from threading import Thread, Event
from differ_items import differ
from worker_template_requests import worker, case_worker
from weapon_parser import new_weapons
import os
from dotenv import load_dotenv
import requests.adapters
from selenium import webdriver


def loop_alarm():
    p = vlc.MediaPlayer("alarm.mp3")
    p.play()
    while True:
        sleep(1)
        if not p.is_playing():
            p = vlc.MediaPlayer("alarm.mp3")
            p.play()


case_re = False
stickers = False
case_fi = False
new_skins = False


def main():
    c_options = webdriver.ChromeOptions()
    # driver = webdriver.Chrome("yandexdriver.exe", options=c_options)

    url = f'https://steamcommunity.com/market/listings/730/Place'
    load_dotenv()
    steam_r = os.getenv('STEAM_REFRESH_MAIN')  # steamRefresh_steam cookie for login.steampowered.com
    steam_s = os.getenv('STEAM_SECURE_MAIN')  # steamLoginSecure cookie for steamcommunity.com
    session = requests.session()
    session.cookies.set(steam_s[:steam_s.find('=')], steam_s[steam_s.find('=') + 1:], domain='steamcommunity.com',
                        path='/')
    session.cookies.set(steam_r[:steam_r.find('=')], steam_r[steam_r.find('=') + 1:], domain='login.steampowered.com',
                        path='/')
    session.get('https://login.steampowered.com/jwt/refresh?redir=https%3A%2F%2Fsteamcommunity.com')
    # driver.get(url)
    # for c in session.cookies:
    #     if c.domain != 'steamcommunity.com':
    #         continue
    #     print({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
    #     driver.add_cookie({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
    # while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
    #     driver.refresh()
    #     sleep(2)
    # session.close()

    new_box_name = False
    case_workers = []
    event = Event()

    def case_blog(fun=differ.check_case_update_blog):
        global case_re
        case_re = fun()
        while case_re is False:
            sleep(3)
            case_re = fun()

    def case_commits(fun=differ.check_case_update):
        global case_fi
        global stickers
        global new_skins
        case_fi, stickers = fun()
        current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
        old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
        current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()
        new_skins = new_weapons(current_items, old_items, current_names)
        while case_fi is False and not stickers and not new_skins:
            case_fi, stickers = fun()
            current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
            old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
            current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()
            new_skins = new_weapons(current_items, old_items, current_names)

    t1 = Thread(target=case_blog)
    t2 = Thread(target=case_commits)
    # t1.start()
    t2.start()
    while True:
        sleep(5)
        global case_re
        global case_fi
        global stickers
        global new_skins
        # if isinstance(case_re, str):
        #     if len(case_workers) == 0:
        #         new_box_name = case_re
        #         print(f"Регулярка: {new_box_name}")
        #         w = Thread(target=case_worker, args=(new_box_name, event))
        #         w.start()
        #         case_workers.append(w)
        #         Thread(target=loop_alarm).start()
        #     elif len(case_workers) == 1:
        #         break
        #     case_re = False
        if isinstance(case_fi, list):
            if len(case_workers) == 0:
                new_box_name = case_fi[0]
                w = Thread(target=case_worker, args=(new_box_name, event))
                w.start()
                case_workers.append(w)
                Thread(target=loop_alarm).start()
            elif case_fi[0] != new_box_name:
                event.set()
                case_workers[-1].join()
                del case_workers[-1]
                event = Event()
                new_box_name = case_fi[0]
                w = Thread(target=case_worker, args=(new_box_name, event))
                w.start()
                case_workers.append(w)
                Thread(target=loop_alarm).start()
            print(f"Файл парсер: {new_box_name}")

            case_fi = []
            break
        if stickers:
            print('New stickers without case')
            Thread(target=loop_alarm).start()
            break
        if new_skins:
            print('New skins without case')
            Thread(target=loop_alarm).start()
            break

    if case_workers:
        case_workers[-1].join()

    # driver.refresh()
    # if new_box_name and 'Operation' not in new_box_name:  # No sense in placing bo for operation case
    #     print(new_box_name)
    #     w = Thread(target=case_worker, args=new_box_name)
    #     w.start()
    #     while w.is_alive():
    #         print('Trying case')
    #         sleep(5)

    # current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
    # old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
    # current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()
    # new_skins = new_weapons(current_items, old_items, current_names)
    list_of_covert = []
    list_of_extreme_covert = []
    list_of_classified = []
    list_of_extreme_classified = []
    # print(new_skins)
    if new_skins:
        # Need to adapt prices depending on your choice and currency
        for collection in new_skins.keys():
            for item in new_skins[collection]:
                if 'Collection' in collection and item[1] == 'Covert':
                    for exterior in item[2]:
                        cost = 14000
                        # list_of_extreme_covert.append((item[0] + f' ({exterior})', cost, 2))
                        print(f'"{item[0]} ({exterior})" {cost} 3')

                elif 'Collection' in collection and item[1] == 'Classified':
                    for exterior in item[2]:
                        cost = 3500
                        # list_of_extreme_classified.append((item[0] + f' ({exterior})', cost, 6))
                        print(f'"{item[0]} ({exterior})" {cost} 6')

                elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Classified':
                    for exterior in item[2]:
                        if exterior == 'Field-Tested':
                            cost = 255
                            quan = 20
                        elif exterior == 'Minimal Wear':
                            cost = 425
                            quan = 15
                        else:
                            continue
                        # list_of_classified.append((item[0] + f' ({exterior})', cost, quan))

                # elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Covert':
                #     for exterior in item[2]:
                #         if exterior == 'Factory New':
                #             cost = 70
                #             quan = 5
                #         elif exterior == 'Minimal Wear':
                #             cost = 70
                #             quan = 10
                #         elif exterior == 'Field-Tested':
                #             cost = 70
                #             quan = 10
                #         else:
                #             continue
                #         list_of_covert.append((item[0] + f' ({exterior})', cost, quan))

    covert_workers = []
    classified_workers = []
    extreme_workers = []
    normal_workers = []
    if list_of_extreme_covert:
        extreme_workers.append(Thread(target=worker, args=(list_of_extreme_covert, 730, 1)))
        extreme_workers[-1].start()
    if list_of_extreme_classified:
        extreme_workers.append(Thread(target=worker, args=(list_of_extreme_classified, 730, 1)))
        extreme_workers[-1].start()
    if list_of_classified:
        normal_workers.append(Thread(target=worker, args=(list_of_classified, 730)))
        normal_workers[-1].start()
    for w in extreme_workers + normal_workers:
        w.join()

    # if list_of_covert:
    #     covert_worker = Thread(target=worker, args=(list_of_covert, 730, 0.6))
    #     covert_workers.append(covert_worker)
    #     covert_worker.start()
    #
    # if list_of_classified:
    #     classified_worker = Thread(target=worker, args=(list_of_classified, 0.3))
    #     classified_workers.append(classified_worker)
    #     classified_worker.start()
    covert_s = []
    class_s = []
    restr_s = []
    milsp_s = []
    if isinstance(stickers, list):

        # Need to adapt prices depending on your choice and currency
        allowed_stickers = ['breach', 'heroic', '9ine', 'mouz', 'faze', 'fnatic', 'vitality', 'pain', 'fluxo']

        def sticker_map(st):
            if not any([i in st[0].lower() for i in allowed_stickers]):
                return False
            # if st[1] == 'Covert':
            #     covert_s.append((st[0], 65, 20))
            # if st[1] == 'Classified':
            #     class_s.append((st[0], 10, 200))
            # if st[1] == 'Restricted':
            #     restr_s.append((st[0], 2, 1000))
            # elif st[1] == 'Mil-Spec':
            #     milsp_s.append((st[0], 1, 300))
            else:
                return False
        for s in stickers:
            sticker_map(s)
    sticker_workers = []
    if stickers:
        # if covert_s:
        #     covert_sticker_worker = Thread(target=worker, args=(covert_s, 730, 0))
        #     sticker_workers.append(covert_sticker_worker)
        # if class_s:
        #     sticker_workers.append(Thread(target=worker, args=(class_s, 730, 0), kwargs={"time_out": 0.42}))
        #     sticker_workers.append(Thread(target=worker, args=(class_s, 730, 0), kwargs={"time_out": 0.42, "acc": 1}))
        if restr_s:
            sticker_workers.append(Thread(target=worker, args=(restr_s, 730, 0), kwargs={"time_out": 0.45}))
            sticker_workers.append(Thread(target=worker, args=(restr_s, 730, 0), kwargs={"time_out": 0.45, "acc": 1}))
        # if milsp_s:
        #     milsp_sticker_worker = Thread(target=worker, args=(milsp_s, 730, 0))
        #     sticker_workers.append(milsp_sticker_worker)
        print('starting sticker_workers')
        for s_w in sticker_workers:
            s_w.start()
            sleep(0.3)

    # if new_box_name:
    #     knives_worker = Thread(target=worker, args=(list_of_knives, 0.5))
    #     knives_worker.start()

    for s_w in sticker_workers:
        s_w.join()
    # if new_box_name or is_operation:
    #     knives_worker.join()
    if list_of_covert:
        for c in covert_workers:
            c.join()
    if list_of_classified:
        for c in classified_workers:
            c.join()
    # driver.close()


if __name__ == '__main__':
    main()