import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import minimize
from scipy.optimize import differential_evolution
from net_v2 import simulate
import time


def object_function(x):
    return simulate(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7])

def opt():

    x0 = [30, 30, 30, 30, 0.5, 0.5, 2, 3]
    bounds_power = [(0,100), (0,100), (0,100), (0,100), (0,1.), (0,1.), (0,10.), (0,10.)]

    opt_time = time.time()

    #result = minimize(object_function, x0, bounds = bounds_power)
    #result = minimize(object_function, x0, bounds = bounds_power,  method = "Nelder-Mead")
    result = differential_evolution(object_function, bounds = bounds_power, x0 = x0, popsize=6)

    opt_time = time.time() - opt_time

    print("Benötigte Zeit: ", opt_time)

    print(result)



if __name__ == "__main__":
    opt()