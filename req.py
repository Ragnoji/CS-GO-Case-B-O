from time import sleep
from selenium.webdriver.common.keys import Keys
import vlc
import pickle
import requests
from datetime import datetime
from threading import Thread
from differ_items import differ
from worker_template import worker
from weapon_parser import new_weapons
import os
from dotenv import load_dotenv
import telebot
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
    options = {
        'proxy': {
            'http': 'http://user58497:nx0yrs@193.160.211.84:1443',
            'https': 'https://user58497:nx0yrs@193.160.211.84:1443',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    c_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome("yandexdriver.exe", options=c_options)

    url = f'https://steamcommunity.com/market/listings/730/Place'
    load_dotenv()
    token = os.getenv('AUTH_TOKEN')
    bot = telebot.TeleBot(token)
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
    session.get('https://steamcommunity.com/market/')
    driver.get(url)
    for c in session.cookies:
        driver.add_cookie({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
    while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
        driver.refresh()
        sleep(2)
    session.close()
    # list_of_knives = open('knives_to_parse.txt', 'r', encoding='utf-8')
    # list_of_knives = list_of_knives.readlines()
    #
    # if not list_of_knives:
    #     print('create "target_items.txt" file with inputs')

    # list_of_knives = [item_line.strip().split() for item_line in list_of_knives]
    # count_knives = dict()
    # for i in range(len(list_of_knives)):
    #     tmp = list_of_knives[i]
    #     for g, v in enumerate(tmp):
    #         if v.endswith('"'):
    #             list_of_knives[i] = [''.join(' '.join(tmp[:g + 1])[1:-1])] + tmp[g + 1:]
    #             count_knives[list_of_knives[i][0]] = 0
    # print(*list_of_knives)
    # if input('Согласны с таргетами?') != '':
    #     return

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
        while case_fi is False and stickers is False and not new_skins:
            case_fi, stickers = fun()
            current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
            old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
            current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()
            new_skins = new_weapons(current_items, old_items, current_names)

    t1 = Thread(target=case_blog)
    t2 = Thread(target=case_commits)
    t1.start()
    t2.start()
    while True:
        sleep(5)
        global case_re
        global case_fi
        global stickers
        global new_skins
        if case_re:
            new_box_name = case_re
            Thread(target=loop_alarm).start()
            bot.send_message(852738955, "Новые кейс в CS:GO")
            break
        if case_fi:
            new_box_name = case_fi
            Thread(target=loop_alarm).start()
            bot.send_message(852738955, "Новый кейс в CS:GO")
            break
        if stickers:
            Thread(target=loop_alarm).start()
            bot.send_message(852738955, "Новые стикеры в CS:GO")
            break
        if new_skins:
            print('New skins without case')
            Thread(target=loop_alarm).start()
            bot.send_message(852738955, "Новые скины без кейса в CS:GO")

    driver.refresh()
    Thread(target=loop_alarm).start()
    console_command = f'Market_ShowBuyOrderPopup(730, "{new_box_name}", "{new_box_name}")'
    print(f'NEW CASE RELEASE\nCommand for fast buy:\n{console_command}')
    count = 0
    while True:
        if not new_box_name:
            break
        if count == 20:
            count = 0
            driver.refresh()
            while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
                driver.refresh()
                sleep(1)
        driver.execute_script(console_command)
        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
        cost = 70
        try:
            price.send_keys(Keys.BACKSPACE * 20, f'{cost}')
        except Exception:
            with open('log.txt', 'a', encoding='utf-8') as logg:
                message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | слетела кука или баганула страница\n'
                logg.write(message)
                print(message)
            session = requests.session()
            session.headers.update(headers)
            session.get('https://steamcommunity.com/market/')
            driver.get(url)
            for c in session.cookies:
                driver.add_cookie({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
            while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
                driver.refresh()
                sleep(2)
            session.close()
            driver.execute_script(console_command)
            price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
            price.send_keys(Keys.BACKSPACE * 20, f'{cost}')
        balance_element = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_walletbalance_amount"]').text
        balance = int(balance_element.split('руб')[0].split(',')[0])
        quant = (balance // cost) - 1
        # sleep(0.1)
        quantity = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_quantity"]')
        quantity.send_keys(Keys.BACKSPACE * 20, f'{quant}')
        # sleep(0.1)

        accept = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_accept_ssa"]')
        if not accept.is_selected():
            accept.click()
        # sleep(0.1)

        place = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_purchase"]')
        if not place.is_displayed():
            count = 20
            continue
        place.click()
        sleep(0.3)
        count += 1

        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        if is_error != 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
            continue

        with open('log.txt', 'a', encoding='utf-8') as logg:
            message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {new_box_name} | {cost} руб | {quant}\n'
            logg.write(message)
            print(message)
        break

    # current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
    # old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
    # current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()
    # new_skins = new_weapons(current_items, old_items, current_names)
    # list_of_covert = []
    # list_of_classified = []
    # print(new_skins)
    # if new_skins:
    #     for collection in new_skins.keys():
    #         for item in new_skins[collection]:
    #             if 'Collection' in collection and item[1] == 'Covert':
    #                 for exterior in item[2]:
    #                     cost = 6000
    #                     list_of_covert.append((item[0] + f' ({exterior})', cost, 2))
    #
    #             elif 'Collection' in collection and item[1] == 'Classified':
    #                 for exterior in item[2]:
    #                     cost = 3000
    #                     list_of_classified.append((item[0] + f' ({exterior})', cost, 5))
    #
    #             elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Covert':
    #                 for exterior in item[2]:
    #                     if exterior == 'Factory New':
    #                         cost = 400
    #                     elif exterior == 'Minimal Wear':
    #                         cost = 150
    #                     else:
    #                         cost = 100
    #                     list_of_covert.append(('StatTrak™ ' + item[0] + f' ({exterior})', cost*2, 20))
    #
    #                     elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Classified':
    #                 for exterior in item[2]:
    #                     if exterior == 'Factory New':
    #                         cost = 200
    #                     elif exterior == 'Minimal Wear':
    #                         cost = 100
    #                     elif exterior == 'Field-Tested':
    #                         cost = 60
    #                     else:
    #                         cost = 50
    #                     list_of_classified.append((item[0] + f' ({exterior})', cost, 20))
    # covert_workers = []
    # if list_of_covert:
    #     # covert_worker = Thread(target=worker, args=(list_of_covert, 2.5))
    #     for c in list_of_covert:
    #         covert_worker = Thread(target=worker, args=([c], 2))
    #         covert_worker.start()
    #         sleep(10)
    #         covert_workers.append(covert_worker)

    # if list_of_classified:
    #     classified_worker = Thread(target=worker, args=(list_of_classified, 2.5))
    #     classified_worker.start()
    if isinstance(stickers, list):

        def sticker_map(s):
            if '(Gold)' in s:
                return s, 80, 10
            elif '(Foil)' in s:
                return s, 40, 30
            elif '(Holo)' in s:
                return s, 14, 100
            else:
                return s, 2, 200

        stickers = list(map(lambda s: sticker_map(s), stickers))
                            # filter(lambda s: isinstance(s, str) and ('(Holo)' in s or '(Gold)' in s or '(Foil)' in s),
                            #        stickers)))
    sticker_workers = []
    if stickers:
        gold_sticker_worker = Thread(target=worker, args=([s for s in stickers if '(Gold)' in s[0]], 1))
        foil_sticker_worker = Thread(target=worker, args=([s for s in stickers if '(Foil)' in s[0]], 0.4))
        holo_sticker_worker = Thread(target=worker, args=([s for s in stickers if '(Holo)' in s[0]], 0.4))
        paper_sticker_worker = Thread(target=worker, args=([s for s in stickers if '(' not in s[0] and ')' not in s[0]], 0.4))
        sticker_workers = [gold_sticker_worker, foil_sticker_worker, holo_sticker_worker, paper_sticker_worker]
        for s_w in sticker_workers[::-1]:
            s_w.start()
            sleep(6)

    # if new_box_name or is_operation:
    #     knives_worker = Thread(target=worker, args=(list_of_knives, 4))
    #     knives_worker.start()

    for s_w in sticker_workers:
        s_w.join()
    # if new_box_name or is_operation:
    #     knives_worker.join()
    # if list_of_covert:
    #     for c in covert_workers:
    #         c.join()
    # if list_of_classified:
    #     classified_worker.join()
    driver.close()


if __name__ == '__main__':
    main()