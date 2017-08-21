import math
import random

random.seed()


class Game:
    # This is the main game class that is used by both the GUI module and the AI module
    def __init__(self, N=4, DownSideRatio=3, SleepTime=5, R=25, r=5, Height=400, Halfwidth=200,
                 GlobalHeight=600, GlobalWidth=800, Thickness=20, RandomTreshold=0.2, RandomStep=1,
                 RandomVertTreshold=0.2, RandomVertStep=1, MaxScore=None):
        self.N = N     # number of falling objects
        self.DownSideRatio = DownSideRatio     # ratio fall speed/left-right speed (integer)
        self.SleepTime = SleepTime     # delay time between steps, game is progressing slower for higher values
        self.R = R     # radius of the blue half circle
        self.r = r     # radius of the falling objects
        self.treshold = (R +r/2)**2      # treshold to indicate the contact for game over
        self.Height = Height     # height of the white structure
        self.Halfwidth = Halfwidth     # half width of the white structure
        self.GlobalHeight = GlobalHeight     # height of the game window
        self.GlobalWidth = GlobalWidth     # width of the game window
        self.Thickness = Thickness     # thickness of the white walls
        self.RandomTreshold = RandomTreshold     # probability of left/right noise for falling objects
        self.RandomStep = RandomStep     # intensity of left/right noise for falling objects
        self.RandomVertTreshold = RandomVertTreshold     # probability of up/down noise for falling objects
        self.RandomVertStep = RandomVertStep     # intensity of up/down noise for falling objects
        self.MaxScore = MaxScore     # Maximum Score before terminating the game (None for infinity)
        
        self.Direction = random.choice(['L','R'])     # setting the initial direction
        self.steps, self.counter = 0, 0     # total pixel moves (time) and total score
        self.asteroids = []     # relative coordinates of the falling objects
        for i in range(N):         # initialize the falling objects' coordinates
            t = random.random()
            if t < 0.5:
                x = (-1)*(Halfwidth + R)/2 - t*(Halfwidth-R)
            else:
                x = (Halfwidth + R)/2 + (t-0.5)*(Halfwidth-R)
            self.asteroids.append([x,2*Height/3+(i+1)*Height/(3*N)])
   

    def ChangeDirection(self, direction):
        if direction == 'L':
            self.Direction = 'L'
        if direction == 'R':
            self.Direction = 'R'

            
    def GameOver(self):
        # Testing for game over
        for aster in self.asteroids:
            if aster[0]**2 + aster[1]**2 < self.treshold:
                return True
        if not self.MaxScore == None and self.counter >= self.MaxScore:
            return True
        return False

    
    def Destroy(self):
        # updating falling objects when one gets destroyed (and testing for that scenario)
        Kill = False
        for i in range(self.N):
            if self.asteroids[i][0] <= (-1)*self.Halfwidth or self.asteroids[i][0] >= self.Halfwidth or self.asteroids[i][1] <= 0:
                Kill = True
                self.asteroids.pop(i)
                self.asteroids.append([(2*random.random()-1)*self.Halfwidth, self.Height])
                self.counter += 1
        return Kill


    def UpdateStep(self):
        # Updating locations of falling objects at pixel moves.
        # Returns triple to determine:
            # 1. whether one needs to force refresh the screen due to destroyed objects or because noise was added;
            # 2. whether a falling object was destroyed and one point obtained;
            # 3. whether the game is over;
        self.steps += 1
        for i in range(self.N):          
            self.asteroids[i][1] -= self.DownSideRatio
            if self.Direction == 'L':
                self.asteroids[i][0] += 1
            if self.Direction == 'R':
                self.asteroids[i][0] -= 1

        Update = False
        for i in range(self.N):          #  Adding the noise to falling objects
            t1, t2 = random.random(), random.random()
            if t1 < self.RandomTreshold/2:
                Update = True
                self.asteroids[i][0] += self.RandomStep
            elif t1 < self.RandomTreshold:
                Update = True
                self.asteroids[i][0] -= self.RandomStep
            if t2 < self.RandomVertTreshold/2:
                Update = True
                self.asteroids[i][1] += self.RandomVertStep
            elif t2 < self.RandomVertTreshold:
                Update = True
                self.asteroids[i][1] -= self.RandomVertStep

        Kill = self.Destroy()
        if Kill:
            Update = True
        Over = self.GameOver()
        return (Update, Kill, Over)

    


