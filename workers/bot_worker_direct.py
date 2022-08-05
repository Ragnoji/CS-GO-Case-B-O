import asyncio
from time import sleep
import requests
from datetime import datetime
from discord.ext import commands
import os
from dotenv import load_dotenv


def worker_direct(list_of_items, game_index, mode=0, delay=0):
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

    session = requests.session()
    session.headers.update(headers)
    resp = session.get('https://steamcommunity.com/market/')
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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = commands.Bot(command_prefix='>')

        @bot.event
        async def on_message(msg):
            if msg.author == bot.user:
                return
            if msg.embeds and ('Rust Item Definitions Updated' in msg.embeds[0].title or 'Rust Store' in msg.embed[0].title):
                await bot.close()

        bot.run('NjUwMzQxMTc3NTcyMTk2MzY0.GIPr5_.D_mTHc23pm_i58r-ja8LrZ2LzV10rKDvoAmleE')

        while not bot.is_closed():
            continue
    elif mode == -1:
        pass
    else:
        while datetime.now().time().hour != 3:
            sleep(0.1)

    sleep(delay * 0.05)

    i = 0
    while list_of_items:
        if i == len(list_of_items):
            i = 0
        item = list_of_items[i]
        credentials['market_hash_name'] = item[0]
        credentials['price_total'] = int(float(item[1]) * 100) * int(item[2])
        credentials['quantity'] = item[2]
        try:
            resp = session.post(create_buy_order, data=credentials, timeout=0.6)
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
                continue
            if j['success'] == 40:
                sleep(0.1)
                continue
            break
        except requests.exceptions.Timeout:
            pass
        i += 1

