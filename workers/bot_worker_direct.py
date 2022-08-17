import asyncio
from time import sleep, perf_counter
import requests
import requests.adapters
from datetime import datetime
from discord.ext import commands
import os
from dotenv import load_dotenv


def worker_direct(list_of_items, game_index, mode=0, delay=0, slp=0.2):
    load_dotenv()
    steam_m = os.getenv('STEAM_AUTH_MAIN')
    steam_r = os.getenv('STEAM_REMEMBER_MAIN')
    headers = {'Host': 'steamcommunity.com',
               'Origin': 'https://steamcommunity.com',
               'Referer': 'https://steamcommunity.com/market', 'Connection': 'keep-alive',
               'Accept-Language': 'en;q=0.9,zh;q=0.8', 'Accept-Encoding': 'gzip, deflate, br',
               'Accept': '*/*',
               'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.134 YaBrowser/22.7.1.806 Yowser/2.5 Safari/537.36',
               'Cookie': f'{steam_m};{steam_r};steamCurrencyId=5'
               }
    create_buy_order = 'https://steamcommunity.com/market/createbuyorder'

    # Строки на входе должны быть вида '"Name Name Name" cost(int) quantity(int)'
    proxy = {'https': 'socks5://user58497:nx0yrs@193.160.211.84:11443',
             'http': 'socks5://user58497:nx0yrs@193.160.211.84:11443'}
    use_proxy = True
    session = requests.session()
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.headers.update(headers)
    if use_proxy:
        session.proxies.update(proxy)
    session.headers.update(headers)
    resp = session.get('https://steamcommunity.com/')
    with open('OUTPUT.html', 'w', encoding='utf-8') as o:
        o.write(resp.text)

    sessionid = [
        {'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path}
        for c in session.cookies if c.name == 'sessionid'
    ][0]['value']
    steamloginsecure = [
        {'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path}
        for c in session.cookies if c.name == 'steamLoginSecure'
    ][0]['value']
    session.headers.update({'Cookie': f"sessionid={sessionid};steamLoginSecure={steamloginsecure};" + session.headers.get('Cookie')})
    credentials = {
        'sessionid': sessionid, 'currency': '5', 'appid': game_index, 'market_hash_name': '',
        'price_total': '', 'quantity': '', 'billing_state': '', 'save_my_address': '0',
    }
    if mode == 0:
        sleep(delay * 0.2)
    elif mode == -1:
        pass
    else:
        while datetime.now().hour != 3 or datetime.now().microsecond / 1000000 < 0.5:
            continue
        sleep(0.2 * delay)

    i = 0
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
            resp = session.post(create_buy_order, data=credentials, timeout=0.6)
            t0 = perf_counter() - t0
            if t0 < 0.5:
                sleep(0.5 - t0)
            j = resp.json()
            if not j:
                print('COOKIES EXPIRED')
                break
            print(j)
            if j['success'] == 1 or j['success'] == 29:
                with open('log.txt', 'a', encoding='utf-8') as logg:
                    message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {item[0]} | {item[1]} руб | {item[2]}'
                    if 'buy_orderid' in j:
                        message += f' | {j["buy_orderid"]}\n'
                    logg.write(message)
                del list_of_items[i]
                sleep(0.3)
                continue
            if j['success'] == 40:
                sleep(0.3)
                continue
            sleep(slp)
        except requests.exceptions.Timeout:
            pass
        i += 1
    session.close()

