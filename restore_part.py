import math
import sys

SIZE = 500

# Представим вокруг каждой точки прямоугольную рамку (горизонтально или вертикально ориетированную)
# чтобы получить координаты точки принадлежащей к этой рамке нужно прибавить определенное число к id данной точки
# HORIZONTAL_FRAME и VERTICAL_FRAME содержат все такие числа для соответствующей рамки Собственно с помощью этих рамок
# будет производится поиск объединений точек принадлежащих треугольнику
HORIZONTAL_FRAME = [1, 1 + 500, 1 + 500 * 2,  500 * 2, -1 + 500 * 2, -1 + 500, -1]
VERTICAL_FRAME = [2, 2 + 500, 1 + 500, 500, -1 + 500, -2 + 500, -2]

# Вспомогательный массив для обхода графа чтобы не обходить одни и те же вершины дважды
USED = [[False for i in range(14)] for j in range(SIZE * SIZE + 1)]

# Место для хранения структуры точек которая предположительно принадлежит треугольнику
POINTS = []

#
NEW_IMAGE = [[0 for i in range(SIZE)] for j in range(SIZE)]

GRAPH = [[] for i in range(SIZE * SIZE + 1)]
COMPONENT = []
G_USED = [False for i in range(SIZE * SIZE + 1)]
sys.setrecursionlimit(SIZE * SIZE)


def draw():
    '''
    Помечает все точки в POITNS белым цветом на вспомогательном изображении NEW_IMAGE (которое должно иметь намного
    меньший уровень шума по сравнению с оригинальным) для последующего анализа
    :return:
    '''
    global NEW_IMAGE, POINTS
    for point in POINTS:
        y1, x1 = point[0]
        y2, x2 = point[1]
        NEW_IMAGE[y1][x1] = 255
        NEW_IMAGE[y2][x2] = 255


def get_id(y, x):
    """
    Для упрощения манипуляции с элементами изображения переведем координаты в id. id по сути своей номер
    элемента если считать справа налево и сверху вниз начиная с 1
    :param y: номер строки
    :param x: номер столбца
    :return: id
    """
    return y * SIZE + x + 1


def get_coordinates(id):
    """
    Функция обратная функции get_id (Переводит id в координаты)
    :param id: id
    :return: кортеж с номерами строки и столбца
    """
    y = id // 500
    if id % 500 == 0:
        y -= 1
    x = (id - y * 500) - 1
    coordinates = (y, x)
    return coordinates


def get_angle(vector1, vector2):
    '''
    Возвращает угол между векторами с координатами vector1 и vector2
    '''
    scalar_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    len1 = (vector1[0] ** 2 + vector1[1] ** 2) ** 0.5
    len2 = (vector2[0] ** 2 + vector2[1] ** 2) ** 0.5
    cos = scalar_product / (len1 * len2)
    angle = math.acos(cos) * (360 / 2 / math.pi)  # Угол сразу переведем в градусы
    return angle


def search_cluster(key, current_id, ways_ind, image):
    '''
    Ищет ступенчатую структуру из расположенных подряд пар которые следуюют друг за другом в определенном направлении
    При нахождении такой структуры достаточно большого размера проецирует ее на NEW_IMAGE
    :param key: правило для вычисления id второго пикселя в паре (по сути определяет 1 из двух вариантов:
        1) второй пиксель ниже текущего, key = 1
        2) второй писель правее, key = 500
        Таким образом id второго пикселя = id первого + key
    )
    :param current_id: id текущего пикселя обозначает первый пиксель текущей пары
    :param ways_ind: список чисел из HORIZONATL_FRAME или VERTICAL_FRAME которые прибавляются к текущему id
    для вычисления следующего
    :param image: Матрица изображения
    :return:
    '''
    global POINTS, USED
    all_good = False
    y2, x2, y1, x1 = 0, 0, 0, 0

    current_id_inside = (current_id <= SIZE * SIZE) and (current_id > 0)
    second_id = current_id + key
    second_id_inside = (second_id <= SIZE * SIZE) and (second_id > 0)
    if current_id_inside and second_id_inside:
        # Проверим чтобь оба пикселя не были черными Конечно согласно алгоритму Ву пара принадлежащая линии
        # должна давать суммарную яркость 255 но из за зашумления это условие с большой вероятностью будет нарушено
        # Однако если мы встретим пару из 0 и 255-254 то ее мы тоже засчитаем потому что даже если она получена
        # из за шума вероятность на это довольно мала
        y1, x1 = get_coordinates(current_id)
        y2, x2 = get_coordinates(second_id)
        correction = (254, 255)
        all_good = (image[y1][x1] != 0 and image[y2][x2] != 0) \
            or (image[y1][x1] in correction and image[y2][x2] == 0) \
            or (image[y2][x2] in correction and image[y1][x1] == 0)

    if all_good:
        pair_points = ((y2, x2), (y1, x1))
        POINTS.append(pair_points)
        for index in ways_ind:
            # в USED для каждого id лист из 14 bool значений первая половина для VERTICAL_FRAME
            # вторая для HORIZONTAL_FRAME
            if key == 500:
                if not USED[current_id][index]:
                    USED[current_id][index] = True
                    search_cluster(key, current_id + VERTICAL_FRAME[index], ways_ind, image)
            if key == 1:
                if not USED[current_id][7 + index]:
                    USED[current_id][7 + index] = True
                    search_cluster(key, current_id + HORIZONTAL_FRAME[index], ways_ind, image)
        POINTS.pop()
    else:
        # Если дошли до конца или просто наткнулись на несоответствующую пару то анализируем что успели собрать
        limit = 50
        if len(POINTS) > limit:
            draw()


def DFS(v):
    """
    Обход графа в глубину
    :param v: вершина из которой происходит обход в данный момент
    :return:
    """
    global G_USED, GRAPH, COMPONENT
    G_USED[v] = True
    COMPONENT.append(v)
    for point in GRAPH[v]:
        if not G_USED[point]:
            DFS(point)


def build_graph():
    '''
    Строим граф на основе данных
    Вершины это все белые ячейки в двумерном листе дата считаем что две соседние такие вершины соединены ребрами
    :param data:
    :return:
    '''
    global GRAPH, NEW_IMAGE
    for i in range(SIZE):
        for j in range(SIZE):
            c = NEW_IMAGE[i][j]
            c_id = get_id(i, j)
            if c != 0:
                if j + 1 < SIZE:
                    r = NEW_IMAGE[i][j + 1]
                    r_id = get_id(i, j + 1)
                    if r != 0:
                        GRAPH[r_id].append(c_id)
                        GRAPH[c_id].append(r_id)
                if i + 1 < SIZE:
                    d = NEW_IMAGE[i + 1][j]
                    d_id = get_id(i + 1, j)
                    if d != 0:
                        GRAPH[d_id].append(c_id)
                        GRAPH[c_id].append(d_id)


def collect_extra_components():
    """
    После построения графа обойдем его элементы Будем считать что компоненты меньше определенного размера скорее
    являются случайными чем принадлежат треугольнику (На малых уровнях зашумления это почти всегда так и есть) поэтому
    отбросим их
    Хоть такой метод и построен на допущении и существует значительная вероятность потерять часть треугольника как
    правило большая часть тругольника все же остается и приблизительные координаты все еще можно восстановить
    :return:
    """
    global COMPONENT, G_USED
    extra_components = []
    limit = 190
    for element in range(1, SIZE * SIZE + 1, 1):
        if not G_USED[element]:
            COMPONENT = []
            DFS(element)
            if len(COMPONENT) < limit:
                extra_components.append(COMPONENT[:])
    return extra_components


def check_vicinity(y, x):
    """
    Функция осматривает окрестность точки с координатами y ,x на наличие белых (то есть принадлежащих треугольнику
    точек) на NEW_IMAGE Если таких точек несколько то берем среднее из их координат и возвращаем его как точку
    пересечения
    :param y: координата y
    :param x: координата x
    :return: координаты точки пересечения
    """
    global NEW_IMAGE
    vicinity_inter = ()
    frame = [0, 1, 1 + 500, 500, -1 + 500, -1, -1 - 500, -500, 1 - 500]
    start_id = get_id(-y, x)
    for direction in frame:
        near_id = start_id + direction
        if (near_id <= SIZE * SIZE) and (near_id >= 1):
            y, x = get_coordinates(near_id)
            if NEW_IMAGE[y][x] != 0:
                point = (-y, x)
                if not vicinity_inter:
                    vicinity_inter = point
                else:
                    y1, x1 = vicinity_inter
                    new_point = ((y1 - y) / 2, (x1 + x) / 2)
                    vicinity_inter = new_point
    return vicinity_inter


def intersect(k, b, steep):
    """
    Функция ищет точки пересечения прямой заданной коэффициентами k и b (y = k*x + b) с треугольником уже прошедшим
    очистку от шума и заданным на NEW_IMAGE
    :param k: коэффициент в уравнении прямой
    :param b: коэффициент в уравнении прямой
    :param steep: Определяет порядок обхода точек прямой и зависит от наклона
    :return:
    """
    global NEW_IMAGE
    intersections = []
    offset = 2
    if steep:
        for y in range(0, -500, -1):
            x = int((y - b) / k)
            if (x < 500) and (x >= 0):
                inter_area = check_vicinity(y, x)
                if inter_area:
                    inter_y, inter_x = inter_area
                    # Поиск ближайших точек и объединение их в одну
                    for index in range(len(intersections)):
                        other = intersections[index]
                        y1, x1 = other
                        distance = ((y1 - inter_y) ** 2 + (x1 - inter_x) ** 2) ** 0.5
                        if distance <= offset:
                            other = ((y1 + inter_y) / 2, (x1 + inter_x) / 2)
                            intersections[index] = other
                            break
                    else:
                        intersections.append(inter_area)

    else:
        for x in range(500):
            y = int(k * x + b)
            if (y > -500) and (y <= 0):
                inter_area = check_vicinity(y, x)
                if inter_area:
                    inter_y, inter_x = inter_area
                    for index in range(len(intersections)):
                        other = intersections[index]
                        y1, x1 = other
                        distance = ((y1 - inter_y) ** 2 + (x1 - inter_x) ** 2) ** 0.5
                        if distance <= offset:
                            other = ((y1 + inter_y) / 2, (x1 + inter_x) / 2)
                            intersections[index] = other
                            break
                    else:
                        intersections.append(inter_area)

    return intersections


def main(img):
    '''
    Восстановление проходит в 2 этапа
    1) Сначала мы ищем все скопления точек которые могут быть сторонами (Поскольку алгоритм отрисовывает точки парами
    то такие скопления будут выглядеть как ступенчатые структуры) При нахождении достаточно большого такого скопления
    оно 'отрисовывается' на изначально пустой матрице NEW_IMAGE Таким после окончания первого этапа мы получим
    достаточо грубую копию треугольника в NEW_IMAGE

    Далее чтобы избавится от случайных линий которые появляются на большом уровне шума
    Мы строим граф который описывает связи белых точек и очерняем явно неподходящие компоненты

    Данный метод неплохо себя показывает вплоть до уровня зашумления 0.5
    Обычно при уровне 0.5 изображение полученное в NEW_IMAGE выглядит немного размытый треугольник с немного рваными
    сторонами
    2) Считая что в NEW_IMAGE мы имеем только 2 типа точек:
        1) черные - не принадлежат треугольнику
        2) белые - принадлежат
    Можно достаточно просто найти координаты
    Сначала найдем самую левую и самую правую белую точку (первые 2 вершины)
    Обозначим прямую на которой лежит сторона связывающая эти 2 вершины как A
    Для того чтобы найти последнююю вершину достаточно просто смещать прмяую А параллельно самой себе вверх или вниз
    до тех пор пока не найдем место где она перескает тругольник в одном месте
    Когда мы найдем
    :param img:
    :return corners: вершины треугольника
    '''
    global POINTS, USED, NEW_IMAGE
    # Первый этап
    first_half = [i for i in range(0, 4, 1)]
    second_half = [i for i in range(3, 7, 1)]
    for i in range(SIZE):
        for j in range(SIZE):
            first_point = img[i][j]
            if first_point != 0:
                first_id = get_id(i, j)
                # Вертикально ориентирована вниз и вправо
                search_cluster(500, first_id, first_half, img)

                # Вертикально ориентирована вниз и влево
                search_cluster(500, first_id, second_half, img)

                # Горизонтально ориентирована вниз и вправо
                search_cluster(1, first_id, first_half, img)

                # Горизонтально ориентирована вниз и влево
                search_cluster(1, first_id, second_half, img)
    build_graph()
    extra_clusters = collect_extra_components()
    for cluster in extra_clusters:
        for point in cluster:
            y, x = get_coordinates(point)
            NEW_IMAGE[y][x] = 0

    # Второй этап
    corners = []
    found = False
    # поиск самой левой вершины
    right_vicinity = [-500, -500 + 1, 1, 1 + 500, 500]
    for i in range(SIZE):
        for j in range(SIZE):
            if NEW_IMAGE[j][i] != 0:
                corner = (j, i)
                corner_id = get_id(j, i)
                empty_right = True

                # Проверим окрестность
                for direction in right_vicinity:
                    near_id = corner_id + direction
                    if (near_id >= 1) and (near_id <= SIZE * SIZE):
                        ny, nx = get_coordinates(near_id)
                        if NEW_IMAGE[ny][nx] != 0:
                            empty_right = False
                            y, x = corner
                            corner = ((y + ny) / 2, (x + nx) / 2)
                # Если окрестность оказалась непустой тогда добавим точку

                if not empty_right:
                    corners.append(corner)
                    found = True
                    break
        if found:
            break

    found = False
    # поиск самой правой вершины
    left_vicinity = [-500, -500 - 1, -1, -1 + 500, 500]
    for i in range(SIZE - 1, -1, -1):
        for j in range(SIZE):
            if NEW_IMAGE[j][i] != 0:
                corner = (j, i)
                corner_id = get_id(j, i)
                empty_left = True

                # Проврим окрестность
                for direction in left_vicinity:
                    near_id = corner_id + direction
                    if (near_id >= 1) and (near_id <= SIZE * SIZE):
                        ny, nx = get_coordinates(near_id)
                        if NEW_IMAGE[ny][nx] != 0:
                            empty_left = False
                            y, x = corner
                            corner = ((y + ny) / 2, (x + nx) / 2)

                # Если окрестность непустая то добавим точку
                if not empty_left:
                    corners.append(corner)
                    found = True
                    break
        if found:
            break

    # Поиск последней вершины
    y1, x1 = corners[0]
    y2, x2 = corners[1]
    y1 = -y1
    y2 = -y2

    # Обозначим прямую А через параметры k и b в уравнении y = k*x + b
    k = (y2 - y1) / (x2 - x1)
    b = y2 - k * x2
    steep = abs(y2 - y1) > abs(x2 - x1)
    """
    steep дает понять как обходить точки принадлежащие прямой
    1) Перебор y и вычисление x (steep = True)
    2) Перебор x и вычисление y (steep = False
    """

    """
    Теперь надо понять в каком направлении двигать прямую для этого последовательно отступим вниз и вверх
    И пойдем в ту сторону в которой количество пересечений было ненулевым
    переменная direction определяющая направление равна +1 или -1 и определеяет изменение b
    """
    # Определение направления
    test_dir = 0
    offset = 20
    direction = 1
    for new_b in range(int(b) + offset, int(b) + offset + 5):
        quantity = len(intersect(k, new_b, steep))
        test_dir += quantity

    if test_dir == 0:
        direction = -1

    # Поиск в установленном направлении
    vicinity = []

    """
    Причиной остановить поиск будет момент когда мы наткнулись на место где тругольник уже закончился
    Поскольку линия может прерываться будем считать что мы вышли за пределы если количество линий 
    подряд не пересекающих ничего (void_cases) превысило void_limit
    """
    void_faced = False
    void_cases_in_a_row = 0
    void_limit = 6
    curr_b = b + offset * direction
    while not void_faced:
        curr_inter = intersect(k, curr_b, steep)
        if len(curr_inter) == 1:
            vicinity.append(curr_inter[0])
            void_cases_in_a_row = 0
        elif len(curr_inter) == 0:
            void_cases_in_a_row += 1
        else:
            void_cases_in_a_row = 0
        curr_b += direction
        void_faced = void_cases_in_a_row >= void_limit

    # Объединение точек для установления окончательных координат третьей вершины
    last_y, last_x = 0, 0
    for (curr_y, curr_x) in vicinity:
        last_y += curr_y
        last_x += curr_x

    if vicinity:
        last_y = -1 * (last_y / len(vicinity))
        last_x = last_x / len(vicinity)
        last_corner = (last_y, last_x)
    else:
        last_corner = (0, 0)
    corners.append(last_corner)

    return corners
