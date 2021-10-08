from math import log10

import pandas as pd
from scipy.optimize import least_squares

df = pd.read_csv('./comments-sequential.csv', index_col=0)

def residual(variables):
    a, b = variables
    trend = [a * log10(max(i, 1)) + b for i in range(10)]

    return df.apply(lambda row: sum(abs(row - trend)), axis=1).fillna(0)


lm = least_squares(residual, [-0.1, 1])
print(lm.x, lm.cost, lm.optimality)
