import random
import math
import numpy as np

from Game import *
from Bots import *
                       



GameParameters = {'N': 5, 'DownSideRatio': 3, 'SleepTime': 5, 'R': 25, 'r': 5, 'Height': 400, 'Halfwidth': 200,
                  'GlobalHeight': 600, 'GlobalWidth': 800, 'Thickness': 20, 'RandomTreshold': 0.2, 'RandomStep': 1,
                  'RandomVertTreshold': 0.2, 'RandomVertStep': 1, 'MaxScore': None}
LearnParameters = {'HiddenSize': 12, 'gamma': 0.8, 'GameOverCost': 1, 'NSim': 400, 'NTest': 400, 'TestTreshold': None,
                   'NumberOfSessions': 100, 'Inertia': 0.8, 'p': 0.0, 'a': 1.0, 'epsilon': 0.05,
                   'epsilon_decay_rate': 0.0, 'discount': 0.999, 'p_decay_rate': 0.5}

bot = BotTrain(GameParameters = GameParameters, **LearnParameters)
bot.TrainSession()

print bot.Theta1
print bot.Theta2
np.savez("Data/parameters", GameParameters = GameParameters, Theta1 = bot.Theta1, Theta2 = bot.Theta2)

