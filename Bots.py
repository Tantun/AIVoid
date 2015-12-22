import math
import random
import numpy as np

from Game import *


class Bot:
    # A bot that just plays the game using the values Theta1 and Theta2 for neural network parameters
    def __init__(self, Theta1, Theta2, game):
        self.Theta1 = Theta1
        self.Theta2 = Theta2
        self.game = game


        
    def Sigmoid(self, x):
        return (1 + math.exp((-1)*x))**(-1)

    
    
    def PreProcess(self, action):
        # Use the relative coordinates of the falling objects to generate the input numpy vector the neural network (exploit game symmetry to use only one net)
        state_new = []
        for aster in self.game.asteroids:          # Scaling input values
            state_new.append(aster[0]/(self.game.Halfwidth+0.0))
            state_new.append(aster[1]/(self.game.Height+0.0))
        state_new.append(1)     # Add the bias term
        if action == 'L':
            for i in range(self.game.N):
                state_new[2*i] *= -1
        layer1 = np.empty([2*self.game.N+1,1])
        for i in range(2*self.game.N+1):
            layer1[i, 0] = state_new[i]
        return layer1

    

    def ForwardPropagate(self, action):
        # Evalue the neural network for the current game state with the given L/R action; Returns triple of values/vectors (one for each layer)
        layer1 = self.PreProcess(action)
        layer2_temp = np.dot(np.transpose(self.Theta1), layer1)
        for i in range(layer2_temp.shape[0]):
            layer2_temp[i,0] = self.Sigmoid(layer2_temp[i,0])
        layer2 = np.append(layer2_temp, [[1]], axis=0)
        layer3 = np.dot(np.transpose(self.Theta2), layer2)
        result = self.Sigmoid(layer3[0,0])
        return (layer1, layer2, result)


    
    def TestStep(self):
        # Determines the optimal direction in the next move by using the given Theta1, Theta2 parameters
        outputL = self.ForwardPropagate('L')
        outputR = self.ForwardPropagate('R')
        if outputL[-1] < outputR[-1]:
            self.game.ChangeDirection('L')
        else:
            self.game.ChangeDirection('R')
        result = self.game.GameOver()
        return result






class BotTrain(Bot):
    # A bot that performs reinforcement learning to opitmize the Theta1, Theta2 parameters in the neural network
    def __init__(self, GameParameters, HiddenSize=12, gamma=0.9995, GameOverCost=1, NSim=500, NTest=100, TestTreshold=200, NumberOfSessions=None, Inertia=0.8, p=0.0, a=1.0, epsilon=0.2, epsilon_decay_rate=1):
        Theta1 = np.random.uniform(-1.0, 1.0, (2*GameParameters["N"]+1, HiddenSize))
        Theta2 = np.random.uniform(-1.0, 1.0, (HiddenSize+1, 1))        
        game = Game(**GameParameters)
        Bot.__init__(self, Theta1, Theta2, game)

        self.GameParameters = GameParameters        
        self.HiddenSize = HiddenSize     # Size of the neural network hidden layer 
        self.gamma = gamma     # gamma parameter in the game cost function E[gamma^N]
        self.GameOverCost = GameOverCost     # Game Over Cost (set to 1.0 for standard game cost function E[gamma^N])
        self.NSim = NSim     # Number of consecutive learning games
        self.NTest = NTest     # Number of consecutive test games
        self.TestTreshold = TestTreshold    # Stop learning when median test score goes over TestTreshold (set to None for fixed number of sessions)
        self.NumberOfSessions = NumberOfSessions     # Number of learn train/test session (active only if TestTreshold = None)
        self.Inertia = Inertia     # (1 - Inertia) is the probability of resampling the game direction while learning
        self.p = p     # Probability of chosing learned move in reinforcement learning        
        self.a = a     # Reinforcement learning rate (set to 1.0 since it can be absorbed into gradient descent step factor)
        self.epsilon = epsilon     # Initial gradient descent step factor
        self.epsilon_decay_rate = epsilon_decay_rate     # Exponent in power decay for the gradient descent step factor

        self.counter = []    # Container for average and median test scores
    

        
    def BackPropagate(self, output, expected, layer1, layer2):
        # Backpropagation algorithm for neural network; computes the partial derivatives with respect to parameters and performs the stochastic gradient descent
        delta3 = output - expected
        delta2 = delta3*self.Theta2
        for i in range(self.HiddenSize):
            delta2[i,0] *= layer2[i,0]*(1-layer2[i,0])
        for i in range(2*self.game.N+1):
            for j in range(self.HiddenSize):
                self.Theta1[i,j] -= self.epsilon*layer1[i,0]*delta2[j,0]
        for i in range(self.HiddenSize+1):
            self.Theta2[i,0] -= self.epsilon*delta3*layer2[i,0]
  

            
    def ReinforcedLearningStep(self):
        # Performs one step of reinforcement learning
        t = random.random()
        if t < 1-self.p:
            tt = random.random()
            if tt < self.Inertia:
                output = self.ForwardPropagate(self.game.Direction)
            else:
                new_direction = random.choice(['L','R'])
                output = self.ForwardPropagate(new_direction)
                self.game.ChangeDirection(new_direction)
        else:
            outputL = self.ForwardPropagate('L')
            outputR = self.ForwardPropagate('R')
            if outputL[-1] < outputR[-1]:
                output = outputL
                self.game.ChangeDirection('L')
            else:
                output = outputR
                self.game.ChangeDirection('R')
                
        if random.random()<0.00002:
            # Occasionally prints out the current value of the network (useful for adjusting various learning parameters, especially gamma)
            print output[-1]
            
        result = self.game.UpdateStep()
        if result[-1]:
            estimate = self.GameOverCost
        else:
            estimateL = self.ForwardPropagate('L')
            estimateR = self.ForwardPropagate('R')
            estimate = min(estimateL[-1], estimateR[-1])
            if result[1]:
                estimate *= self.gamma
        expected = (1-self.a)*output[-1] + self.a*estimate
        self.BackPropagate(output[-1], expected, output[0], output[1])
        return result

    

    def Training(self):
        # Run NSim consecutive training games
        for i in range(self.NSim):
            stop = False
            while not stop:
                (update, kill, stop) = self.ReinforcedLearningStep()
            self.game = Game(**self.GameParameters)

            
            
    def Testing(self):
        # Run NTest consecutive test games to evaluate learned performance; prints out all the test values and records average and median values
        s = 0
        alist = []
        for i in range(self.NTest):
            stop = False
            while not stop:
                stop = self.TestStep()
                self.game.UpdateStep()
            alist.append(self.game.counter)
            self.game = Game(**self.GameParameters)
        print alist
        m1 = sum(alist)/(len(alist)+0.0)
        m2 = np.median(alist)
        self.counter.append((m1,m2))

        

    def TrainSession(self):
        # Performs a learning session until median scores achieves TestTreshold or for fixed number of learn/test sessions
        self.Testing()
        keep_going = True
        i = 0
        while keep_going:
            i += 1
            self.Training()
            self.Testing()
            print
            print "N:", self.game.N
            print "Session:", i
            print "Test Results:", self.counter
            new, old = self.counter[-1][-1], self.counter[-2][-1]
            self.epsilon *= (old/new)**self.epsilon_decay_rate
            print "Gradient Learning Rate:", self.epsilon
            print
            if self.TestTreshold == None and not self.NumberOfSessions == None:
                if i >= self.NumberOfSessions:
                    keep_going = False
            elif not self.TestTreshold == None:                 
                if self.counter[-1][-1] >= self.TestTreshold:
                    keep_going = False

            
            


             
