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
    proxy = {'https': 'socks5://user58497:nx0yrs@193.160.211.84:11443',
             'http': 'socks5://user58497:nx0yrs@193.160.211.84:11443'}
    float_url = 'https://api.csgofloat.com/'
    item_url = 'https://steamcommunity.com/market/listings/730/'
    use_proxy = False
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
    if os.path.isfile('gem_item_cache'):
        item_cache = pickle.load(open('gem_item_cache', 'rb'))

    token = os.getenv('AUTH_TOKEN')
    bot = telebot.TeleBot(token)

    exteriors_to_check = ['Battle-Scarred', 'Well-Worn', 'Field-Tested', 'Minimal Wear', 'Factory New']
    id = 0
    while True:
        if use_proxy:
            session.proxies.update(proxy)
        if id == len(list_of_items.keys()):
            id = 0
            print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | sleeping 4.0 sec')
            with open('gem_item_cache', 'wb') as ch:
                pickle.dump(item_cache, ch)
            sleep(5)
        item = list(list_of_items.items())[id]
        gem_patterns = item[1]
        item = f"{item[0]} | Case Hardened"
        print(item)
        if item not in item_cache.keys():
            item_cache[item] = []
        # driver.get(item_url + item + query_settings)
        ed = 0
        while ed != len(exteriors_to_check):
            if use_proxy:
                session.proxies.update(proxy)
            exterior = exteriors_to_check[ed]
            while True:
                try:
                    resp = session.get(item_url + item + f" ({exterior})" + query_settings, headers=headers)
                    break
                except requests.ConnectionError:
                    continue
            resp = resp.text
            soup = BeautifulSoup(resp, "html.parser")
            r = re.findall(r'var g_rgAssets = \{.*\}', resp)
            prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
            k = 0
            while (not r or not prices) and k < 2:
                print('!')
                sleep(10)
                if use_proxy:
                    session.proxies.update(proxy)
                while True:
                    try:
                        resp = session.get(item_url + item + f" ({exterior})" + query_settings, headers=headers)
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
            if k == 2:
                print('!!!')
                with open('OUTPUT.html', 'w', encoding='utf-8') as o:
                    o.write(resp)
                ed += 1
                sleep(5)
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
                                break
                            except requests.ConnectionError:
                                continue
                    while True:
                        try:
                            resp2 = resp2.json()
                            break
                        except json.decoder.JSONDecodeError:
                            sleep(1)
                            continue
                        break
                    if resp2:
                        if listing in context_market.keys():
                            this_price = context_market[listing][0]
                        else:
                            this_price = '0'
                        if not isinstance(this_price, float) or not isinstance(cheapest_price, float):
                            this_price = '0'
                            cheapest_price = '0'
                        if resp2['iteminfo']['paintseed'] in gem_patterns:
                            to_print.append(f"💎 Pattern: {resp2['iteminfo']['paintseed']} | FV: {resp2['iteminfo']['floatvalue']} | {this_price} руб. {'{:.2f}'.format(this_price / cheapest_price * 100) if this_price != '0' else '?'}%")
            print(f"{new_items} new items for {item} ({exterior})")
            if to_print:
                print(f"Cheapest price | {cheapest_price}")
                print('\n'.join(to_print))
                bot.send_message(852738955, f"{item} | {cheapest_price}\n" + '\n'.join(to_print))
            r_end = soup.find_all("span", {"id": "searchResults_end"})
            r_total = soup.find_all("span", {"id": "searchResults_total"})
            if r_end and r_total[0].text != r_end[0].text:
                exterior = exteriors_to_check[ed]
                if use_proxy:
                    session.proxies.update(proxy)
                while True:
                    try:
                        resp = session.get(item_url + item + f" ({exterior})?query=&start=100&count=100", headers=headers)
                        break
                    except requests.ConnectionError:
                        continue
                resp = resp.text
                soup = BeautifulSoup(resp, "html.parser")
                r = re.findall(r'var g_rgAssets = \{.*\}', resp)
                prices = re.findall(r'var g_rgListingInfo = \{.*\}', resp)
                k = 0
                while (not r or not prices) and k < 2:
                    print('!')
                    sleep(10)
                    if use_proxy:
                        session.proxies.update(proxy)
                    while True:
                        try:
                            resp = session.get(item_url + item + f" ({exterior})?query=&start=100&count=100", headers=headers)
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
                if k == 2:
                    print('!!!')
                    with open('OUTPUT.html', 'w', encoding='utf-8') as o:
                        o.write(resp)
                    ed += 1
                    sleep(5)
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
                                    break
                                except requests.ConnectionError:
                                    continue
                        while True:
                            try:
                                resp2 = resp2.json()
                                break
                            except json.decoder.JSONDecodeError:
                                sleep(1)
                                continue
                            break
                        if resp2:
                            if listing in context_market.keys():
                                this_price = context_market[listing][0]
                            else:
                                this_price = '0'
                            if not isinstance(this_price, float) or not isinstance(cheapest_price, float):
                                this_price = '0'
                                cheapest_price = '0'
                            if resp2['iteminfo']['paintseed'] in gem_patterns:
                                to_print.append(f"💎 Pattern: {resp2['iteminfo']['paintseed']} | FV: {resp2['iteminfo']['floatvalue']} | {this_price} руб. {'{:.2f}'.format(this_price / cheapest_price * 100) if this_price != '0' else '?'}%")
                print(f"{new_items} new items for {item} ({exterior})")
                if to_print:
                    print(f"Cheapest price | {cheapest_price}")
                    print('\n'.join(to_print))
                    bot.send_message(852738955, f"{item} | {cheapest_price}руб.\n" + '\n'.join(to_print))
            ed += 1
            sleep(8)
        id += 1

items = {
    #'★ Bayonet': [179, 321, 442, 496, 555, 588, 592, 670, 698, 828, 916],
    #'★ StatTrak™ Bayonet': [179, 321, 442, 496, 555, 588, 592, 670, 698, 828, 916],
    #'★ Bowie Knife': [29, 182, 358, 396, 398, 399, 420, 534, 749, 913, 928, 944, 964],
    #'★ StatTrak™ Bowie Knife': [29, 182, 358, 396, 398, 399, 420, 534, 749, 913, 928, 944, 964], 
    '★ Classic Knife': [169, 180, 288, 316, 403, 449, 456, 583, 585, 601, 634, 651],
    #'★ StatTrak™ Classic Knife': [169, 180, 288, 316, 403, 449, 456, 583, 585, 601, 634, 651],
    #'★ Falchion Knife': [488, 494, 510, 575, 638, 664, 694, 770, 800, 838, 868, 891, 917],
    #'★ StatTrak™ Falchion Knife': [488, 494, 510, 575, 638, 664, 694, 770, 800, 838, 868, 891, 917],
    #'★ Flip Knife': [151, 180, 262, 321, 442, 555, 592, 647, 661, 670, 698, 828, 916], 
    #'★ StatTrak™ Flip Knife': [151, 180, 262, 321, 442, 555, 592, 647, 661, 670, 698, 828, 916],
    #'★ Huntsman Knife': [29, 248, 306, 510, 618, 652, 703, 798, 800, 838], 
    #'★ StatTrak™ Huntsman Knife': [29, 248, 306, 510, 618, 652, 703, 798, 800, 838],
    '★ Navaja Knife': [182, 371, 398, 407, 420, 515, 638, 720, 838, 839], 
    #'★ StatTrak™ Navaja Knife': [182, 371, 398, 407, 420, 515, 638, 720, 838, 839],
    '★ Nomad Knife': [55, 169, 403, 456, 557, 577, 681, 700, 704, 723], 
    #'★ StatTrak™ Nomad Knife': [55, 169, 403, 456, 557, 577, 681, 700, 704, 723],
    '★ Paracord Knife': [180, 316, 403, 456, 468, 497, 577, 583, 585, 634],
    #'★ StatTrak™ Paracord Knife': [180, 316, 403, 456, 468, 497, 577, 583, 585, 634],
    '★ Skeleton Knife': [169, 403, 449, 456, 468, 497, 557, 577, 583, 585, 681],
    #'★ StatTrak™ Skeleton Knife': [169, 403, 449, 456, 468, 497, 557, 577, 583, 585, 681],
    '★ Stiletto Knife': [182, 371, 398, 407, 478, 638, 749, 838, 913, 928],
    #'★ StatTrak™ Stiletto Knife': [182, 371, 398, 407, 478, 638, 749, 838, 913, 928],
    '★ Survival Knife': [169, 403, 456, 468, 497, 557, 577, 583, 634, 681],
    #'★ StatTrak™ Survival Knife': [169, 403, 456, 468, 497, 557, 577, 583, 634, 681],
    '★ Talon Knife': [3, 10, 55, 74, 112, 185, 222, 241, 357, 387, 450, 528, 575, 805, 819, 837, 899, 905, 923],
    #'★ StatTrak™ Talon Knife': [3, 10, 55, 74, 112, 185, 222, 241, 357, 387, 450, 528, 575, 805, 819, 837, 899, 905, 923],
    '★ Ursus Knife': [398, 494, 510, 575, 618, 694, 770, 838, 891, 917], 
    #'★ StatTrak™ Ursus Knife': [398, 494, 510, 575, 618, 694, 770, 838, 891, 917]
}

# 'AK-47': [151, 168, 179, 321, 387, 555, 592, 617, 661, 670, 760, 809, 828, 955]
listings_worker(items)
