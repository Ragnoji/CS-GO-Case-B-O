from time import sleep
from selenium import webdriver
import pickle
from threading import Thread
from weapon_parser import new_weapons
from worker_template import worker
import os
from dotenv import load_dotenv
import requests


def main():
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'


    url = f'https://steamcommunity.com/market/listings/730/Place'
    list_of_knives = open('knives_to_parse.txt', 'r', encoding='utf-8')
    list_of_knives = list_of_knives.readlines()

    if not list_of_knives:
        print('create "target_items.txt" file with inputs')

    list_of_knives = [item_line.strip().split() for item_line in list_of_knives]
    count_knives = dict()
    for i in range(len(list_of_knives)):
        tmp = list_of_knives[i]
        for g, v in enumerate(tmp):
            if v.endswith('"'):
                list_of_knives[i] = [''.join(' '.join(tmp[:g + 1])[1:-1])] + tmp[g + 1:]
                count_knives[list_of_knives[i][0]] = 0
    print(*list_of_knives)
    if input('Согласны с таргетами?') != '':
        return
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
    session = requests.session()
    session.headers.update(headers)
    session.get('https://steamcommunity.com/market/')

    current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
    old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
    current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()
    new_skins = new_weapons(current_items, old_items, current_names)
    list_of_covert = []
    list_of_covert_stat = []
    print(new_skins)


if __name__ == '__main__':
    main()