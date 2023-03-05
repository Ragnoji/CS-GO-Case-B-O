import json.decoder
from time import sleep, perf_counter
import requests
import requests.adapters
from datetime import datetime
import os
from dotenv import load_dotenv
from accounts_pool import accounts
from bs4 import BeautifulSoup


def worker(list_of_items, game_index, slp=0, use_proxy=False):
    load_dotenv()
    steam_r = os.getenv('STEAM_REFRESH_MAIN')
    steam_s = os.getenv('STEAM_SECURE_MAIN')
    create_buy_order = 'https://steamcommunity.com/market/createbuyorder'

    # Строки на входе должны быть вида '"Name Name Name" cost(int) quantity(int)'
    proxy = {'https': 'socks5://user58497:nx0yrs@45.152.178.185:16580',
             'http': 'socks5://user58497:nx0yrs@45.152.178.185:16580'}
    session = requests.session()
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    if use_proxy:
        session.proxies.update(proxy)
    # session.headers.update(headers)
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
        'sessionid': sessionid, 'currency': '5', 'appid': game_index, 'market_hash_name': '',
        'price_total': '', 'quantity': '', 'billing_state': '', 'save_my_address': '0',
    }

    i = 0
    time_out = 0.55
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
            if not j:
                print('COOKIES EXPIRED')
                break
            print(item, j)
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
                sleep(slp)
                continue
            if j['success'] == 40:
                sleep(slp)
                continue
            sleep(slp)
        except requests.exceptions.Timeout:
            pass
        i += 1
    session.close()


def case_worker(case_name, event, slp=0):
    game_index = 730
    cost = 100
    load_dotenv()
    create_buy_order = 'https://steamcommunity.com/market/createbuyorder'

    # Строки на входе должны быть вида '"Name Name Name" cost(int) quantity(int)'
    sessions = []

    for acc in accounts:
        if event.is_set():
            return False
        steam_r = acc[0]
        steam_s = acc[1]

        session = requests.session()
        adapter = requests.adapters.HTTPAdapter(max_retries=2)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        session.cookies.set(steam_s[:steam_s.find('=')], steam_s[steam_s.find('=') + 1:], domain='steamcommunity.com', path='/')
        session.cookies.set(steam_r[:steam_r.find('=')], steam_r[steam_r.find('=') + 1:], domain='login.steampowered.com', path='/')
        resp = session.get('https://login.steampowered.com/jwt/refresh?redir=https%3A%2F%2Fsteamcommunity.com')
        with open('OUTPUT.html', 'w', encoding='utf-8') as o:
            o.write(resp.text)
        parser = BeautifulSoup(resp.text, 'html.parser')
        balance = int(float(''.join(filter(lambda s: s.isdigit() or s == '.', parser.find("a", {"id": "header_wallet_balance"}).text[:-5].replace(',', '.')))))
        if balance < 1000:
            continue
        quantity = (balance - 500) // cost
        for c in session.cookies:
            print({'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path})


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
        credentials = {
            'sessionid': sessionid, 'currency': '5', 'appid': game_index, 'market_hash_name': case_name,
            'price_total': cost * quantity * 100, 'quantity': quantity, 'billing_state': '', 'save_my_address': '0',
        }
        sessions.append({
            'steam_r': steam_r,
            'steam_s': steam_s,
            'session': session,
            'adapter': adapter,
            'sessionid': sessionid,
            'steamloginsecure': steamloginsecure,
            'headers': headers,
            'credentials': credentials,
            'balance': balance
        })

    i = 0
    time_out = 0.55

    while sessions:
        if event.is_set():
            return False
        if i == len(sessions):
            i = 0
        acc = sessions[i]
        session = acc['session']
        credentials = acc['credentials']
        try:
            resp = session.post(create_buy_order, data=credentials, timeout=time_out)
            try:
                j = resp.json()
            except json.decoder.JSONDecodeError:
                print('A Denied')
                sleep(1)
                # i += 1
                continue
            if not j:
                print('COOKIES EXPIRED')
                # i += 1
                continue
            print(i, j)
            if j['success'] == 8:
                session.headers.clear()
                session.get('https://login.steampowered.com/jwt/refresh?redir=https%3A%2F%2Fsteamcommunity.com')
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
                sessions[i]['headers'] = headers
                sessions[i]['sessionid'] = sessionid
                sessions[i]['steamloginsecure'] = steamloginsecure
                continue
            if j['success'] == 1 or j['success'] == 29:
                with open('log.txt', 'a', encoding='utf-8') as logg:
                    message = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {case_name} | Account#{i + 1}'
                    if 'buy_orderid' in j:
                        message += f' | {j["buy_orderid"]}\n'
                    logg.write(message)
                session.close()
                del sessions[i]
                sleep(slp)
                continue
            if j['success'] == 40:
                sleep(slp)
                continue
            sleep(slp)
        except requests.exceptions.Timeout:
            pass
        # i += 1
