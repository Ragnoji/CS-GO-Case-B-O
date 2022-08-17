from time import sleep
from selenium.webdriver.common.keys import Keys
import vlc
import pickle
import requests
from datetime import datetime
from threading import Thread
from differ_items import differ
from worker_template_requests import worker
from weapon_parser import new_weapons
import os
from dotenv import load_dotenv
import telebot
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
            bot.send_message(852738955, "Новый кейс в CS:GO")
            break
        if case_fi:
            new_box_name = case_fi[0]
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
        if not new_box_name or 'Operation' in new_box_name:
            break
        if count == 20:
            count = 0
            driver.refresh()
            while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
                driver.refresh()
                sleep(1)
        driver.execute_script(console_command)
        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
        cost = 72
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
    list_of_covert = []
    list_of_classified = []
    # print(new_skins)
    if new_skins:
        for collection in new_skins.keys():
            for item in new_skins[collection]:
                if 'Collection' in collection and item[1] == 'Covert':
                    for exterior in item[2]:
                        cost = 7000
                        list_of_covert.append((item[0] + f' ({exterior})', cost, 2))

                elif 'Collection' in collection and item[1] == 'Classified':
                    for exterior in item[2]:
                        cost = 3500
                        list_of_classified.append((item[0] + f' ({exterior})', cost, 4))

                elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Covert':
                    for exterior in item[2]:
                        if exterior == 'Factory New':
                            cost = 1400
                            quan = 5
                        elif exterior == 'Minimal Wear':
                            cost = 1400
                            quan = 5
                        elif exterior == 'Field-Tested':
                            cost = 700
                            quan = 10
                        else:
                            continue
                        list_of_covert.append((item[0] + f' ({exterior})', cost, quan))

                elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Classified':
                    for exterior in item[2]:
                        if exterior == 'Factory New':
                            cost = 350
                            quan = 5
                        elif exterior == 'Minimal Wear':
                            cost = 140
                            quan = 10
                        elif exterior == 'Field-Tested':
                            cost = 140
                            quan = 10
                        else:
                            continue
                        list_of_classified.append((item[0] + f' ({exterior})', cost, quan))
    covert_workers = []
    classified_workers = []
    if list_of_covert:
        covert_worker = Thread(target=worker, args=(list_of_covert, 730, 1))
        covert_workers.append(covert_worker)
        covert_worker.start()

    if list_of_classified:
        classified_worker = Thread(target=worker, args=(list_of_classified, 0.4))
        classified_workers.append(classified_worker)
        classified_worker.start()
    covert_s = []
    class_s = []
    restr_s = []
    milsp_s = []
    if isinstance(stickers, list):

        def sticker_map(s):
            if s[1] == 'Covert':
                covert_s.append((s[0], 140, 15))
            elif s[1] == 'Classified':
                class_s.append((s[0], 70, 30))
            elif s[1] == 'Restricted':
                restr_s.append((s[0], 7, 100))
            elif s[1] == 'Mil-Spec':
                milsp_s.append((s[0], 1, 300))
            else:
                return False
        for s in stickers:
            sticker_map(s)
    sticker_workers = []
    if stickers:
        if covert_s:
            covert_sticker_worker = Thread(target=worker, args=(covert_s, 730, 0.4))
            sticker_workers.append(covert_sticker_worker)
        if class_s:
            class_sticker_worker = Thread(target=worker, args=(class_s, 730, 0.4))
            sticker_workers.append(class_sticker_worker)
        if restr_s:
            restr_sticker_worker = Thread(target=worker, args=(restr_s, 730, 0.3))
            sticker_workers.append(restr_sticker_worker)
        if milsp_s:
            milsp_sticker_worker = Thread(target=worker, args=(milsp_s, 730, 0.3))
            sticker_workers.append(milsp_sticker_worker)
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