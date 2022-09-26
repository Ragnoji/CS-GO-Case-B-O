from time import sleep
from selenium import webdriver
from datetime import datetime
import telebot
import os
from dotenv import load_dotenv


def main():
    load_dotenv()
    token = os.getenv('AUTH_TOKEN')
    bot = telebot.TeleBot(token)
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

    url = 'https://steamcommunity.com/market/listings/730/Recoil%20Case'
    driver.get(url)
    driver.add_cookie({'domain': 'steamcommunity.com', 'expiry': 1816811435, 'httpOnly': False, 'name': 'Steam_Language', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'english'})
    driver.refresh()

    list_of_actions = []
    with open('activity_output.txt', 'a', encoding='utf-8') as file:
        while True:
            sleep(0.05)
            d = driver.find_elements_by_xpath('//*[@id="market_activity_block"]/div[4]')
            while not d:
                d = driver.find_elements_by_xpath('//*[@id="market_activity_block"]/div[4]')
            d = d[0].text
            avatar = driver.find_elements_by_xpath('//*[@id="market_activity_block"]/div[4]/span/span[1]/img')
            if d not in list_of_actions and 'purchased' in d and float(d.split()[-1][1:].replace(',', '.')) < 1.1:
                list_of_actions.append(d)
                file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' | ' + d + '\n')
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' | ' + d)
                bot.send_message(852738955, f"Recoil Case | {d}")
                bot.send_photo(852738955, avatar[0].get_attribute('src'))


if __name__ == '__main__':
    main()