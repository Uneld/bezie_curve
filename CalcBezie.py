class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def de_casteljau(p0, p1, p2, p3, t):
    q0 = Point(p0.x + t * (p1.x - p0.x), p0.y + t * (p1.y - p0.y))
    q1 = Point(p1.x + t * (p2.x - p1.x), p1.y + t * (p2.y - p1.y))
    q2 = Point(p2.x + t * (p3.x - p2.x), p2.y + t * (p3.y - p2.y))

    r0 = Point(q0.x + t * (q1.x - q0.x), q0.y + t * (q1.y - q0.y))
    r1 = Point(q1.x + t * (q2.x - q1.x), q1.y + t * (q2.y - q1.y))

    p_final = Point(r0.x + t * (r1.x - r0.x), r0.y + t * (r1.y - r0.y))

    return p_final


if __name__ == '__main__':
    p0 = Point(0, 0)
    p1 = Point(0.0, 0.5)
    p2 = Point(1, 0.5)
    p3 = Point(1, 1)

    duration = 1.0
    time_step = 0.1
    t = 0.0
    x_list = []
    y_list = []
    while t <= 1.0:
        result = de_casteljau(p0, p1, p2, p3, t)
        x_list.append(result.x)
        y_list.append(result.y)
        # print(f"Точка на кривой Безье с параметром t={t} : ({result.x}, {result.y})")

        t += time_step / duration
    print(x_list)
    print(y_list)
