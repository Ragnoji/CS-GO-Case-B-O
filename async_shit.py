from selenium import webdriver
import pickle
from time import sleep
from selenium.webdriver.common.keys import Keys
from datetime import datetime

GAME_INDEX = 252490


def main():
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

    url = 'https://steamcommunity.com/market/listings/730/Dreams%20%26%20Nightmares%20Case'

    # Строки на входе должны быть вида '"Name Name Name" cost(int) quantity(int)'
    list_of_items = open('target_items.txt', 'r')
    list_of_items = list_of_items.readlines()

    if not list_of_items:
        print('create "target_items.txt" file with inputs')
        return

    list_of_items = [item_line.strip().split() for item_line in list_of_items]
    for i in range(len(list_of_items)):
        tmp = list_of_items[i]
        for g, v in enumerate(tmp):
            if v.endswith('"'):
                list_of_items[i] = [''.join(' '.join(tmp[:g + 1])[1:-1])] + tmp[g + 1:]

    print(*list_of_items)
    require = input('Согласны ли вы с таргетами?\n')
    if require != '':
        return

    driver.get(url)
    for cookie in pickle.load(open('steam_cookies', 'rb')):
        driver.add_cookie(cookie)
    driver.refresh()

    index = 0
    accept_terms_flag = True
    while list_of_items:
        item = list_of_items[index]
        name = item[0]
        cost = item[1]
        quant = item[2]
        console_command = f'Market_ShowBuyOrderPopup({GAME_INDEX}, "{name}", "{name}")'

        driver.execute_script(console_command)
        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
        price.send_keys(Keys.BACKSPACE * 50, f'{cost}')
        sleep(0.1)

        quantity = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_quantity"]')
        quantity.send_keys(Keys.BACKSPACE * 50, f'{quant}')
        sleep(0.1)

        if accept_terms_flag:
            accept = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_accept_ssa"]')
            accept.click()
            sleep(0.1)
            accept_terms_flag = False

        place = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_purchase"]')
        place.click()
        sleep(2)

        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        if is_error and (is_error == 'Sorry! We had trouble hearing back from the Steam servers about your order. Double check whether or not your order has actually been created or filled. If not, then please try again later.' or is_error == 'You cannot buy any items until your previous action completes.'):
            index += 1
            if index == len(list_of_items):
                index = 0
            if is_error == 'You cannot buy any items until your previous action completes.':
                accept_terms_flag = True
                driver.refresh()
            continue
        sleep(10)

        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        print(is_error)

        if not is_error or is_error == 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
            del list_of_items[index]
            index -= 1
            accept_terms_flag = True
            driver.refresh()
            with open('log.txt', 'a', encoding='utf-8') as logg:
                message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {name} | {cost} руб | {quant}'
                logg.write(message)
                print(message)

        index += 1
        if index == len(list_of_items):
            index = 0


if __name__ == '__main__':
    main()