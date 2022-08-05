from bot_worker import worker
from bot_worker_direct import worker_direct
from threading import Thread
from time import sleep


def main():
    list_of_items = open('target_items.txt', 'r', encoding='utf-8')
    list_of_items = list_of_items.readlines()

    if not list_of_items:
        print('create "target_items.txt" file with inputs')
        return

    list_of_items = [item_line.strip().split() for item_line in list_of_items]
    count_map = dict()
    for i in range(len(list_of_items)):
        tmp = list_of_items[i]
        for g, v in enumerate(tmp):
            if v.endswith('"'):
                list_of_items[i] = [''.join(' '.join(tmp[:g + 1])[1:-1])] + tmp[g + 1:]
                count_map[list_of_items[i][0]] = 0
    print(*list_of_items)
    game_index = 252490
    webdriver = True
    mode = 1  # 0 если нужен бот на нормал скины и 1 если бот на абнормал (-1 если нужно прямо сейчас В СЛУЧАЕ КЕЙСА ИТД)
    parallel = False  # Регулировка режима запуска воркеров
    require = input(f'Согласны ли вы с таргетами и параметрами:\nwebdriver = {webdriver}\ngame_index = {game_index}\nmode = {mode}\nparallel = {parallel}\n')
    if require != '':
        return
    print('Начинаю работу')
    threads = []
    selected_worker = worker if webdriver else worker_direct
    if parallel:
        for i in range(0, len(list_of_items)):
            threads.append(Thread(target=selected_worker, args=([list_of_items[i]], game_index, mode, i)))
            threads[-1].start()
            if webdriver:
                sleep(7)
            else:
                sleep(0.1)
    else:
        splited_lists = [[], []]
        for i, item in enumerate(list_of_items):
            splited_lists[i % 2].append(item)
        for i, s_l in enumerate(splited_lists):
            if s_l:
                threads.append(Thread(target=selected_worker, args=(s_l, game_index, mode, i)))
                threads[-1].start()

    sleep(3)
    for t in threads:
        if t.is_alive():
            t.join()


if __name__ == '__main__':
    main()
