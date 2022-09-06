import csv
import math
from datetime import datetime

def load_data(path: str):
    with open(path) as csvfile:
        return list(csv.reader(csvfile))

def prepare_data(input_array: list[list[str]]) -> list[list]:
    """Убираем лишние символы, форматируем строчные данные в числовые и преобразуем время в секунды

    Args:
        input_array (list[list[str]]): входящий двумерный список содержащий считанные данные из csv файла

    Returns:
        list[list]: список с данными
    """
    data = []
    for _, row in enumerate(input_array):
        # убираем лишние символы и разделяем столбцы
        m = [s.strip().strip('}') for s in row[0].split(';')]
        # парсим время
        tm1 = datetime.strptime(m[4], '%H:%M:00')
        tm2 = datetime.strptime(m[5], '%H:%M:00')
        # находим разницу между временем отправления и прибытия
        time = tm2 - tm1
        data.append([int(m[0]), int(m[1]), int(m[2]), float(m[3]), time.seconds])
    
    return data

def to_matr(v: dict[int, int], data: list[list[int]], kind: int = 0) -> list:
    """Преобразует входные данные в матрицу для удобной обработки

    Args:
        v (dict[int, int]): вершины графа с идентификаторами, ключ вершина(станция), значение вес(цена или время)
        data (list[list[int]]): думерный список
        kind (int, optional): тип веса: 0 - цена, 1 - время

    Returns:
        list: двумерный список с весом ребер графа
    """
    
    # инициализируем двумерный список размером N * N
    matr = []
    for _ in range(len(v)):
        matr.append([math.inf] * len(v))
    
    # заполняем матрицу
    for _, r in enumerate(data):
        if kind == 0:
            # цена
            item = r[3]
        elif kind == 1:
            # время
            item = r[4]
        else:
            raise Exception('Тип для веса либо 0, либо 1')

        # проверяем является ли текущий элемент более выгодным того, который уже находится в матрице
        if item < matr[v[r[1]]][v[r[2]]]:
            matr[v[r[1]]][v[r[2]]] = item
    
    return matr

def find_best(N: int, g: list, node: int) -> tuple[int, list[int]] | None:
    """Находит лучший путь в графе - g начиная с вершины - node

    Args:
        N (int): количество вершин
        g (list): двумерный список, который является графом
        node (int): вершина графа с которой ищется путь

    Returns:
        tuple[int, list[int]]: возращает самый выгодный вариант по весу и его путь, который начинается с вершины node
        None: такого варианта не существует
    """
    cost = 0
    path = []
    seen = [False] * N
    def next(node: int, curr_cost: int) -> None | tuple[int, int]:
        """ищет следующую вершину - node с минимальным весом

        Args:
            node (int): вершина
            curr_cost (int): текущая стоимость пуьт

        Returns:
            None: если нет пути к этой вершине
            tuple: новая стоимость и индекс вершины
        """
        min_node = (-1, math.inf)
        this_cost = 0
        for i in range(N):
            # проверяем не посещали ли мы эту вершину ранее
            # и является ли она более выгодной
            if not seen[i] and g[node][i] < min_node[1]:
                this_cost = g[node][i]
                min_node = (i, g[node][i])

        if min_node[0] == -1:
            return None

        return curr_cost + this_cost, min_node[0]

    def tsp(node: int, cost: int) -> None | int:
        """Запускает процесс поиска выгодных вершин начиная с текущей - node

        Args:
            node (int): начальная вершина
            cost (int): общий вес пройденного пути

        Returns:
            int: общий вес пройденного пути
            None: нет ни одной непосещенной вершины, к которой можно прийти из текущей
        """
        # отмечаем вершину как посещенную
        seen[node] = True
        # добавляем в список пути
        path.append(node)
        # находим следующую веришну с минимальным весом
        next_nd = next(node, cost)
        
        # если путь равен количеству вершин, то самый выгодный путь найден
        # возвращаем стоимость
        if len(path) == N:
            return cost
        
        # если пути к следующей вершине нет, то возвращаем None
        if not next_nd:
            return None

        cost = next_nd[0]
        # если путь не найден запускаем функцию по новой
        return tsp(next_nd[1], cost)
    
    result = tsp(node, cost)
    if not result:
        return None
    
    return result, path


def main():
    
    # загружаем данные и готовим для обработки
    data = load_data('test_task_data.csv')
    data = prepare_data(data)

    # создаем словарь вершин и присваеваем им индекс для удобства
    v = {}
    for r in data:
        for i in range(0, 2):
            if r[i+1] not in v:
                v[r[i+1]] = len(v)
    vkeys = list(v.keys())

    # находим лучшие пути по цене
    best_prices: list[tuple] = []
    g_with_prices = to_matr(v, data, 0)
    for k in v:
        result = find_best(len(v), g_with_prices, v[k])
        if not result:
            continue
        best_prices.append(result)

    best_prices.sort(key=lambda el: el[0])
    for i, price_path in enumerate(best_prices):
        print(f'{i+1}.', 'Цена:', round(price_path[0], 2), 'Путь:', ' -> '.join([str(vkeys[vert_idx]) for vert_idx in price_path[1]]))

    # находим лучшие пути по времени
    best_time: list[tuple] = []
    g_with_time = to_matr(v, data, 1)
    for k in v:
        result = find_best(len(v), g_with_time, v[k])
        if not result:
            continue
        best_time.append((result))

    best_time.sort(key=lambda el: el[0])
    for i, tm_path in enumerate(best_time):
        print(f'{i+1}.', 'Время(сек):', tm_path[0], 'Путь:', ' -> '.join([str(vkeys[vert_idx]) for vert_idx in tm_path[1]]))


if __name__ == '__main__':
    main()