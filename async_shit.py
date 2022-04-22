from selenium import webdriver
import pickle
from time import sleep
from selenium.webdriver.common.keys import Keys

GAME_INDEX = 252490


def main():
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

    url = 'https://steamcommunity.com/market/listings/730/Dreams%20%26%20Nightmares%20Case'

    list_of_items = open('target_items.txt', 'r')
    list_of_items = [tuple(item_line.strip().split()) for item_line in list_of_items.readlines()]
    driver.get(url)
    for cookie in pickle.load(open('steam_cookies', 'rb')):
        driver.add_cookie(cookie)
    driver.refresh()

    index = 0
    while list_of_items:
        item = list_of_items[index]
        name = item[0]
        cost = item[1]
        quant = item[2]
        console_command = f'Market_ShowBuyOrderPopup({GAME_INDEX}, "{name}", "{name}")'
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
        sleep(2)
        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        if not is_error or is_error == 'Sorry! We had trouble hearing back from the Steam servers about your order. Double check whether or not your order has actually been created or filled. If not, then please try again later.':
            index += 1
            if index == len(list_of_items):
                index = 0
            continue
        sleep(5)

        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        print(is_error)
        if not is_error or is_error == 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
            driver.execute_script('window.close();')
            del list_of_items[index]
            index -= 1
        index += 1
        if index == len(list_of_items):
            index = 0


if __name__ == '__main__':
    main()