from __future__ import generators
from scipy import stats
import simpy
# To samples from a discrete distribution,
# use X = stats.rv_discrete(values = (xk, pk)),
# Where xk are integer values to pick from, and pk are the values (non-zero)
# to define a random variable X. Then choose a number with X.random()

# Car speed at certain node

PathChoice = stats.rv_discrete(values = ([-5, 1], [0.5, 0.5]))
print(PathChoice.rvs(size = 5))

class Car_generator():
    # Needs to know where to put cars, speed of generation
    def __init__(self):
        pass

class Car(object):
    # Needs to know speed at position it is in, probability
    # of transition to different spots.
    def __init__(self):
        pass

env = simpy.Environment()

left  = simpy.Resource(env, capacity = 2)
right = simpy.Resource(env, capacity = 2)