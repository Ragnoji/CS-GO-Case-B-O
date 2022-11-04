from time import sleep
from selenium.webdriver.common.keys import Keys
import vlc
import requests
from datetime import datetime
from threading import Thread
from differ_items import differ
from worker_template_requests import worker
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
    driver = webdriver.Chrome("yandexdriver.exe", options=c_options)

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
    driver.get(url)
    for c in session.cookies:
        if c.domain != 'steamcommunity.com':
            continue
        print({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
        driver.add_cookie({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
    while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
        driver.refresh()
        sleep(2)
    session.close()
    balance_element = driver.find_element_by_xpath('//*[@id="marketWalletBalanceAmount"]').text
    balance = ''.join(list((filter(lambda s: s.isdigit() or s in [',', '.'], balance_element))))
    balance = int(balance.split(',')[0].split('.')[0])
    cost = 21  # В рублях
    quantity = (balance // cost) - 20
    print(f"Баланс {balance}. Можно поставить {balance // cost} кейсов")

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
    t1.start()
    t2.start()
    new_box_name = False
    while True:
        sleep(5)
        global case_re
        global case_fi
        global stickers
        global new_skins
        if case_re:
            new_box_name = case_re
            Thread(target=loop_alarm).start()
            break
        if isinstance(case_fi, list):
            new_box_name = case_fi[0]
            print(new_box_name)
            Thread(target=loop_alarm).start()
            break
        if stickers:
            print('New stickers without case')
            Thread(target=loop_alarm).start()
            break
        if new_skins:
            print('New skins without case')
            Thread(target=loop_alarm).start()

    driver.refresh()
    if new_box_name and 'Operation' not in new_box_name:  # No sense in placing bo for operation case
        print(f'"{new_box_name}" {cost} {quantity}')
        case_worker = Thread(target=worker, args=([(new_box_name, cost, quantity)], 730, 0.1))
        case_worker.start()
        while case_worker.is_alive():
            print('Trying case')
            sleep(5)

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
                        cost = 8000
                        # list_of_extreme_covert.append((item[0] + f' ({exterior})', cost, 3))
                        print(f'"{item[0]} ({exterior})" {cost} 3')

                elif 'Collection' in collection and item[1] == 'Classified':
                    for exterior in item[2]:
                        cost = 3500
                        # list_of_classified.append((item[0] + f' ({exterior})', cost, 6))
                        print(f'"{item[0]} ({exterior})" {cost} 6')

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

                # elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Classified':
                #     for exterior in item[2]:
                #         if exterior == 'Factory New':
                #             cost = 70
                #             quan = 10
                #         elif exterior == 'Minimal Wear':
                #             cost = 70
                #             quan = 10
                #         # elif exterior == 'Field-Tested':
                #         #     cost = 70
                #         #     quan = 10
                #         else:
                #             continue
                #         list_of_classified.append((item[0] + f' ({exterior})', cost, quan))
    covert_workers = []
    classified_workers = []
    extreme_workers = []
    if list_of_extreme_covert or list_of_extreme_classified:
        for i in list_of_extreme_covert:
            extreme_workers.append(Thread(target=worker, args=([i], 730, 1)))
            extreme_workers[-1].start()
            sleep(0.2)
        for i in list_of_extreme_classified:
            extreme_workers.append(Thread(target=worker, args=([i], 730, 0.6)))
            extreme_workers[-1].start()
            sleep(0.3)
        for w in extreme_workers:
            w.join()

    if list_of_covert:
        covert_worker = Thread(target=worker, args=(list_of_covert, 730, 0.6))
        covert_workers.append(covert_worker)
        covert_worker.start()

    if list_of_classified:
        classified_worker = Thread(target=worker, args=(list_of_classified, 0.3))
        classified_workers.append(classified_worker)
        classified_worker.start()
    covert_s = []
    class_s = []
    restr_s = []
    milsp_s = []
    if isinstance(stickers, list):

        # Need to adapt prices depending on your choice and currency
        def sticker_map(s):
            if s[1] == 'Covert':
                covert_s.append((s[0], 60, 20))
            # elif s[1] == 'Classified':
            #     class_s.append((s[0], 10, 50))
            # elif s[1] == 'Restricted':
            #     restr_s.append((s[0], 2, 200))
            # elif s[1] == 'Mil-Spec':
            #     milsp_s.append((s[0], 1, 300))
            else:
                return False
        for s in stickers:
            sticker_map(s)
    sticker_workers = []
    if stickers:
        if covert_s:
            covert_sticker_worker = Thread(target=worker, args=(covert_s, 730, 0.2))
            sticker_workers.append(covert_sticker_worker)
        # if class_s:
        #     class_sticker_worker = Thread(target=worker, args=(class_s, 730, 0.3))
        #     sticker_workers.append(class_sticker_worker)
        if restr_s:
            restr_sticker_worker = Thread(target=worker, args=(restr_s, 730, 0.2))
            sticker_workers.append(restr_sticker_worker)
        # if milsp_s:
        #     milsp_sticker_worker = Thread(target=worker, args=(milsp_s, 730, 0.3))
        #     sticker_workers.append(milsp_sticker_worker)
        for s_w in sticker_workers:
            s_w.start()
            sleep(0.5)

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
    driver.close()


if __name__ == '__main__':
    main()