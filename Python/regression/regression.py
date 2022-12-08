import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math


def find_regression_line(coordinate:list):
    x = []
    y = []
    for coo in coordinate:
        x.append(coo[0])
        y.append(coo[1])
    y = np.polyfit(x, y, 1)     #https://numpy.org/doc/stable/reference/generated/numpy.polyfit.html
    return y                    #let y = ax+b ,a = y[0], b = y[1] 

#https://zhuanlan.zhihu.com/p/344482100
def euclidean_distance(coordinate:list, y:list):
    k = y[0]
    h = y[1]
    Distance = []
    for (i,j) in coo:
        Distance.append(math.fabs(h+k*i-j)/(math.sqrt(k*k+1)))
    return Distance

if __name__ == '__main__':
    coo = [(2,5), (3,7), (4,8), (5,17),(8,19),(4,10)]
    y = find_regression_line(coo)
    print(y)
    D = euclidean_distance(coo,y)
    print(D)