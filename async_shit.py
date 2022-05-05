from selenium import webdriver
import pickle
from time import sleep
from selenium.webdriver.common.keys import Keys
from datetime import datetime

GAME_INDEX = 730  # 252490


def main():
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

    url = 'https://steamcommunity.com/market/listings/730/Place'

    # Строки на входе должны быть вида '"Name Name Name" cost(int) quantity(int)'
    list_of_items = open('stickers_to_parse.txt', 'r')
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

    while datetime.now().time().hour != 9 or datetime.now().time().minute != 59:
        sleep(60)

    while list_of_items:
        item = list_of_items[index]
        name = item[0]
        cost = item[1]
        quant = item[2]
        console_command = f'Market_ShowBuyOrderPopup({GAME_INDEX}, "{name}", "{name}")'

        try:
            driver.execute_script(console_command)
        except Exception:
            with open('log.txt', 'a', encoding='utf-8') as logg:
                message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | слетела кука или баганула страница\n'
                logg.write(message)
                print(message)
            driver.get(url)
            for cookie in pickle.load(open('steam_cookies', 'rb')):
                driver.add_cookie(cookie)
            driver.refresh()
            sleep(1)
            driver.execute_script(console_command)

        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
        price.send_keys(Keys.BACKSPACE * 50, f'{cost}')
        sleep(0.1)

        quantity = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_quantity"]')
        quantity.send_keys(Keys.BACKSPACE * 50, f'{quant}')
        sleep(0.1)

        accept = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_accept_ssa"]')
        accept.click()
        sleep(0.1)

        place = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_purchase"]')
        place.click()

        break_loop = False
        for _ in range(7):
            sleep(2)
            is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
            commodity_status = driver.find_element_by_xpath('//*[@id="market_buy_commodity_status"]').text

            if is_error and (
                    is_error == 'Sorry! We had trouble hearing back from the Steam servers about your order. Double check whether or not your order has actually been created or filled. If not, then please try again later.' or is_error == 'You cannot buy any items until your previous action completes.'):
                if is_error == 'You cannot buy any items until your previous action completes.':
                    break_loop = True
                    break
                index += 1
                if index == len(list_of_items):
                    index = 0
                break_loop = True
                break

            elif 'Success! Your buy order has been placed.' in commodity_status or is_error == 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
                del list_of_items[index]
                index -= 1
                with open('log.txt', 'a', encoding='utf-8') as logg:
                    message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {name} | {cost} руб | {quant}\n'
                    logg.write(message)
                    print(message)
                index += 1
                if index == len(list_of_items):
                    index = 0
                break_loop = True
                break

        if break_loop:
            driver.refresh()
            continue
    driver.close()


if __name__ == '__main__':
    main()