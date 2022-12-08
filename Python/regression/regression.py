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
    line = np.polyfit(x, y, 1)     #https://numpy.org/doc/stable/reference/generated/numpy.polyfit.html
    return line                    #let line = ax+b ,a = line[0], b = line[1] 

def euclidean_distance(coordinate:list, line:list):
    k = line[0]
    h = line[1]
    Distance = []
    for (x,y) in coordinate:
        Distance.append(math.fabs(h+k*x-y)/(math.sqrt(k*k+1)))  #https://zhuanlan.zhihu.com/p/344482100
    return Distance

def objection(coordinate:list, line:list):
    k = line[0]
    h = line[1]
    obj = []
    for (x,y) in coordinate:
        obj.append(((k*(y-h)+x)/(k*k+1) , k*(k*(y-h)+x)/(k*k+1)+h))
    return obj
if __name__ == '__main__':
    coo = [(2,5), (3,7), (4,8), (5,17),(4,10)]
    L = find_regression_line(coo)
    print(L)
    D = euclidean_distance(coo,L)
    print(D)
    O = objection(coo,L)
    print(O)