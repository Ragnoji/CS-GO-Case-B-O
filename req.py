import requests
from re import search
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import vlc
import pickle
from datetime import datetime
from threading import Thread
from differ_items import differ
from weapon_parser import new_weapons
from worker_template import worker


def check_case_update():
    past = ['Prisma 2 Case', 'Prisma Case', 'Fracture Case', 'Danger Zone Case', 'Snakebite Case', 'Horizon Case',
            'CS20 Case', 'Revolver Case', 'Falchion Case', 'Shadow Case', 'Clutch Case', 'Operation Wildfire Case',
            'Chroma 3 Case', 'Spectrum 2 Case', 'Gamma Case', 'Chroma 2 Case', 'Gamma 2 Case',
            'Operation Vanguard Weapon Case', 'Spectrum Case', 'Chroma Case', 'Dreams & Nightmares Case',
            'Operation Phoenix Weapon Case', 'Shattered Web Case', 'Operation Broken Fang Case',
            'Operation Riptide Case', 'Glove Case', 'Operation Breakout Weapon Case', 'eSports 2014 Summer Case',
            'Huntsman Weapon Case', 'Winter Offensive Weapon Case', 'CS:GO Weapon Case 3', 'CS:GO Weapon Case 2',
            'CS:GO Weapon Case', 'eSports 2013 Winter Case', 'Operation Hydra Case', 'eSports 2013 Case',
            'Operation Bravo Case']
    box_name = differ.differ()
    if box_name and 'Case' in box_name[0] and '|' not in box_name[0] and box_name[0] not in past:
        return box_name[0], box_name[1:]
    return False, box_name


def loop_alarm():
    p = vlc.MediaPlayer("alarm.mp3")
    p.play()
    while True:
        sleep(1)
        if not p.is_playing():
            p = vlc.MediaPlayer("alarm.mp3")
            p.play()


def main():
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

    url = f'https://steamcommunity.com/market/listings/730/Place'
    driver.get(url)
    list_of_knives = open('knives_to_parse.txt', 'r', encoding='utf-8')
    list_of_knives = list_of_knives.readlines()

    if not list_of_knives:
        print('create "target_items.txt" file with inputs')

    list_of_knives = [item_line.strip().split() for item_line in list_of_knives]
    count_knives = dict()
    for i in range(len(list_of_knives)):
        tmp = list_of_knives[i]
        for g, v in enumerate(tmp):
            if v.endswith('"'):
                list_of_knives[i] = [''.join(' '.join(tmp[:g + 1])[1:-1])] + tmp[g + 1:]
                count_knives[list_of_knives[i][0]] = 0
    print(*list_of_knives)
    if input('Согласны с таргетами?') != '':
        return
    driver.get(url)
    for cookie in pickle.load(open('steam_cookies', 'rb')):
        driver.add_cookie(cookie)
    driver.refresh()

    new_box_name, stickers = check_case_update()
    while not new_box_name and not stickers:
        new_box_name, stickers = check_case_update()
        sleep(1)
    Thread(target=loop_alarm).start()
    is_operation = False
    if isinstance(new_box_name, str) and 'Operation' in new_box_name:
        new_box_name = False
        is_operation = True
    console_command = f'Market_ShowBuyOrderPopup(730, "{new_box_name}", "{new_box_name}")'
    print(f'NEW CASE RELEASE\nCommand for fast buy:\n{console_command}')
    count = 0
    while True:
        if not new_box_name:
            break
        if count == 20:
            driver.refresh()
        driver.execute_script(console_command)
        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
        cost = 67
        try:
            price.send_keys(Keys.BACKSPACE * 20, f'{cost}')
        except Exception:
            with open('log.txt', 'a', encoding='utf-8') as logg:
                message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | слетела кука или баганула страница\n'
                logg.write(message)
                print(message)
            driver.get(url)
            for cookie in pickle.load(open('steam_cookies', 'rb')):
                driver.add_cookie(cookie)
            driver.refresh()
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
        accept.click()
        # sleep(0.1)

        place = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_purchase"]')
        place.click()
        sleep(0.45)
        count += 1

        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        if is_error != 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
            continue

        with open('log.txt', 'a', encoding='utf-8') as logg:
            message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {new_box_name} | {cost} руб | {quant}\n'
            logg.write(message)
            print(message)
        break

    current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
    old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
    current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()
    new_skins = new_weapons(current_items, old_items, current_names)
    list_of_covert = []
    list_of_classified = []
    if new_skins:
        for collection in new_skins.keys():
            for item in new_skins[collection]:
                if 'Collection' in collection and item[1] == 'Covert':
                    for exterior in item[2]:
                        cost = 8000
                        list_of_covert.append((item[0] + f' ({exterior})', cost, 4))

                elif 'Collection' in collection and item[1] == 'Classified':
                    for exterior in item[2]:
                        cost = 3000
                        list_of_classified.append((item[0] + f' ({exterior})', cost, 6))

                elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Covert':
                    for exterior in item[2]:
                        if exterior == 'Factory New':
                            cost = 500
                        elif exterior == 'Minimal Wear':
                            cost = 200
                        else:
                            cost = 100
                        list_of_covert.append((item[0] + f' ({exterior})', cost, 20))

                elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Classified':
                    for exterior in item[2]:
                        if exterior == 'Factory New':
                            cost = 400
                        elif exterior == 'Minimal Wear':
                            cost = 220
                        elif exterior == 'Field-Tested':
                            cost = 145
                        else:
                            cost = 75
                        list_of_classified.append((item[0] + f' ({exterior})', cost, 20))
    if list_of_covert:
        covert_worker = Thread(target=worker, args=(list_of_covert, 2.5))
        covert_worker.start()

    if list_of_classified:
        classified_worker = Thread(target=worker, args=(list_of_classified, 2.5))
        classified_worker.start()

    stickers = list(map(lambda s: (s, 10, 100) if 'Holo' in s else (s, 75, 25),
                        filter(lambda s: 'Holo' in s or 'Gold' in s, stickers)))
    if stickers:
        sticker_worker = Thread(target=worker, args=(stickers, 1))
        sticker_worker.start()

    if new_box_name or is_operation:
        knives_worker = Thread(target=worker, args=(list_of_knives, 3))
        knives_worker.start()

    if stickers:
        sticker_worker.join()
    if new_box_name or is_operation:
        knives_worker.join()
    if list_of_covert:
        covert_worker.join()
    if list_of_classified:
        classified_worker.join()
    driver.close()


if __name__ == '__main__':
    main()