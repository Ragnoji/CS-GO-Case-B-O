from bot_worker import worker
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
    require = input('Согласны ли вы с таргетами?\n')
    if require != '':
        return
    mode = 0  # 0 если нужен бот на нормал скины и 1 если бот на абнормал
    threads = []
    for i in range(0, len(list_of_items)):
        threads.append(Thread(target=worker, args=([list_of_items[i]], mode)))
        threads[-1].start()
        sleep(10)

    sleep(1)
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
