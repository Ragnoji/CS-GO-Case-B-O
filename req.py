import requests
from re import search
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import vlc
import pickle
from datetime import datetime
from bs4 import BeautifulSoup


def check_case_update(page=1):
    response = requests.get(
        f'https://blog.counter-strike.net/index.php/category/updates/page/{page}/',
    )
    recent_post = BeautifulSoup(response.text, features='lxml')
    recent_post = recent_post.find("div", "inner_post").getText()
    text = search(r'the .*[A-Z].+Case', recent_post)
    if not text:
        text = search(r'The .*[A-Z].+Case', recent_post)
    box_name = False
    if text:
        box_name = text[0]
        box_name = box_name[:box_name.find('Case') + 4]
        box_name = box_name.replace('#038;', '')[4:]
        box_name = box_name.replace(' Weapon', '')
        box_name = ' '.join(filter(lambda w: w[0].isupper() or w[0].isdigit() or w[0] == '&', box_name.split()))
        if box_name.find('Operation') != -1:
            box_name = False

    if not box_name:
        text = search(r'the .*[A-Z].+Collection', recent_post)
        if not text:
            text = search(r'The .*[A-Z].+Collection', recent_post)
        box_name = False
        if text:
            box_name = text[0]
            box_name = box_name[:box_name.find('Collection') - 1]
            box_name += ' Case'
            box_name = box_name.replace('#038;', '')[4:]
            box_name = box_name.replace(' Weapon', '')
            box_name = ' '.join(filter(lambda w: w[0].isupper() or w[0].isdigit() or w[0] == '&', box_name.split()))
            if box_name.find('Operation') != -1:
                box_name = False
    return box_name


def loop_alarm():
    p = vlc.MediaPlayer("alarm.mp3")
    p.play()
    while True:
        sleep(1)
        if not p.is_playing():
            p = vlc.MediaPlayer("alarm.mp3")
            p.play()


if __name__ == '__main__':
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

    url = f'https://steamcommunity.com/market/listings/730/Place'
    driver.get(url)
    for cookie in pickle.load(open('steam_cookies', 'rb')):
        driver.add_cookie(cookie)
    driver.refresh()

    req_time = 2
    print('Checking for case update...')
    new_box_name = check_case_update()
    while not new_box_name:
        sleep(req_time)
        print('Checking for case update...')
        new_box_name = check_case_update()

    console_command = f'Market_ShowBuyOrderPopup(730, "{new_box_name}", "{new_box_name}")'
    print(f'NEW CASE RELEASE\nCommand for fast buy:\n{console_command}')
    while True:
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
            driver.execute_script(console_command)
        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
        balance_element = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_walletbalance_amount"]').text
        balance = int(balance_element.split('руб')[0].split(',')[0])
        cost = 100  # рублей
        quant = balance // cost
        price.send_keys(Keys.BACKSPACE*50, f'{cost}')
        # sleep(0.1)
        quantity = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_quantity"]')
        quantity.send_keys(Keys.BACKSPACE*50, f'{quant}')
        # sleep(0.1)

        accept = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_accept_ssa"]')
        accept.click()
        # sleep(0.1)

        place = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_purchase"]')
        place.click()
        sleep(0.5)

        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        if is_error != 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
            driver.refresh()
            sleep(1)
            continue

        with open('log.txt', 'a', encoding='utf-8') as logg:
            message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {new_box_name} | {cost} руб | {quant}\n'
            logg.write(message)
            print(message)
        break

    loop_alarm()

