def solve_quadratic_equation(a, b, c):
    import math
    d = b * b - 4 * a * c
    assert d >= 0, "You put shitty a, b, c to solver"
    return (-b + math.sqrt(d)) / 2 / a, (-b - math.sqrt(d)) / 2 / a


def get_parabola(x0, y0):
    a = y0 / x0 / x0
    b = -2 * a * x0
    c = y0
    return a, b, c


def calc_parabola(a, b, c, x):
    return a * x * x + b * x + c


def sigmoid(x):
    import math
    return 1 / (1 + math.exp(-x))


def block_reward_multiplier(x):
    import math
    target_point = 40_000_000_000
    x0 = math.pow(math.e, .15)
    x1 = (math.e - x0) / target_point
    return math.log(x0 + x * x1)
