from selenium import webdriver
import pickle
from time import sleep, time
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from discord.ext import commands

GAME_INDEX = 252490  # 252490


def main():
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

    url = 'https://steamcommunity.com/market/listings/730/Place'

    # Строки на входе должны быть вида '"Name Name Name" cost(int) quantity(int)'
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
    require = input('Согласны ли вы с таргетами?\n')
    if require != '':
        return

    driver.get(url)
    for cookie in pickle.load(open('steam_cookies', 'rb')):
        driver.add_cookie(cookie)
    driver.refresh()

    list_of_tabs = [driver.current_window_handle]
    for _ in range(len(list_of_items) - 1):
        sleep(2)
        driver.execute_script(f'window.open("{url}")')
        sleep(1)
        for w in driver.window_handles:
            if w not in list_of_tabs:
                list_of_tabs.append(w)
    driver.switch_to.window(list_of_tabs[0])

    bot = commands.Bot(command_prefix='>')

    @bot.event
    async def on_message(msg):
        if msg.author == bot.user:
            return
        if msg.embeds and ('Rust Item Definitions Updated' in msg.embeds[0].title or 'Rust Store' in msg.embed[0].title):
            await bot.close()

    bot.run('NjUwMzQxMTc3NTcyMTk2MzY0.GIPr5_.D_mTHc23pm_i58r-ja8LrZ2LzV10rKDvoAmleE')

    while not bot.is_closed():
        continue

    index = 0
    ti = time()
    while list_of_items:
        item = list_of_items[index]
        name = item[0]
        cost = item[1]
        quant = item[2]
        console_command = f'Market_ShowBuyOrderPopup({GAME_INDEX}, "{name}", "{name}")'

        if count_map[name] == 20:
            count_map[name] = 0
            driver.refresh()

        ti2 = time()
        print(ti2 - ti)
        ti = time()
        # driver.refresh()

        driver.execute_script(console_command)
        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
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

        quantity = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_quantity"]')
        quantity.send_keys(Keys.BACKSPACE * 20, f'{quant}')
        # sleep(0.1)

        accept = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_accept_ssa"]')
        if not accept.is_selected():
            accept.click()
        # sleep(0.1)

        place = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_purchase"]')
        place.click()
        count_map[name] += 1

        sleep(0.5)
        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        if is_error != 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
            continue

        del list_of_items[index]
        del list_of_tabs[index]

        if list_of_items:
            driver.switch_to.window(list_of_tabs[index])

        with open('log.txt', 'a', encoding='utf-8') as logg:
            message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {name} | {cost} руб | {quant}\n'
            logg.write(message)
            print(message)

    driver.close()


if __name__ == '__main__':
    main()