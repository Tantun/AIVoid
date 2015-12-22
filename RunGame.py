from Tkinter import *
import random

from Game import *
from Bots import *


class Choose:
    # Window to chose Human/AI player
    def __init__(self):
        self.master = Tk()
        self.frame = Frame(self.master)
        self.frame.pack()

        howmany_options, howfast_options = [6,5,4], ['fast', 'medium', 'slow']
        self.howmany, self.howfast = IntVar(), StringVar()
        self.howmany.set(howmany_options[0])
        self.howfast.set(howfast_options[0])
        self.menu1=OptionMenu(self.master,self.howmany,*howmany_options)
        self.menu2=OptionMenu(self.master,self.howfast,*howfast_options)
        Label(font=("Purisa", 13),text="Number of objects").pack()
        self.menu1.pack()
        Label(font=("Purisa", 13),text="Game speed").pack()
        self.menu2.pack()

        Label(font=("Purisa", 13),text="Player").pack()
        self.button1 = Button(self.master, font=("Purisa", 12), text = "Human", command=self.human)
        self.button2 = Button(self.master, font=("Purisa", 12), text = "AI pre train", command=self.dumb_ai)
        self.button3 = Button(self.master, font=("Purisa", 12), text = "AI post train", command=self.ai)
        self.button1.pack(side=LEFT)
        self.button2.pack(side=LEFT)
        self.button3.pack(side=LEFT)

                
        self.who = None


        
    def human(self):
        self.who = 'human'
        self.master.destroy()


        
    def dumb_ai(self):
        self.who = 'dumb_ai'
        self.master.destroy()



    def ai(self):
        self.who = 'ai'
        self.master.destroy()
        





class Play:
    # General class implementing common features for both Human and AI player
    def __init__(self, GameParameters):        
        self.game = Game(**GameParameters)
        self.x = self.game.GlobalWidth/2
        self.y = self.game.GlobalHeight - self.game.Thickness

        self.master = Tk()
        self.canvas=Canvas(self.master, bg="black", width=self.game.GlobalWidth, height=self.game.GlobalHeight)
        self.canvas.pack()


        # Next draw permanent and variable (falling) game objects. Draw three copies of everything for smooth screen wrapping. 
        for i in range(3):            
            cx, cy = self.x+(i-1)*self.game.GlobalWidth, self.y
            self.canvas.create_oval(cx-self.game.R, cy+self.game.R, cx+self.game.R, cy-self.game.R, fill="blue", width = 0, tag = 'S')
            self.canvas.create_rectangle(cx-self.game.Halfwidth-self.game.Thickness-self.game.r, cy, cx+self.game.Halfwidth+self.game.Thickness+self.game.r, cy+self.game.Thickness, fill="white", width = 0, tag = 'S')
            self.canvas.create_rectangle(cx-self.game.Halfwidth-self.game.Thickness-self.game.r, cy-self.game.Height, cx-self.game.Halfwidth-self.game.r, cy+self.game.Thickness, fill="white", width = 0, tag = 'S')
            self.canvas.create_rectangle(cx+self.game.Halfwidth+self.game.r, cy-self.game.Height, cx+self.game.Halfwidth+self.game.Thickness+self.game.r, cy+self.game.Thickness, fill="white", width = 0, tag = 'S')

        for aster in self.game.asteroids:
            for i in range(3):
                cx, cy = self.x+(i-1)*self.game.GlobalWidth + aster[0], self.y - aster[1]
                self.canvas.create_oval(cx-self.game.r, cy+self.game.r, cx+self.game.r, cy-self.game.r, fill="red", width = 0, tag = 'A')            

        self.canvas.focus_set()
        

        
    def RunStep(self):
        # Moves objects on the screen
        if self.game.Direction == 'L':
            self.canvas.move('S', -1, 0)
            self.x -= 1
            if self.x < (-1)*self.game.GlobalWidth/2:
                self.x += self.game.GlobalWidth
                self.canvas.move('S', self.game.GlobalWidth, 0)                                    
        if self.game.Direction == 'R':
            self.canvas.move('S', 1, 0)
            self.x += 1
            if self.x > 3*self.game.GlobalWidth/2:
                self.x -= self.game.GlobalWidth
                self.canvas.move('S', (-1)*self.game.GlobalWidth, 0)
        self.canvas.move('A', 0, self.game.DownSideRatio)
        (Update, Kill, Over) = self.game.UpdateStep()
        if Update:
            self.canvas.itemconfig(self.text_id, text="Score: "+str(self.game.counter))
            self.canvas.delete('A')
            for aster in self.game.asteroids:
                for i in range(3):
                    cx, cy = self.x+(i-1)*self.game.GlobalWidth + aster[0], self.y - aster[1]
                    self.canvas.create_oval(cx-self.game.r, cy+self.game.r, cx+self.game.r, cy-self.game.r, fill="red", width = 0, tag = 'A')
        self.master.update()
        self.master.after(self.game.SleepTime)
        return Over


        



    
class PlayHuman(Play):
    # Play subclass for a human player
    def __init__(self, GameParameters):
        Play.__init__(self, GameParameters)
            
        self.text_id = self.canvas.create_text(0,0,anchor="nw",fill="white",font=("Purisa", 14),text="Space to start, Left/Right to change direction",tag='Text')
        self.canvas.bind("<Left>", self.left)
        self.canvas.bind("<Right>", self.right)
        self.canvas.bind("<space>", self.Run)            
            
                   
    def left(self, event):
        self.game.ChangeDirection('L')

        
    def right(self, event):
        self.game.ChangeDirection('R')

        
    def Run(self, event):
        Over = False
        while not Over:
            Over = Play.RunStep(self)
        
        
        



            
class PlayAI(Play):
    # Play subclass for an AI player
    def __init__(self, Theta1, Theta2, GameParameters):
        Play.__init__(self, GameParameters)
        self.bot = Bot(Theta1, Theta2, self.game)

        self.text_id = self.canvas.create_text(0,0,anchor="nw",fill="white",font=("Purisa", 14),text="Space to start",tag='Text')
        self.canvas.bind("<space>", self.Run)            

        
    def Run(self, event):
        Over = False
        while not Over:
            self.bot.TestStep()                    
            Over = Play.RunStep(self)


                               

        

            

            
choose = Choose()
choose.master.mainloop()
who = choose.who
howmany = choose.howmany.get()
FileDict = {4:'parameters4.npz', 5:'parameters5.npz', 6:'parameters6.npz'}
FileToOpen = FileDict[howmany]
SpeedDict = {'fast':5, 'medium':10, 'slow':15}
howfast = SpeedDict[choose.howfast.get()]

if who == 'human':
    GameParameters = {'N':howmany, 'DownSideRatio':3, 'SleepTime':howfast, 'R':25, 'r':5, 'Height':400, 'Halfwidth':200, 'GlobalHeight':600, 'GlobalWidth':800, 'Thickness':20, 'RandomTreshold':0.2, 'RandomStep':1, 'RandomVertTreshold':0.2, 'RandomVertStep':1, 'MaxScore':None}
    # GameParameters['N'], GameParameters['SleepTime'] = 7, 5  # Override selected settings
    app=PlayHuman(GameParameters)
    app.master.mainloop()

    print "Human Score:", app.game.counter


    
if who == 'ai':
    arrays = np.load(FileToOpen)
    GameParameters = arrays['GameParameters'][()]
    GameParameters['SleepTime'] = howfast
    Theta1 = arrays['Theta1']
    Theta2 = arrays['Theta2']

    app = PlayAI(Theta1, Theta2, GameParameters)
    app.master.mainloop()

    print "AI Score:", app.game.counter


    
if who == 'dumb_ai':
    arrays = np.load(FileToOpen)
    GameParameters = arrays['GameParameters'][()]
    GameParameters['SleepTime'] = howfast
    Theta1 = arrays['Theta1']
    Theta2 = arrays['Theta2']

    Theta1 = np.random.uniform(-1.0, 1.0, Theta1.shape)
    Theta2 = np.random.uniform(-1.0, 1.0, Theta2.shape)

    app = PlayAI(Theta1, Theta2, GameParameters)
    app.master.mainloop()

    print "Dumb AI Score:", app.game.counter


    

