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
    if os.path.isfile('marble_item_cache'):
        item_cache = pickle.load(open('marble_item_cache', 'rb'))

    token = os.getenv('AUTH_TOKEN')
    bot = telebot.TeleBot(token)

    # exteriors_to_check = ['Battle-Scarred', 'Well-Worn', 'Field-Tested', 'Minimal Wear', 'Factory New']
    id = 0
    while True:
        if use_proxy:
            session.proxies.update(proxy)
        if id == len(list_of_items.keys()):
            id = 0
            print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | sleeping 4.0 sec')
            with open('marble_item_cache', 'wb') as ch:
                pickle.dump(item_cache, ch)
            sleep(5)
        item = list(list_of_items.items())[id]
        gem_patterns = item[1]
        item = item[0]
        print(item)
        if item not in item_cache.keys():
            item_cache[item] = []
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
        if k == 2:
            print('!!!')
            with open('OUTPUT.html', 'w', encoding='utf-8') as o:
                o.write(resp)
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
                    if this_price != '0' and this_price / cheapest_price > 1.2:
                        continue
                    if resp2['iteminfo']['paintseed'] in gem_patterns:
                        to_print.append(f"Pattern: {resp2['iteminfo']['paintseed']} | FV: {resp2['iteminfo']['floatvalue']} | {this_price} руб. {'{:.2f}'.format(this_price / cheapest_price * 100) if this_price != '0' else '?'}%")
        print(f"{new_items} new items for {item}")
        if to_print:
            print(f"Cheapest price | {cheapest_price}")
            print('\n'.join(to_print))
            bot.send_message(852738955, f"{item} | {cheapest_price}\n" + '\n'.join(to_print))
        r_end = soup.find_all("span", {"id": "searchResults_end"})
        r_total = soup.find_all("span", {"id": "searchResults_total"})
        if r_end and r_total[0].text != r_end[0].text:
            if use_proxy:
                session.proxies.update(proxy)
            while True:
                try:
                    resp = session.get(item_url + item + "?query=&start=100&count=100", headers=headers)
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
                        resp = session.get(item_url + item + "?query=&start=100&count=100", headers=headers)
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
                        if this_price != '0' and this_price / cheapest_price > 1.2:
                            continue
                        if resp2['iteminfo']['paintseed'] in gem_patterns:
                            to_print.append(f"Pattern: {resp2['iteminfo']['paintseed']} | FV: {resp2['iteminfo']['floatvalue']} | {this_price} руб. {'{:.2f}'.format(this_price / cheapest_price * 100) if this_price != '0' else '?'}%")
            print(f"{new_items} new items for {item}")
            if to_print:
                print(f"Cheapest price | {cheapest_price}")
                print('\n'.join(to_print))
                bot.send_message(852738955, f"{item} | {cheapest_price}руб.\n" + '\n'.join(to_print))
        sleep(8)
        id += 1


items = {
    '★ Karambit | Marble Fade (Factory New)': [412, 16, 146, 241, 359, 393, 541, 602, 649, 688, 701, 152, 281, 292, 344, 628, 673, 743, 777, 792, 994, 48, 126, 129, 332, 780, 787, 874, 908, 918, 923, 182, 204, 252, 457, 522, 578, 652, 660, 685, 705, 736, 832, 988, 112, 230, 340, 356, 444, 452, 471, 607, 621, 631, 761, 773, 873, 876, 982, 8, 14, 32, 58, 108, 213, 233, 243, 274, 405, 454, 614, 653, 683, 702, 728, 732, 770, 795, 803, 826, 867, 949, 5, 178, 188, 202, 337, 378, 406, 461, 539, 655, 696, 854, 966, 971, 68, 121, 149, 165, 171, 206, 287, 370, 493, 499, 516, 637, 656, 672, 706, 766, 817, 922, 959, 997, 28, 156, 177, 238, 402, 545, 546, 553, 559, 589, 591, 725, 764, 791, 810, 844, 858, 868, 972, 977, 9, 27, 90, 110, 125, 183, 195, 203, 232, 254, 329, 351, 372, 397, 404, 441, 448, 459, 473, 483, 537, 561, 590, 626, 632, 647, 710, 727, 753, 756, 785, 805, 809, 818, 869, 909, 930, 941, 962, 976, 980, 989, 3, 60, 62, 71, 98, 138, 148, 170, 196, 216, 222, 234, 266, 304, 307, 309, 315, 321, 328, 333, 334, 364, 400, 411, 413, 415, 438, 445, 463, 485, 496, 506, 535, 570, 582, 605, 624, 630, 663, 667, 670, 674, 691, 717, 723, 746, 794, 822, 845, 846, 931, 948, 958],
    '★ StatTrak™ Bayonet | Marble Fade (Factory New)': [412, 16, 146, 241, 359, 393, 541, 602, 649, 688, 701, 152, 281, 292, 344, 628, 673, 743, 777, 792, 994, 48, 126, 129, 332, 780, 787, 874, 908, 918, 923, 182, 204, 252, 457, 522, 578, 652, 660, 685, 705, 736, 832, 988, 112, 230, 340, 356, 444, 452, 471, 607, 621, 631, 761, 773, 873, 876, 982, 8, 14, 32, 58, 108, 213, 233, 243, 274, 405, 454, 614, 653, 683, 702, 728, 732, 770, 795, 803, 826, 867, 949, 5, 178, 188, 202, 337, 378, 406, 461, 539, 655, 696, 854, 966, 971, 27, 28, 68, 90, 121, 149, 156, 165, 171, 177, 195, 206, 216, 232, 238, 287, 309, 329, 351, 370, 372, 397, 402, 404, 441, 459, 473, 483, 485, 493, 499, 516, 537, 545, 546, 553, 559, 561, 589, 590, 591, 626, 632, 637, 656, 672, 706, 710, 723, 725, 727, 753, 756, 764, 766, 785, 791, 805, 809, 810, 817, 818, 844, 858, 868, 922, 930, 941, 959, 962, 972, 976, 977, 980, 997],
    '★ Bayonet | Marble Fade (Factory New)': [412, 16, 146, 241, 359, 393, 541, 602, 649, 688, 701, 152, 281, 292, 344, 628, 673, 743, 777, 792, 994, 48, 126, 129, 332, 780, 787, 874, 908, 918, 923, 182, 204, 252, 457, 522, 578, 652, 660, 685, 705, 736, 832, 988, 112, 230, 340, 356, 444, 452, 471, 607, 621, 631, 761, 773, 873, 876, 982, 8, 14, 32, 58, 108, 213, 233, 243, 274, 405, 454, 614, 653, 683, 702, 728, 732, 770, 795, 803, 826, 867, 949, 5, 178, 188, 202, 337, 378, 406, 461, 539, 655, 696, 854, 966, 971, 27, 28, 68, 90, 121, 149, 156, 165, 171, 177, 195, 206, 216, 232, 238, 287, 309, 329, 351, 370, 372, 397, 402, 404, 441, 459, 473, 483, 485, 493, 499, 516, 537, 545, 546, 553, 559, 561, 589, 590, 591, 626, 632, 637, 656, 672, 706, 710, 723, 725, 727, 753, 756, 764, 766, 785, 791, 805, 809, 810, 817, 818, 844, 858, 868, 922, 930, 941, 959, 962, 972, 976, 977, 980, 997],
    '★ StatTrak™ Flip Knife | Marble Fade (Factory New)': [412, 16, 146, 241, 359, 393, 541, 602, 649, 688, 701, 152, 281, 292, 344, 628, 673, 743, 777, 792, 994, 126, 129, 332, 787, 874, 908, 918, 923, 48, 112, 182, 204, 230, 252, 340, 356, 444, 452, 457, 471, 522, 578, 607, 621, 631, 652, 660, 685, 705, 736, 761, 773, 780, 832, 873, 876, 982, 988, 5, 8, 14, 27, 28, 32, 58, 68, 90, 108, 121, 149, 156, 165, 171, 177, 178, 188, 195, 202, 206, 213, 216, 232, 233, 238, 243, 274, 287, 309, 329, 337, 351, 370, 372, 378, 397, 402, 404, 405, 406, 441, 454, 459, 461, 473, 483, 493, 499, 516, 537, 539, 545, 546, 553, 559, 561, 589, 590, 591, 614, 626, 632, 637, 653, 655, 656, 672, 683, 696, 702, 706, 710, 723, 725, 727, 728, 732, 753, 756, 764, 766, 770, 785, 791, 795, 803, 805, 809, 810, 817, 818, 826, 844, 854, 858, 867, 868, 922, 930, 941, 949, 959, 962, 966, 971, 972, 976, 977, 997],
    '★ Flip Knife | Marble Fade (Factory New)': [412, 16, 146, 241, 359, 393, 541, 602, 649, 688, 701, 152, 281, 292, 344, 628, 673, 743, 777, 792, 994, 126, 129, 332, 787, 874, 908, 918, 923, 48, 112, 182, 204, 230, 252, 340, 356, 444, 452, 457, 471, 522, 578, 607, 621, 631, 652, 660, 685, 705, 736, 761, 773, 780, 832, 873, 876, 982, 988, 5, 8, 14, 27, 28, 32, 58, 68, 90, 108, 121, 149, 156, 165, 171, 177, 178, 188, 195, 202, 206, 213, 216, 232, 233, 238, 243, 274, 287, 309, 329, 337, 351, 370, 372, 378, 397, 402, 404, 405, 406, 441, 454, 459, 461, 473, 483, 493, 499, 516, 537, 539, 545, 546, 553, 559, 561, 589, 590, 591, 614, 626, 632, 637, 653, 655, 656, 672, 683, 696, 702, 706, 710, 723, 725, 727, 728, 732, 753, 756, 764, 766, 770, 785, 791, 795, 803, 805, 809, 810, 817, 818, 826, 844, 854, 858, 867, 868, 922, 930, 941, 949, 959, 962, 966, 971, 972, 976, 977, 997],
}

# 'AK-47': [151, 168, 179, 321, 387, 555, 592, 617, 661, 670, 760, 809, 828, 955]
listings_worker(items)
