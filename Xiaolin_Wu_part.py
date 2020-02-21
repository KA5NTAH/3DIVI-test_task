"""
Функция реализует алгоритм Ву который отрисовывает линию со сглаживанием
"""
import math


def plot(img, x, y, brightness):
    b = math.floor(255 * brightness)
    img[min(x, 499)][min(y, 499)] = b


def ipart(x):
    return math.floor(x)


def r_round(x):
    return ipart(x + 0.5)


def fpart(x):
    return x - ipart(x)


def rfpart(x):
    return 1 - fpart(x)


def wu_algorithm(img, x0, y0, x1, y1):
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = 0
    if dx == 0:
        gradient = 1
    else:
        gradient = dy / dx

    # Начальная точка
    x_end = r_round(x0)
    y_end = y0 + gradient * (x_end - x0)
    x_gap = rfpart(x0 + 0.5)
    x_pxl1 = x_end
    y_pxl1 = ipart(y_end)
    if steep:
        plot(img, y_pxl1, x_pxl1, rfpart(y_end) * x_gap)
        plot(img, y_pxl1 + 1, x_pxl1, fpart(y_end) * x_gap)
    else:
        plot(img, x_pxl1, y_pxl1, rfpart(y_end) * x_gap)
        plot(img, x_pxl1, y_pxl1 + 1, fpart(y_end) * x_gap)
    inter_y = y_end + gradient

    # Конечная точка
    x_end = r_round(x1)
    y_end = y1 + gradient * (x_end - x1)
    x_gap = fpart(x1 + 0.5)
    x_pxl2 = x_end
    y_pxl2 = ipart(y_end)
    if steep:
        plot(img, y_pxl2, x_pxl2, rfpart(y_end) * x_gap)
        plot(img, y_pxl2 + 1, x_pxl2, fpart(y_end) * x_gap)
    else:
        plot(img, x_pxl2, y_pxl2, rfpart(y_end) * x_gap)
        plot(img, x_pxl2, y_pxl2, fpart(y_end) * x_gap)

    # Линия
    for x in range(x_pxl1 + 1, x_pxl2, 1):
        if steep:
            plot(img, ipart(inter_y), x, rfpart(inter_y))
            plot(img, ipart(inter_y) + 1, x, fpart(inter_y))
        else:
            plot(img, x, ipart(inter_y), rfpart(inter_y))
            plot(img, x, ipart(inter_y) + 1, fpart(inter_y))
        inter_y += gradient
