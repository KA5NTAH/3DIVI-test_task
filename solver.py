import sys
import random
import math
import Xiaolin_Wu_part as XW
import restore_part


PI = math.pi
SIZE = 500


def read_pgm(name):
    """
    Представляет изображение в формате pgm в формате двумерного листа где каждый элемент опписывает соттветсвущий
    пиксель числом от 0 до 255
    :param name:
    :return data:
    """
    with open(name, "rb") as f:
        lines = f.readlines()

    # Converts data to a list of integers
    data = []
    for line in lines[3:]:
        data1 = []
        data1.extend([int(c) for c in line.split()])
        data.append(data1)
    return data


def paint(img_path, data):
    """
    Создает изображение в формате PGM на основе данных описывающих каждый пиксель изображения
    в формате числа от 0 до 255
    :param img_path: Путь изобаржения
    :param data: данные о изображении
    :return:
    """
    with open(img_path, "wb") as file:
        header = "P2\n" + "500 500\n" + "255\n"
        header_byte = bytearray(header, "utf-8")
        file.write(header_byte)
        for row in data:
            current = ""
            for element in row:
                current += (str(element) + " ")
            current += "\n"
            current_row = bytearray(current, "utf-8")
            file.write(current_row)


def generate(p):
    """
    Генерация изображения с уровенем шума P
    Производится в несколько этпов
    1) Сгенерируем координаты треугольника который удовлетворит следующим требованиям:
        1) Длина наименьшей стороны больше 100
        2) Наименьший угол больше 30
    2) Отрисовка линий в соответствии с алгоритмом Ву
        1) Подготовим данные
        2) Запишем их в изображение
    3) Произведем зашумление
    """
    # Первый этап : Координаты удовлетворяюие требованиям
    good_coordinates = False
    points = []
    while not good_coordinates:
        # Сгенериурем координаты
        for i in range(3):
            x = random.randrange(500)
            y = random.randrange(500)
            points.append((x, y))

        # Посчитаем длины сторон
        len_sides = []
        for i in range(3):
            point1 = points[i]
            point2 = points[(i + 1) % 3]  # Чтобы для последней точки следующей была первая
            diff_x = point2[0] - point1[0]
            diff_y = point2[1] - point1[1]
            curr_length = (diff_x ** 2 + diff_y ** 2) ** 0.5
            len_sides.append(curr_length)

        # Посчитаем углы
        angles = []
        for i in range(3):
            # Зададим 2 вектора соответствующие сторонам
            # исходящим из текущей точки
            start = points[i]
            to1 = points[(i + 1) % 3]  # Следующая точка в списке
            to2 = points[(i + 2) % 3]  # Предыдущая точка в списке
            vector1 = (to1[0] - start[0], to1[1] - start[1])
            vector2 = (to2[0] - start[0], to2[1] - start[1])

            # Посчитаем косинус угла через скалярное произведение
            scalar_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
            len1 = (vector1[0] ** 2 + vector1[1] ** 2) ** 0.5
            len2 = (vector2[0] ** 2 + vector2[1] ** 2) ** 0.5
            cos = scalar_product / (len1 * len2)
            angle_rad = math.acos(cos)
            angle = angle_rad * 360 / 2 / PI  # Переведем радианы в градусы
            angles.append(angle)

        # Теперь проверим подходит ли текущий треугольник под условия
        good_coordinates = (min(angles) > 30) and (min(len_sides) > 100)
        if not good_coordinates:
            points.clear()

    # Второй этап : Подготовим данные с отрисовкой
    image = [[0 for i in range(500)] for i in range(500)]
    for i in range(3):
        # координаты в обратном порядке потому что в двумерном массиве первый индекс соответствует y второй x
        y0, x0 = points[i]
        y1, x1 = points[(i + 1) % 3]
        XW.wu_algorithm(image, x0, y0, x1, y1)

    # Третий этап (зашумление)
    prob = p * 100
    for i in range(500):
        for j in range(500):
            # Сгенерируем случайное значние чтобы понять зашумлять данный пиксель или нет
            roll = random.randrange(1, 101, 1)
            if roll <= prob:
                replacement = random.randrange(256)
                image[i][j] = replacement

    # Запись в файл
    paint("image.pgm", image)


def restore(img_path):
    """
    Вычисляет координты тругольника на основе зашумленного изображения и записывает в файл output.txt
    :param img_path: Зашумленное изображение
    :return:
    """
    # чтение файла
    img = read_pgm(img_path)
    corners = restore_part.main(img)
    with open("output.txt", "w") as answer:
        for corner in corners:
            y, x = corner
            answer.write(str(x) + " " + str(y) + "\n")


mode = sys.argv[1]
if mode == "-restore":
    image_path = sys.argv[2]
    restore(image_path)
elif mode == "-generate":
    p = float(sys.argv[2])
    generate(p)
