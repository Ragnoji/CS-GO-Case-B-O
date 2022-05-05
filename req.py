import requests
from re import search
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import vlc
import pickle
from datetime import datetime


def check_case_update(page=1):
    response = requests.get(
        f'https://blog.counter-strike.net/index.php/category/updates/page/{page}/',
    )
    text = response.text
    recent_post = search(r'the .*[A-Z].+Case', text)
    box_name = False
    if recent_post:
        box_name = recent_post[0].replace('#038;', '')[4:]
        box_name = box_name[:box_name.find('Case') + 4]
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

    url = f'https://steamcommunity.com/market/listings/730/Dreams%20%26%20Nightmares%20Case'
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

    url = f'https://steamcommunity.com/market/listings/730/{new_box_name}'
    console_command = f'Market_ShowBuyOrderPopup(730, "{new_box_name}", "{new_box_name}")'
    print(f'NEW CASE RELEASE\nCommand for fast buy:\n{console_command}')
    # driver.get(url)
    # driver.refresh()
    accept_terms_flag = True
    while True:
        driver.execute_script(f'Market_ShowBuyOrderPopup(730, "{new_box_name}", "{new_box_name}")')
        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
        balance_element = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_walletbalance_amount"]').text
        balance = int(balance_element.split('руб')[0].split(',')[0])
        cost = 84  # рублей
        quant = balance // cost
        price.send_keys(Keys.BACKSPACE*50, f'{cost}')
        sleep(0.1)
        quantity = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_quantity"]')
        quantity.send_keys(Keys.BACKSPACE*50, f'{quant}')
        sleep(0.1)

        if accept_terms_flag:
            accept = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_accept_ssa"]')
            accept.click()
            sleep(0.1)
            accept_terms_flag = False

        place = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_purchase"]')
        place.click()
        break_loop = False
        for _ in range(2):
            sleep(3)
            is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
            if is_error and (
                    is_error == 'Sorry! We had trouble hearing back from the Steam servers about your order. Double check whether or not your order has actually been created or filled. If not, then please try again later.' or is_error == 'You cannot buy any items until your previous action completes.'):
                if is_error == 'You cannot buy any items until your previous action completes.':
                    break_loop = True
                    break
                break_loop = True
                break

        if break_loop:
            continue

        for _ in range(7):
            is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
            commodity_status = driver.find_element_by_xpath('//*[@id="market_buy_commodity_status"]').text
            print(commodity_status)

            if 'Success! Your buy order has been placed.' in commodity_status or is_error == 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
                with open('log.txt', 'a', encoding='utf-8') as logg:
                    message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {new_box_name} | {cost} руб | {quant}\n'
                    logg.write(message)
                    print(message)
                break_loop = True
                break
            sleep(1)

        if break_loop:
            break

    loop_alarm()

