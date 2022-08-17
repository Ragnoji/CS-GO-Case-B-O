import requests
import requests.adapters
import re
import datetime
from time import sleep
import json
from bs4 import BeautifulSoup
import pickle
import telebot
import os
from dotenv import load_dotenv


def listings_worker(list_of_items):
    # credentials = {
    #     'sessionid': '847ce3b4942e55e812f7e115', 'currency': '5', 'appid': '730', 'market_hash_name': 'Chroma Case',
    #     'price_total': '100', 'quantity': '1', 'billing_state': '', 'save_my_address': '0',
    # }
    load_dotenv()
    steam_m = os.getenv('STEAM_AUTH_PARSER')
    steam_r = os.getenv('STEAM_REMEMBER_PARSER')
    headers = {'Host': 'steamcommunity.com',
               'Origin': 'https://steamcommunity.com',
               'Referer': 'https://steamcommunity.com/market', 'Connection': 'keep-alive',
               'Accept-Language': 'en;q=0.9,zh;q=0.8', 'Accept-Encoding': 'gzip, deflate, br',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.134 YaBrowser/22.7.1.806 Yowser/2.5 Safari/537.36',
               'Cookie': f'{steam_m};{steam_r};steamCurrencyId=5'
               }

    float_url = 'https://api.csgofloat.com/'
    item_url = 'https://steamcommunity.com/market/listings/730/'
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
    while True:
        try:
            session.get('https://steamcommunity.com/market/')
            break
        except requests.ConnectionError:
            continue
    query_settings = '?query=&start=0&count=100&country=RU&language=english&currency=5'
    item_cache = dict()
    if os.path.isfile('item_cache'):
        item_cache = pickle.load(open('item_cache', 'rb'))

    token = os.getenv('AUTH_TOKEN')
    bot = telebot.TeleBot(token)

    while True:
        for item in list_of_items:
            float_cap = False
            if item[0] not in item_cache.keys():
                item_cache[item[0]] = []
            if len(item) == 2:
                float_cap = item[1]
            if len(item) == 3:
                float_cap = item[1]
                top_price = item[2]
            item = item[0]
            # driver.get(item_url + item + query_settings)
            if use_proxy:
                session.proxies.update(proxy)
            while True:
                try:
                    resp = session.get(item_url + item + query_settings, headers=headers)
                    break
                except requests.ConnectionError:
                    continue
            resp = resp.text
            with open('OUTPUT.html', 'w', encoding='utf-8') as o:
                o.write(resp)
            soup = BeautifulSoup(resp, "html.parser")
            r = re.findall(r'var g_rgAssets = \{.*\}', resp)
            prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
            k = 0
            if not r or not prices:
                print('>')
                continue
            while (not r or not prices) or ('converted_price' not in list(json.loads(prices[0][22:]).items())[0][1].keys()):
                print('?')
                sleep(4)
                if use_proxy:
                    session.proxies.update(proxy)
                while True:
                    try:
                        resp = session.get(item_url + item + query_settings, headers=headers)
                        break
                    except requests.ConnectionError:
                        continue
                resp = resp.text
                with open('OUTPUT.html', 'w', encoding='utf-8') as o:
                    o.write(resp)
                soup = BeautifulSoup(resp, "html.parser")
                r = re.findall(r'var g_rgAssets = \{.*\}', resp)
                prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
                k += 1
            
            prices = json.loads(prices[0][22:])
            for p in prices.keys():
                if prices[p]['fee'] == 0 or 'converted_price' not in prices[p].keys():
                    continue
                prices[p] = int((prices[p]['converted_price'] + prices[p]['converted_fee']) // 100)
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
                    if use_proxy:
                        while True:
                            try:
                                resp2 = requests.get(link, proxies=proxy)
                                break
                            except requests.ConnectionError:
                                continue
                    else:
                        while True:
                            try:
                                resp2 = requests.get(link)
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
                        if not isinstance(this_price, int) or not isinstance(cheapest_price, int):
                            print(prices)
                            this_price = '0'
                            cheapest_price = '0'
                        if float_cap and float(resp2['iteminfo']['floatvalue']) > float_cap:
                            continue
                        if this_price != '0' and this_price > top_price:
                            continue
                        to_print.append(f"FV: {resp2['iteminfo']['floatvalue']} | {this_price} руб. {'{:.2f}'.format(this_price / cheapest_price * 100) if this_price != '0' else '?'}%")
            print(f"{new_items} new items for {item}")
            if to_print:
                print(f"Cheapest price | {cheapest_price}")
                print('\n'.join(to_print))
                bot.send_message(852738955, f"{item} | {cheapest_price} руб.\n" + '\n'.join(to_print))
            sleep(4)
        print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | sleeping 4.0 sec')
        with open('item_cache', 'wb') as ch:
            pickle.dump(item_cache, ch)
        sleep(4)


items = [('★ Sport Gloves | Nocts (Field-Tested)', 0.18, 27000), ('★ Sport Gloves | Slingshot (Field-Tested)', 0.18, 60000),
         ('★ Sport Gloves | Scarlet Shamagh (Field-Tested)', 0.18, 24000),
         ('★ Specialist Gloves | Tiger Strike (Field-Tested)', 0.18, 67000),
         ('★ Specialist Gloves | Field Agent (Field-Tested)', 0.18, 40000),
         ('★ Driver Gloves | Snow Leopard (Field-Tested)', 0.18, 56000)
]
listings_worker(items)
