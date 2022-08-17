import asyncio
from selenium import webdriver
import pickle
import requests
from time import sleep
from time import perf_counter as time
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from discord.ext import commands
import os
from dotenv import load_dotenv


def worker(list_of_items, game_index, mode=0, delay=0, slp=0.3):
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

    url = 'https://steamcommunity.com/market/listings/730/Place'
    # game_index = 252490

    # Строки на входе должны быть вида '"Name Name Name" cost(int) quantity(int)'

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
    proxy = {'https': 'socks5://user58497:nx0yrs@193.160.211.84:11443',
             'http': 'socks5://user58497:nx0yrs@193.160.211.84:11443'}
    session = requests.session()
    session.headers.update(headers)
    session.get('https://steamcommunity.com/')
    driver.get(url)
    for c in session.cookies:
        print({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
        driver.add_cookie({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
    while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
        driver.refresh()
        sleep(2)
    session.close()

    list_of_tabs = [driver.current_window_handle]
    count_map = {list_of_items[0][0]: 0}
    for item in list_of_items[1:]:
        count_map[item[0]] = 0
        sleep(1)
        driver.execute_script(f'window.open("{url}")')
        while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
            driver.refresh()
            sleep(2)
        sleep(1)
        for w in driver.window_handles:
            if w not in list_of_tabs:
                list_of_tabs.append(w)
    driver.switch_to.window(list_of_tabs[0])

    if mode == 0:
        sleep(delay * 0.1)
    elif mode == -1:
        pass
    else:
        while datetime.now().hour != 3 or datetime.now().microsecond / 1000000 < 0.3:
            continue
        sleep(0.25 * delay)

    index = 0
    while list_of_items:
        item = list_of_items[index]
        name = item[0]
        cost = item[1]
        quant = item[2]
        console_command = f'Market_ShowBuyOrderPopup({game_index}, "{name}", "{name}")'

        if count_map[name] == 20:
            count_map[name] = 0
            driver.refresh()

        while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
            driver.refresh()
            sleep(1)

        driver.execute_script(console_command)
        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
        try:
            price.clear()
            price.send_keys(Keys.BACKSPACE * 20, f'{cost}')
        except Exception:
            with open('log.txt', 'a', encoding='utf-8') as logg:
                message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | слетела кука или баганула страница\n'
                logg.write(message)
            driver.get(url)
            session = requests.session()
            session.headers.update(headers)
            session.get('https://steamcommunity.com/market/')
            driver.get(url)
            for c in session.cookies:
                driver.add_cookie({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
            session.close()
            driver.refresh()
            driver.execute_script(console_command)
            price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
            price.send_keys(Keys.BACKSPACE * 20, f'{cost}')

        quantity = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_quantity"]')
        quantity.send_keys(Keys.BACKSPACE * 20, f'{quant}')

        accept = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_accept_ssa"]')
        if not accept.is_selected():
            accept.click()

        place = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_purchase"]')
        if not place.is_displayed():
            count_map[name] = 20
            continue
        place.click()
        count_map[name] += 1

        sleep(slp)
        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        if is_error != 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
            index += 1
            if index == len(list_of_items):
                index = 0
            driver.switch_to.window(list_of_tabs[index])
            continue

        del list_of_items[index]
        del list_of_tabs[index]
        if index == len(list_of_items):
            index = 0

        if list_of_items:
            driver.switch_to.window(list_of_tabs[index])

        with open('log.txt', 'a', encoding='utf-8') as logg:
            message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {name} | {cost} руб | {quant}\n'
            logg.write(message)

    driver.close()
