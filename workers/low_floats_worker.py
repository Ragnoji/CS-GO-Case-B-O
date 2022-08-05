import requests
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
    load_dotenv()
    # credentials = {
    #     'sessionid': '847ce3b4942e55e812f7e115', 'currency': '5', 'appid': '730', 'market_hash_name': 'Chroma Case',
    #     'price_total': '100', 'quantity': '1', 'billing_state': '', 'save_my_address': '0',
    # }
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
    session = requests.session()
    session.headers.update(headers)
    session.get('https://steamcommunity.com/market/')
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
            item = item[0]
            # driver.get(item_url + item + query_settings)
            resp = session.get(item_url + item + query_settings, headers=headers)
            resp = resp.text
            with open('OUTPUT.html', 'w', encoding='utf-8') as o:
                o.write(resp)
            soup = BeautifulSoup(resp, "html.parser")
            r = re.findall(r'var g_rgAssets = \{.*\}', resp)
            prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
            k = 0
            while (not r or not prices) and k < 2:
                print('!')
                sleep(5)
                resp = session.get(item_url + item + query_settings, headers=headers)
                resp = resp.text
                with open('OUTPUT.html', 'w', encoding='utf-8') as o:
                    o.write(resp)
                soup = BeautifulSoup(resp, "html.parser")
                r = re.findall(r'var g_rgAssets = \{.*\}', resp)
                prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
                k += 1
            if k == 3:
                print('!!!')
                continue
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
                    resp2 = requests.get(link)
                    while True:
                        try:
                            resp2 = resp2.json()
                            break
                        except json.decoder.JSONDecodeError:
                            sleep(1)
                            continue
                        break
                    if resp2:
                        this_price = context_market[listing][0]
                        if not float_cap or (float_cap and resp2['iteminfo']['floatvalue'] < float_cap):
                            to_print.append(f"FV: {resp2['iteminfo']['floatvalue']} | {this_price} руб. {'{:.2f}'.format(this_price / cheapest_price * 100)}%")
            print(f"{new_items} new items for {item}")
            if to_print:
                print(f"Cheapest price | {cheapest_price}")
                print('\n'.join(to_print))
                bot.send_message(852738955, f"{item} | {cheapest_price}\n" + '\n'.join(to_print))
            sleep(5)
        print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | sleeping 4.0 sec')
        with open('item_cache', 'wb') as ch:
            pickle.dump(item_cache, ch)
        sleep(5)


items = [('★ Sport Gloves | Nocts (Field-Tested)', 0.18), ('★ Sport Gloves | Slingshot (Field-Tested)', 0.18),
         ('★ Specialist Gloves | Lt. Commander (Field-Tested)', 0.18), ('★ Sport Gloves | Scarlet Shamagh (Field-Tested)', 0.18),
         ('★ Specialist Gloves | Tiger Strike (Field-Tested)', 0.18), ('★ Driver Gloves | King Snake (Field-Tested)', 0.18),
         ('★ Driver Gloves | Imperial Plaid (Field-Tested)', 0.18),
         ('★ Sport Gloves | Omega (Field-Tested)', 0.18), ('★ Sport Gloves | Amphibious (Field-Tested)', 0.18),
         ('★ Specialist Gloves | Field Agent (Field-Tested)', 0.18),
         ('★ Moto Gloves | Blood Pressure (Field-Tested)', 0.18),
         ('★ Moto Gloves | Finish Line (Field-Tested)', 0.18), ('★ Moto Gloves | Smoke Out (Field-Tested)', 0.18),
         ('★ Driver Gloves | Black Tie (Field-Tested)', 0.18), ('★ Driver Gloves | Snow Leopard (Field-Tested)', 0.18),
]
listings_worker(items)
