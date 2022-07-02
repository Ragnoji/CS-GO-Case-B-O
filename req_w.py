from time import sleep
from selenium import webdriver
import pickle
from threading import Thread
from weapon_parser import new_weapons
from worker_template import worker


def main():
    options = webdriver.ChromeOptions()

    binary_yandex_driver_file = 'yandexdriver.exe'

    driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

    url = f'https://steamcommunity.com/market/listings/730/Place'
    driver.get(url)
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
    driver.get(url)
    for cookie in pickle.load(open('steam_cookies', 'rb')):
        driver.add_cookie(cookie)
    driver.refresh()

    current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
    old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
    current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()
    new_skins = new_weapons(current_items, old_items, current_names)
    list_of_covert = []
    list_of_covert_stat = []
    print(new_skins)
    if new_skins:
        for collection in new_skins.keys():
            for item in new_skins[collection]:
                if 'Collection' in collection and item[1] == 'Covert':
                    for exterior in item[2]:
                        cost = 8000
                        list_of_covert.append((item[0] + f' ({exterior})', cost, 3))

                elif 'Case' in collection and 'Collection' not in collection and item[1] == 'Covert':
                    for exterior in item[2]:
                        if exterior == 'Factory New':
                            cost = 500
                        elif exterior == 'Minimal Wear':
                            cost = 200
                        elif exterior == 'Field-Tested':
                            cost = 100
                        else:
                            continue
                        list_of_covert.append((item[0] + f' ({exterior})', cost, 10))
                        # list_of_covert_stat.append(('StatTrak™ ' + item[0] + f' ({exterior})', cost*2, 10))

    covert_workers = []
    if list_of_covert:
        # covert_worker = Thread(target=worker, args=(list_of_covert, 2.5))
        for c in list_of_covert:
            covert_worker = Thread(target=worker, args=([c], 3))
            covert_worker.start()
            sleep(10)
            covert_workers.append(covert_worker)

    if list_of_knives:
        l1 = [list_of_knives[i] for i in range(len(list_of_knives)) if i % 3 == 0]
        l2 = [list_of_knives[i] for i in range(len(list_of_knives)) if i % 3 == 2]
        l3 = [list_of_knives[i] for i in range(len(list_of_knives)) if i % 3 == 1]
        k1 = Thread(target=worker, args=(l1, 1))
        k2 = Thread(target=worker, args=(l2, 1))
        k3 = Thread(target=worker, args=(l3, 1))
        k1.start()
        sleep(5)
        k2.start()
        sleep(5)
        k3.start()
        k1.join()
        k2.join()
        k3.join()
    if list_of_covert:
        for c in covert_workers:
            c.join()
    driver.close()


if __name__ == '__main__':
    main()