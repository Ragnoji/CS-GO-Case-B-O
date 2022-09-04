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


def worker(list_of_items, game_index=730, mode=0, delay=0, slp=0.5):
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)
    driver.get('https://steamcommunity.com/login/home/?goto=')
    t = input('Введи 1, когда авторизуешься')
    while t != '1':
        t = input('Некорректный ввод')
    url = 'https://steamcommunity.com/market/listings/730/Place'

    driver.get(url)
    while not driver.find_elements_by_xpath('//*[@id="header_wallet_balance"]'):
        driver.refresh()
        sleep(2)
        continue
    # session.close()

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
        sleep(delay * 0.2)
    elif mode == -1:
        pass
    else:
        while datetime.now().hour != 3 or datetime.now().microsecond / 1000000 < 0.2:
            continue
        sleep(0.2 * delay)

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
            driver.get('https://steamcommunity.com/login/home/?goto=steamcommunity.com/market/listings/730/Place')
            t = input('Введи 1, когда авторизуешься')
            while t != '1':
                t = input('Некорректный ввод')
            driver.get(url)
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


if __name__ == '__main__':
    name = input('Введи название предмета\n')
    cost = input('Введи цену\n')
    quantity = input('Введи количество\n')
    worker([[name, cost, quantity]])