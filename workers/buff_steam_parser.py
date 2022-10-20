from time import sleep, perf_counter
import requests
import telebot
import requests.adapters
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


def work(min_price=2000, max_price=10000):
    load_dotenv()
    steam_r = os.getenv('STEAM_REFRESH_MAIN')
    steam_s = os.getenv('STEAM_SECURE_MAIN')

    # Строки на входе должны быть вида '"Name Name Name" cost(int) quantity(int)'
    proxy = {'https': 'socks5://user58497:nx0yrs@45.152.178.185:16580',
             'http': 'socks5://user58497:nx0yrs@45.152.178.185:16580'}
    no_proxy = {
        'https': '',
        'http': ''
    }
    use_proxy = True
    proxy_switch = False
    steam_session = requests.session()
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    steam_session.mount('https://', adapter)
    steam_session.mount('http://', adapter)
    steam_session.cookies.set(steam_s[:steam_s.find('=')], steam_s[steam_s.find('=') + 1:], domain='steamcommunity.com', path='/')
    steam_session.cookies.set(steam_r[:steam_r.find('=')], steam_r[steam_r.find('=') + 1:], domain='login.steampowered.com', path='/')
    resp = steam_session.get('https://login.steampowered.com/jwt/refresh?redir=https%3A%2F%2Fsteamcommunity.com')
    for c in steam_session.cookies:
        print({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
    with open('OUTPUT.html', 'w', encoding='utf-8') as o:
        o.write(resp.text)
    sessionid = [
        {'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path}
        for c in steam_session.cookies if c.name == 'sessionid'
    ][0]['value']
    steamloginsecure = [
        c.name + '=' + c.value
        for c in steam_session.cookies if c.name == 'steamLoginSecure'
    ][0]
    headers = {'Host': 'steamcommunity.com',
               'Origin': 'https://steamcommunity.com',
               'Referer': 'https://steamcommunity.com/market', 'Connection': 'keep-alive',
               'Accept-Language': 'en;q=0.9,zh;q=0.8', 'Accept-Encoding': 'gzip, deflate, br',
               'Accept': '*/*',
               'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.134 YaBrowser/22.7.1.806 Yowser/2.5 Safari/537.36',
               'Cookie': f'sessionid={sessionid};{steamloginsecure};steamCurrencyId=5'
               }
    steam_session.headers.update(headers)

    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    buff_session = webdriver.Chrome(binary_yandex_driver_file, options=options)

    token = os.getenv('AUTH_TOKEN')
    bot = telebot.TeleBot(token)
    i = 0
    max_i = 100

    resp = buff_session.get(f'https://buff.163.com/market/csgo#tab=selling&page_num=1&min_price={min_price}'
                            f'&max_price={max_price}&quality=normal&sort_by=price.asc')
    buff_session.add_cookie(
        {"name": "session", "value": os.getenv("BUFF_SESSION"), "domain": 'buff.163.com', "path": '/'})
    buff_session.refresh()

    for c in buff_session.get_cookies():
        print({'name': c['name'], 'value': c['value'], 'domain': c['domain'], 'path': c['path']})

    sort_b = buff_session.find_element_by_xpath("/html/body/div[5]/div[1]/div[3]/div[1]/div[3]/h3")
    while not sort_b:
        sort_b = buff_session.find_element_by_xpath("/html/body/div[5]/div[1]/div[3]/div[1]/div[3]/h3")
    sort_b.click()

    asc_b = buff_session.find_element_by_xpath("/html/body/div[5]/div[1]/div[3]/div[1]/div[3]/ul/li[2]/h6/span")
    while not asc_b:
        asc_b = buff_session.find_element_by_xpath("/html/body/div[5]/div[1]/div[3]/div[1]/div[3]/ul/li[2]/h6/span")
    asc_b.click()

    while i != max_i:
        sleep(4)
        cards = buff_session.find_elements_by_xpath('//*[@id="j_list_card"]/ul/li')
        while not cards:
            cards = buff_session.find_elements_by_xpath('//*[@id="j_list_card"]/ul/li')
            sleep(0.5)
        max_i = int(buff_session.find_element_by_css_selector("div.pager.card-pager.light-theme.simple-pagination > ul > li:nth-child(12) > a").text)
        for card in cards:
            name = card.find_element_by_css_selector('h3 > a').get_attribute('title')
            cost_raw = card.find_element_by_css_selector('p > strong').text
            cost = float(cost_raw.strip()[2:])
            if proxy_switch:
                steam_session.proxies.update(no_proxy)
                proxy_switch = False
            else:
                if use_proxy:
                    steam_session.proxies.update(proxy)
            item_page = steam_session.get(f'https://steamcommunity.com/market/listings/730/{name}')
            prices = re.findall(r'var g_rgListingInfo = \{.*\}', item_page.text)

            while not prices:
                sleep(4)
                if proxy_switch:
                    steam_session.proxies.update(no_proxy)
                    proxy_switch = False
                else:
                    if use_proxy:
                        steam_session.proxies.update(proxy)
                item_page = steam_session.get(f'https://steamcommunity.com/market/listings/730/{name}')
                prices = re.findall(r'var g_rgListingInfo = \{.*\}', item_page.text)
            while not prices or ('converted_price' not in list(json.loads(prices[0][22:]).items())[0][1].keys() or
                                 'converted_fee' not in list(json.loads(prices[0][22:]).items())[0][1].keys()):
                print('?')
                sleep(4)
                while True:
                    try:
                        if proxy_switch:
                            steam_session.proxies.update(no_proxy)
                            proxy_switch = False
                        else:
                            if use_proxy:
                                steam_session.proxies.update(proxy)
                        item_page = steam_session.get(f'https://steamcommunity.com/market/listings/730/{name}')
                        break
                    except requests.exceptions.ConnectionError:
                        continue
                prices = re.findall(r'var g_rgListingInfo = \{.*\}', item_page.text)

            prices = list(json.loads(prices[0][22:]).items())[0][1]
            steam_price = (prices['converted_price'] + prices['converted_fee']) / 100

            with open('item_page.html', 'w', encoding='utf-8') as o:
                o.write(item_page.text)
            if cost / steam_price < 0.7 and i > 3:
                soup = BeautifulSoup(item_page.text, 'lxml')
                item_img = soup.select("div.market_listing_largeimage > img")[0]["src"] + '.png'
                bot.send_message(852738955, f'<a href="https://steamcommunity.com/market/listings/730/{name}">{name}</a> {cost} руб {steam_price} руб\n'
                                            f"{cost / steam_price}\n"                                        
                                            f'<a href="{item_img}"></a>', parse_mode="HTML")
            sleep(4)
            print(name, cost, steam_price, cost/steam_price)
        next_page = buff_session.find_element_by_xpath('//*[@id="j_market_card"]/div[2]/ul/li[14]/a').click()
        i += 1

    steam_session.close()
    buff_session.close()


if __name__ == '__main__':
    work()
