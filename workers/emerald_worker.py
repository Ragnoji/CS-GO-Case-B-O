import requests
import requests.adapters
import re
import datetime
from time import sleep, perf_counter
import json
from selenium import webdriver
from bs4 import BeautifulSoup
import pickle
import telebot
import os
from dotenv import load_dotenv


def listings_worker(list_of_items):
    load_dotenv()
    # credentials = {
    #     'sessionid': '847ce3b4942e55e812f7e115', 'currency': '5', 'appid': '730', 'market_hash_name': 'Chroma Case',
    #     'price_total': '100', 'quantity': '1', 'billing_state': '', 'save_my_address': '0',
    # }
    steam_r = os.getenv('STEAM_REFRESH_MAIN')
    steam_s = os.getenv('STEAM_SECURE_MAIN')
    proxy = {'https': 'socks5://user58497:nx0yrs@193.160.211.84:11443',
             'http': 'socks5://user58497:nx0yrs@193.160.211.84:11443'}
    no_proxy = {
        'https': '',
        'http': ''
    }
    float_url = 'https://api.csgofloat.com/'
    item_url = 'https://steamcommunity.com/market/listings/730/'
    use_proxy = True
    session = requests.session()
    adapter = requests.adapters.HTTPAdapter(max_retries=2)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.cookies.set(steam_s[:steam_s.find('=')], steam_s[steam_s.find('=') + 1:], domain='steamcommunity.com',
                        path='/')
    session.cookies.set(steam_r[:steam_r.find('=')], steam_r[steam_r.find('=') + 1:], domain='login.steampowered.com',
                        path='/')
    # session.headers.update(headers)
    if use_proxy:
        session.proxies.update(proxy)
    while True:
        try:
            resp = session.get('https://steamcommunity.com/')
            break
        except requests.ConnectionError:
            continue
    headers = {'Host': 'steamcommunity.com',
               'Origin': 'https://steamcommunity.com',
               'Referer': 'https://steamcommunity.com/market', 'Connection': 'keep-alive',
               'Accept-Language': 'en;q=0.9,zh;q=0.8', 'Accept-Encoding': 'gzip, deflate, br',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.134 YaBrowser/22.7.1.806 Yowser/2.5 Safari/537.36',
               'Cookie': f'steamCurrencyId=5'
               }
    for c in session.cookies:
        headers['Cookie'] += f';{c.name}={c.value}'
        print(c)
    session.headers.update(headers)
    query_settings = '?query=&start=0&count=100&country=RU&language=english&currency=5'
    item_cache = dict()
    if os.path.isfile('emerald_item_cache'):
        item_cache = pickle.load(open('emerald_item_cache', 'rb'))

    token = os.getenv('AUTH_TOKEN')
    bot = telebot.TeleBot(token)

    # exteriors_to_check = ['Battle-Scarred', 'Well-Worn', 'Field-Tested', 'Minimal Wear', 'Factory New']
    id = 0
    proxy_switch = False
    while True:
        t1 = perf_counter()
        if id == len(list_of_items):
            id = 0
            print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | sleeping 4.0 sec')
            with open('emerald_item_cache', 'wb') as ch:
                pickle.dump(item_cache, ch)
            sleep(1)
        item = list_of_items[id]
        limit = item[1]
        limit_p4 = item[2]
        item = item[0]
        print(item)
        if item not in item_cache.keys():
            item_cache[item] = []
        # driver.get(item_url + item + query_settings)
        t0 = perf_counter()
        while True:
            try:
                if proxy_switch:
                    session.proxies.update(no_proxy)
                    proxy_switch = False
                else:
                    if use_proxy:
                        session.proxies.update(proxy)
                    proxy_switch = True
                resp = session.get(item_url + item + query_settings, headers=headers)
                t0 = perf_counter() - t0
                break
            except requests.ConnectionError:
                continue
        if t0 < 6:
            sleep(6 - t0)
        resp = resp.text
        soup = BeautifulSoup(resp, "html.parser")
        r = re.findall(r'var g_rgAssets = \{.*\}', resp)
        prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
        if not r or not prices:
            print('>')
            id += 1
            if t0 < 6:
                sleep(6 - t0)
            sleep(2)
            continue
        while (not r or not prices) or ('converted_price' not in list(json.loads(prices[0][22:]).items())[0][1].keys()):
            print('?')
            for c in session.cookies:
                print(c)
            t0 = perf_counter()
            while True:
                try:
                    if proxy_switch:
                        session.proxies.update(no_proxy)
                        proxy_switch = False
                    else:
                        if use_proxy:
                            session.proxies.update(proxy)
                        proxy_switch = True
                    resp = session.get(item_url + item + query_settings, headers=headers)
                    t0 = perf_counter() - t0
                    break
                except requests.ConnectionError:
                    continue
            resp = resp.text
            with open('OUTPUT.html', 'w', encoding='utf-8') as o:
                o.write(resp)
            soup = BeautifulSoup(resp, "html.parser")
            r = re.findall(r'var g_rgAssets = \{.*\}', resp)
            prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
            if t0 < 6:
                sleep(6 - t0)
        prices = json.loads(prices[0][22:])
        for p in prices.keys():
            if prices[p]['fee'] == 0 or 'converted_price' not in prices[p].keys():
                continue
            prices[p] = (prices[p]['converted_price'] + prices[p]['converted_fee']) / 100
        buttons = soup.find_all("a", {"class": "item_market_action_button btn_green_white_innerfade btn_small"})
        context_market = dict()
        for b in buttons:
            tmp = b['href']
            tmp = tmp[tmp.find('(') + 1:tmp.find(')')].split(', ')
            if tmp[1][1:-1] not in prices.keys():
                item_cache[item].append(tmp[4][1:-1])
                continue
            context_market[tmp[4][1:-1]] = (prices[tmp[1][1:-1]], tmp[1][1:-1])
        cheapest_price = list(context_market.items())[0][1][0]
        r = r[0][17:]
        r = json.loads(r)
        listings = r['730']['2']
        to_print = []
        new_items = 0
        for listing in listings:
            if listing not in item_cache[item]:
                new_items += 1
                item_cache[item].append(listing)
                item_data = listings[listing]
                link = f"{float_url}?url={item_data['actions'][0]['link'].replace('%assetid%', listing)}"
                while True:
                    try:
                        if use_proxy and not proxy_switch:
                            resp2 = requests.get(link, proxies=proxy)
                            proxy_switch = True
                        else:
                            resp2 = requests.get(link)
                            proxy_switch = False
                        try:
                            resp2 = resp2.json()
                            break
                        except json.decoder.JSONDecodeError:
                            print(resp2.text)
                            sleep(0.5)
                            continue
                    except requests.ConnectionError:
                        continue
                if resp2:
                    if listing in context_market.keys():
                        this_price = context_market[listing][0]
                    else:
                        this_price = '0'
                    if not isinstance(this_price, float) or not isinstance(cheapest_price, float):
                        this_price = '0'
                        cheapest_price = '0'
                    if 'emerald' not in resp2['iteminfo']['imageurl']:
                        if 'phase4' not in resp2['iteminfo']['imageurl']:
                            continue
                        if this_price == '0' or this_price <= limit_p4 * 1.05:
                            to_print.append(f"Phase4 | FV: {resp2['iteminfo']['floatvalue']} | {this_price} руб. {'{:.2f}'.format(this_price / cheapest_price * 100) if this_price != '0' else '?'}%")
                        continue
                    if this_price == '0' or this_price <= limit * 1.15:
                        to_print.append(
                            f"Emerald | FV: {resp2['iteminfo']['floatvalue']} | {this_price} руб. {'{:.2f}'.format(this_price / cheapest_price * 100) if this_price != '0' else '?'}%")
                    else:
                        print(this_price)
        print(f"{new_items} new items for {item}")
        if to_print:
            print(f"Cheapest price | {cheapest_price}")
            print('\n'.join(to_print))
            bot.send_message(852738955, f"{item}\n" + '\n'.join(to_print))
        r_end = soup.find_all("span", {"id": "searchResults_end"})
        r_total = soup.find_all("span", {"id": "searchResults_total"})
        if r_end and r_total[0].text != r_end[0].text:
            print(r_total[0].text, r_end[0].text)
            t0 = perf_counter()
            while True:
                try:
                    if proxy_switch:
                        session.proxies.update(no_proxy)
                        proxy_switch = False
                    else:
                        if use_proxy:
                            session.proxies.update(proxy)
                        proxy_switch = True
                    resp = session.get(item_url + item + "?query=&start=100&count=100", headers=headers)
                    t0 = perf_counter() - t0
                    break
                except requests.ConnectionError:
                    continue
            resp = resp.text
            soup = BeautifulSoup(resp, "html.parser")
            r = re.findall(r'var g_rgAssets = \{.*\}', resp)
            prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
            if not r or not prices:
                print('>')
                id += 1
                if t0 < 6:
                    sleep(6 - t0)
                sleep(1)
                continue
            while (not r or not prices) or ('converted_price' not in list(json.loads(prices[0][22:]).items())[0][1].keys()):
                print('?')
                t0 = perf_counter()
                while True:
                    try:
                        if proxy_switch:
                            session.proxies.update(no_proxy)
                            proxy_switch = False
                        else:
                            if use_proxy:
                                session.proxies.update(proxy)
                            proxy_switch = True
                        resp = session.get(item_url + item + query_settings, headers=headers)
                        t0 = perf_counter() - t0
                        break
                    except requests.ConnectionError:
                        continue
                resp = resp.text
                with open('OUTPUT.html', 'w', encoding='utf-8') as o:
                    o.write(resp)
                soup = BeautifulSoup(resp, "html.parser")
                r = re.findall(r'var g_rgAssets = \{.*\}', resp)
                prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
                if t0 < 6:
                    sleep(6 - t0)
            prices = json.loads(prices[0][22:])
            for p in prices.keys():
                if prices[p]['fee'] == 0 or 'converted_price' not in prices[p].keys():
                    continue
                prices[p] = (prices[p]['converted_price'] + prices[p]['converted_fee']) / 100
            buttons = soup.find_all("a", {"class": "item_market_action_button btn_green_white_innerfade btn_small"})
            context_market = dict()
            for b in buttons:
                tmp = b['href']
                tmp = tmp[tmp.find('(') + 1:tmp.find(')')].split(', ')
                if tmp[1][1:-1] not in prices.keys():
                    item_cache[item].append(tmp[4][1:-1])
                    continue
                context_market[tmp[4][1:-1]] = (prices[tmp[1][1:-1]], tmp[1][1:-1])
            cheapest_price = list(context_market.items())[0][1][0]
            r = r[0][17:]
            r = json.loads(r)
            listings = r['730']['2']
            to_print = []
            new_items = 0
            for listing in listings:
                if listing not in item_cache[item]:
                    new_items += 1
                    item_cache[item].append(listing)
                    item_data = listings[listing]
                    link = f"{float_url}?url={item_data['actions'][0]['link'].replace('%assetid%', listing)}"
                    while True:
                        try:
                            if proxy_switch:
                                session.proxies.update(no_proxy)
                                proxy_switch = False
                            else:
                                if use_proxy:
                                    session.proxies.update(proxy)
                                proxy_switch = True
                            resp2 = session.get(link)
                            try:
                                resp2 = resp2.json()
                                break
                            except json.decoder.JSONDecodeError:
                                sleep(1)
                                continue
                        except requests.ConnectionError:
                            continue
                    if resp2:
                        if listing in context_market.keys():
                            this_price = context_market[listing][0]
                        else:
                            this_price = '0'
                        if not isinstance(this_price, float) or not isinstance(cheapest_price, float):
                            this_price = '0'
                            cheapest_price = '0'
                        if 'emerald' not in resp2['iteminfo']['imageurl']:
                            continue
                        if this_price == '0' or this_price <= limit * 1.15:
                            to_print.append(f"Emerald | FV: {resp2['iteminfo']['floatvalue']} | {this_price} руб. {'{:.2f}'.format(this_price / cheapest_price * 100) if this_price != '0' else '?'}%")
                        else:
                            print(this_price)
            print(f"{new_items} new items for {item}")
            if to_print:
                print(f"Cheapest price | {cheapest_price}")
                print('\n'.join(to_print))
                bot.send_message(852738955, f"{item} | предел {limit} руб.\n" + '\n'.join(to_print))
        print(perf_counter() - t1)
        with open('emerald_item_cache', 'wb') as ch:
            pickle.dump(item_cache, ch)
        id += 1


items = [
         ('★ Bowie Knife | Gamma Doppler (Factory New)', 66000, 18000),
         ('★ Huntsman Knife | Gamma Doppler (Factory New)', 82000, 18000),
]

# 'AK-47': [151, 168, 179, 321, 387, 555, 592, 617, 661, 670, 760, 809, 828, 955]
listings_worker(items)
