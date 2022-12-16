import random
import math

def circle_diverge(coo:list,R:float,num:int):
    x_total = 0
    y_total = 0
    points = []
    n = len(coo)
    for (x,y) in coo:
        x_total = x_total + x
        y_total = y_total + y
    (x_avg,y_avg) = ( x_total / n , y_total / n)
    for i in range(0,num):
        theta = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, R)
        x = x_avg + r * math.cos(theta)
        y = y_avg + r * math.sin(theta)
        points.append((x,y))
    return points


if __name__ == '__main__':
    coo = [(2,5), (3,7), (4,8), (5,17),(4,10)]
    points = circle_diverge(coo,1,10)
    print(points)