import asyncio
import json.decoder
from time import sleep, perf_counter
import requests
import requests.adapters
from datetime import datetime
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()


def worker_direct(list_of_items, game_index, mode=0, delay=0, slp=0, use_proxy=False, acc=0):
    load_dotenv()

    def ceil_func(x):
        if '.' not in x or len(x) - x.find('.') < 4:
            return x

        if x[x.find('.') + 3] != 0:
            return str(float(x[:x.find('.') + 3]) + 0.01)

        return x[:x.find('.') + 3]

    if acc == 0:
        currency = '5'
        steam_r = os.getenv('STEAM_REFRESH_MAIN')
        steam_s = os.getenv('STEAM_SECURE_MAIN')
    if acc == 1:
        currency = '5'
        steam_r = os.getenv('STEAM_REFRESH_PARSER')
        steam_s = os.getenv('STEAM_SECURE_PARSER')
    if acc == 2:
        currency = '24'
        steam_r = os.getenv('STEAM_REFRESH_INR1')
        steam_s = os.getenv('STEAM_SECURE_INR1')
        conversion_json = requests.get("https://api.currencyapi.com/v3/latest?apikey=g3sW8AAFzhV4ZfpiSOFyB0eVNLAi6zIdC4S27Zr5&currencies=INR&base_currency=RUB").json()
        conversion = conversion_json["data"]["INR"]["value"]
        list_of_items = [[s[0], ceil_func(str(float(s[1]) * conversion)), s[2]] for s in list_of_items]
    create_buy_order = 'https://steamcommunity.com/market/createbuyorder'

    # Строки на входе должны быть вида '"Name Name Name" cost(int) quantity(int)'
    proxy = {'https': 'socks5://user58497:nx0yrs@213.139.228.116:6735',
             'http': 'socks5://user58497:nx0yrs@213.139.228.116:6735'}
    session = requests.session()
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.cookies.set(steam_s[:steam_s.find('=')], steam_s[steam_s.find('=') + 1:], domain='steamcommunity.com', path='/')
    session.cookies.set(steam_r[:steam_r.find('=')], steam_r[steam_r.find('=') + 1:], domain='login.steampowered.com', path='/')
    resp = session.get('https://login.steampowered.com/jwt/refresh?redir=https%3A%2F%2Fsteamcommunity.com')
    for c in session.cookies:
        print({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
    with open('OUTPUT.html', 'w', encoding='utf-8') as o:
        o.write(resp.text)
    print(f"{list_of_items}, use_proxy={use_proxy}")

    sessionid = [
        {'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path}
        for c in session.cookies if c.name == 'sessionid'
    ][0]['value']
    steamloginsecure = [
        c.name + '=' + c.value
        for c in session.cookies if c.name == 'steamLoginSecure'
    ][0]
    # print(sessionid)
    # print(steamloginsecure)
    headers = {'Host': 'steamcommunity.com',
               'Origin': 'https://steamcommunity.com',
               'Referer': 'https://steamcommunity.com/market', 'Connection': 'keep-alive',
               'Accept-Language': 'en;q=0.9,zh;q=0.8', 'Accept-Encoding': 'gzip, deflate, br',
               'Accept': '*/*',
               'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.134 YaBrowser/22.7.1.806 Yowser/2.5 Safari/537.36',
               'Cookie': f'sessionid={sessionid};{steamloginsecure};steamCurrencyId=5'
               }
    session.headers.update(headers)
    credentials = {
        'sessionid': sessionid, 'currency': currency, 'appid': game_index, 'market_hash_name': '',
        'price_total': '', 'quantity': '', 'billing_state': '', 'save_my_address': '0',
    }
    if mode == 0:
        pass
    elif mode == -1:
        pass
    elif mode == 1:
        while datetime.now().hour != 9 or datetime.now().minute != 59 or datetime.now().second < 59 or datetime.now().microsecond / 1000000 < 0.5:
            sleep(0.05)
    else:
        while datetime.now().hour != 2 or datetime.now().minute != 59 or datetime.now().second != 59 or datetime.now().microsecond / 1000000 < 0.95:
            sleep(0.01)
        sleep(0.15 * delay)

    i = 0
    time_out = 0.5
    while list_of_items:
        if i == len(list_of_items):
            i = 0
        item = list_of_items[i]
        credentials['market_hash_name'] = item[0]
        credentials['price_total'] = int(float(item[1]) * 100) * int(item[2])
        credentials['quantity'] = item[2]
        try:
            if use_proxy:
                session.proxies.update(proxy)
            t0 = perf_counter()
            resp = session.post(create_buy_order, data=credentials, timeout=time_out)
            t0 = perf_counter() - t0
            if t0 < time_out:
                sleep(time_out - t0)
            try:
                j = resp.json()
            except json.decoder.JSONDecodeError:
                print('A Denied')
                sleep(3)
                i += 1
                continue
            print(j)
            if not j:
                print('COOKIES EXPIRED')
                break
            # print(t0, j, item)
            if j['success'] == 8:
                # for c in session.cookies:
                #     print({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
                # print('---')
                session.headers.clear()
                session.get('https://login.steampowered.com/jwt/refresh?redir=https%3A%2F%2Fsteamcommunity.com')
                # for c in session.cookies:
                #     print({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})
                sessionid = [
                    {'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path}
                    for c in session.cookies if c.name == 'sessionid'
                ][0]['value']
                steamloginsecure = [
                    c.name + '=' + c.value
                    for c in session.cookies if c.name == 'steamLoginSecure'
                ][0]
                headers = {'Host': 'steamcommunity.com',
                           'Origin': 'https://steamcommunity.com',
                           'Referer': 'https://steamcommunity.com/market', 'Connection': 'keep-alive',
                           'Accept-Language': 'en;q=0.9,zh;q=0.8', 'Accept-Encoding': 'gzip, deflate, br',
                           'Accept': '*/*',
                           'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.134 YaBrowser/22.7.1.806 Yowser/2.5 Safari/537.36',
                           'Cookie': f'sessionid={sessionid};{steamloginsecure};steamCurrencyId=5'
                           }
                session.headers.update(headers)
                credentials['sessionid'] = sessionid
                continue
            if j['success'] == 1 or j['success'] == 29:
                with open('log.txt', 'a', encoding='utf-8') as logg:
                    message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {item[0]} | {item[1]} руб | {item[2]}'
                    if 'buy_orderid' in j:
                        message += f' | {j["buy_orderid"]}\n'
                    logg.write(message)
                del list_of_items[i]
                # sleep(0.1)
                continue
            if j['success'] == 40:
                sleep(slp)
                i += 1
                continue
            sleep(slp)
        except requests.exceptions.Timeout:
            pass
        i += 1
    session.close()

