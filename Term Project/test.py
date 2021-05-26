from cmu_112_graphics import *
import random
if not (LAST_UPDATED.month == 7 and LAST_UPDATED.day == 27):
    raise Exception("Please download the new version of the animation framework from the hw13 page!")
import math
import basic_graphics
from math import sqrt

class MapGenerator(App): # turn 2d list into drawings
    def appStarted(self): 
        self.grid = []
        self.unitList = [([0]* 32) for i in range(7)]
        for col in range(len(self.unitList)):
            for row in range(7):
                if random.choice([True,False]) == True:
                    num = random.randint(3,9)
                    k = random.randint(0, 32-num-1)
                    for i in range(num):
                        self.unitList[row][k + i] = 1
        self.r = 25
        self.rMax = self.r * 10
        self.rMin = self.r * 3
        self.rList = list(range(self.rMin + 1,self.rMax + 1, self.r))
        self.cX  = self.width // 2
        self.cY = self.height // 2
        i = 0
        self.arcList = []
        # self.yList = []
        n = row * 33 + col
        for r in self.rList[::-1]:
            for i in range(33):
                self.arcList.append(Arc(self,r,i))
        print(self.unitList)
        for arc in self.arcList:
            row = (arc.r - self.rMin) // self.r - 1
            col = i - 1
            if self.unitList[row][col] == 1:
                arc.color = "grey"

        def redrawAll(self,canvas):
            for arc in self.arcList:
                arc.render
            


    # def redrawAll(self,canvas):
    #     for row in range(len(self.unitList)):
    #         i = 0
    #         for col in range(len(self.unitList[0])):
    #             x0 = 40 + 25 * col
    #             y0 = 500 / 2 + 30 * row
    #             x1 = x0 + 25
    #             y1 = y0 + 30
    #             n = row * 33 + col
    #             if self.unitList[row][col] == 1:
    #                 color = "grey"
    #             elif self.unitList[row][col] == 0:
    #                 color = "white"
    #             canvas.create_rectangle(x0,y0,x1,y1,fill = color)
class Arc(object):
    """draws the unit geomtry"""
    def __init__(self,app,r,i):
        self.app = app
        self.r = r
        self.degree = 360 / 32
        self.ray = 2 * math.pi / 32
        self.i = i
        self.speed = 0.3
        self.cX  = self.app.width // 2
        self.cY = self.app.height // 2
        self.color = "white"
        self.angle = 2 * math.pi - self.ray * self.i
        self.point1 = self.cY - self.r * math.sin(self.angle - self.ray)
        self.point2 = self.cY - self.r * math.sin(self.angle)
        self.y = min(self.point1,self.point2)
        if self.r ** 2 - self.y ** 2 < 0:
            self.x = sqrt(-(self.r ** 2 - self.y ** 2))
        else:
            self.x = sqrt((self.r ** 2 - self.y ** 2))
    
    def rotate(self):
        self.i -= self.speed

    def isCollideUp(self):
        if - self.ray < (2 * math.pi - self.ray * self.i) % (math.pi * 2) < self.ray:
            return True
    
    def changeDirectionRight(self):
        self.speed = -0.3

    def changeDirectionLeft(self):
        self.speed = 0.3

    def rightCollide(self):
        if self.speed > 0:
            if  0 < (2 * math.pi - self.ray * self.i) % (math.pi * 2) < self.ray / 4:
                return True
    
    def leftCollide(self):
        if self.speed < 0:
            if  - self.ray / 4 < (2 * math.pi - self.ray * self.i) % (math.pi * 2) < 0:
                return True
    
    def isCollideDown(self):
        if - self.ray < (math.pi - self.ray * self.i) % (math.pi * 2) < self.ray:
            return True

    def onClick(self):
        self.color = self.app.color

    def render(self,canvas):
        x0 = self.cX - self.r
        y0 = self.cY - self.r
        x1 = self.cX + self.r
        y1 = self.cY + self.r
        canvas.create_arc(x0,y0,x1,y1,start = 90 - self.degree * self.i, width = 0, outline = "", extent = -self.degree,  fill = self.color,
                onClick = self.onClick)

class BaseGeometry(object):
    """organizes the unit gemetries into the drawing template"""
    def __init__(self,app):
        self.app = app
        self.angle = 2 * math.pi / 32
        self.degree = 360 / 32
        self.r = 25
        self.rMax = self.r * 10
        self.rMin = self.r * 3
        self.rList = list(range(self.rMin,self.rMax + 1, self.r))
        self.cX  = self.app.width // 2
        self.cY = self.app.height // 2
        i = 0
        self.arcList = []
        # self.yList = []
        for r in self.rList[::-1]:
            for i in range(33):
                self.arcList.append(Arc(self.app,r,i))
        # self.d = dict()
        # for arc in self.arcList:
        #     self.yList.append(arc.y)
        #     self.d[arc.y] = arc

    def render(self,canvas):
        for arc in self.arcList:
            arc.render(canvas)
        if self.app.outline == True:
            for r in self.rList[::-1]:
                x0 = self.cX - r
                y0 = self.cY - r
                x1 = self.cX + r
                y1 = self.cY + r
                canvas.create_oval(x0,y0,x1,y1,outline = "grey")
                for i in range(33):
                    x2 = self.cX + r * math.sin(i * self.angle)
                    y2 = self.cX - r * math.cos(i * self.angle)
                    canvas.create_line(x2,y2,self.cX,self.cY,width = 1,fill = "grey")
            x0 = self.cX - self.rMin
            y0 = self.cY - self.rMin
            x1 = self.cX + self.rMin
            y1 = self.cY + self.rMin
            canvas.create_oval(x0,y0,x1,y1,fill = "white", outline = "grey")
MapGenerator(width = 900, height = 900)
