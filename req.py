import requests
from re import search
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import vlc
import pickle


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

    req_time = 10
    print('Checking for case update...')
    new_box_name = check_case_update()
    while not new_box_name:
        sleep(req_time)
        print('Checking for case update...')
        new_box_name = check_case_update()

    url = f'https://steamcommunity.com/market/listings/730/{new_box_name}'
    console_command = f'Market_ShowBuyOrderPopup(730, "{new_box_name}", "{new_box_name}")'
    print(f'NEW CASE RELEASE\nCommand for fast buy:\n{console_command}')
    driver.get(url)
    for cookie in pickle.load(open('steam_cookies', 'rb')):
        driver.add_cookie(cookie)

    while True:
        driver.refresh()
        sleep(1)

        driver.execute_script(f'Market_ShowBuyOrderPopup(730, "{new_box_name}", "{new_box_name}")')
        price = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_price"]')
        price.send_keys(Keys.BACKSPACE*50, '1')
        sleep(0.1)
        quantity = driver.find_element_by_xpath('//*[@id="market_buy_commodity_input_quantity"]')
        quantity.send_keys(Keys.BACKSPACE*50,'2')
        sleep(0.1)
        accept = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_accept_ssa"]')
        accept.click()
        sleep(0.1)
        place = driver.find_element_by_xpath('//*[@id="market_buyorder_dialog_purchase"]')
        place.click()
        sleep(15)

        is_error = driver.find_element_by_id('market_buyorder_dialog_error_text').text
        print(is_error)
        if not is_error or is_error == 'You already have an active buy order for this item. You will need to either cancel that order, or wait for it to be fulfilled before you can place a new order.':
            break

    loop_alarm()

