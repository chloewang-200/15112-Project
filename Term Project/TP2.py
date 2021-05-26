import math
from math import sqrt
import random
from cmu_112_graphics import * # from cmu 112 Diderot page
import basic_graphics # from cmu 112 Diderot page
import time
import copy
import tkinter as tk
import numpy as np
import time
import random
import copy

# 1.eraser icon from flaticon.com:
#   Icons made by <a href="https://www.flaticon.com/authors/kiranshastry" 
#   title="Kiranshastry">Kiranshastry</a> from <a href="https://www.flaticon.com/" 
#   title="Flaticon"> www.flaticon.com</a>

# 2.map generation and pathfinding algorithms inspired by <maze for programmers>
#   by Jamis Buck ISBN-13: 978-1-68050-055-4, Book version: P1.0—July 2015
#       - chapter 3 - Finding Solutions
#       - chapter 5 - Adding Constraints to Random Walks
#       - chapter 7 - Going in Circles 

# 3.cmu_112_graphics and basic_graphics modules:
#    credit: Carnegie Mellon University 15-112 course materials

def distance(x0,y0,x1,y1):
    return sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

class Arc(object):
    """draws the unit geomtry"""
    def __init__(self,app,r,i):
        self.app = app
        self.r = r
        self.degree = 360 / 32
        self.ray = 2 * math.pi / 32
        self.i = i
        self.speed = 0.1
        self.cX  = self.app.width // 2
        self.cY = self.app.height // 2
        self.color = self.app.color
        self.angle = (2 * math.pi - self.ray * self.i) % (2 * math.pi)
        self.point1 = self.cY - self.r * math.sin(self.angle - self.ray)
        self.point2 = self.cY - self.r * math.sin(self.angle)
        self.y = min(self.point1,self.point2)
        if self.r ** 2 - self.y ** 2 < 0:
            self.x = sqrt(-(self.r ** 2 - self.y ** 2))
        else:
            self.x = sqrt((self.r ** 2 - self.y ** 2))
    
    def rotate(self):
        self.i -= self.speed
    
    def xValue(self):
        x = 450 + self.r * math.cos(- 1.5 * math.pi + self.angle - self.ray)
        return x
    
    def yValue(self):
        y = 450 - self.r * math.sin(-1.5 * math.pi + self.angle - self.ray)
        return y

    def isCollideDown(self):
        if - self.ray < (2 * math.pi - self.ray * self.i) % (math.pi * 2) < self.ray:
            return True
    
    def isCollideUp(self):
        if - self.ray < (2 * math.pi - self.ray * self.i) % (math.pi * 2) < self.ray:
            return True

    def changeDirectionRight(self):
        self.speed = -0.1

    def changeDirectionLeft(self):
        self.speed = 0.1

    def rightCollide(self):
        if self.speed > 0:
            if 0 < (2 * math.pi - self.ray * self.i) % (math.pi * 2) < self.ray:
                return True
        return False
    
    def leftCollide(self):
        if self.speed < 0:
            if 2 * math.pi - self.ray * 1.2 < self.ray * self.i % (math.pi * 2) < 2 * math.pi - self.ray /2:
                return True
        return False

    def onClick(self):
        self.color = self.app.color

    def render(self,canvas):
        self.cX = 450
        self.cY = 450
        x0 = self.cX - self.r
        y0 = self.cY - self.r
        x1 = self.cX + self.r
        y1 = self.cY + self.r
        canvas.create_arc(x0,y0,x1,y1,start = 90 - self.degree * self.i, width = 0, outline = "", extent = -self.degree,  fill = self.color,
                onClick = self.onClick)


class BaseGeometry(object):
    """organizes the unit gemetries into the drawing template"""
    def __init__(self,app,row,col):
        self.app = app
        self.col =  col
        self.row =row
        self.angle = 2 * math.pi / self.col
        self.degree = 360 / self.col
        self.r = 25
        self.rMax = self.r * (3 + self.row)
        self.rMin = self.r * 3
        self.rList = list(range(self.rMin + 1,self.rMax + 1, self.r))
        self.cX  = 450
        self.cY = 450
        self.arcList = []
        for r in self.rList[::-1]:
            for i in range(self.col):
                self.arcList.append(Arc(self.app,r,i))

    def render(self,canvas):
        self.cX = 450
        self.cY = 450
        for arc in self.arcList:
            arc.render(canvas)
        if self.app.outline == True:
            for r in self.rList[::-1]:
                x0 = self.cX - r
                y0 = self.cY - r
                x1 = self.cX + r
                y1 = self.cY + r
                canvas.create_oval(x0,y0,x1,y1,outline = "grey")
                for i in range(self.col):
                    x2 = self.cX + r * math.sin(i * self.angle)
                    y2 = self.cX - r * math.cos(i * self.angle)
                    canvas.create_line(x2,y2,self.cX,self.cY,width = 1,fill = "grey")
            x0 = self.cX - self.rMin
            y0 = self.cY - self.rMin
            x1 = self.cX + self.rMin
            y1 = self.cY + self.rMin
            canvas.create_oval(x0,y0,x1,y1,fill = "white", outline = "grey")
                
class PaintBucket(object):
    """paint bucket tool that fill the template with colors"""
    def __init__(self,app):
        self.app = app
        self.r = 10
        self.eraser = self.app.eraser
    
    # map the clicked color bucket to the clicked cell
    def greyClicked(self):
        self.app.color = "light grey"
    
    def yellowClicked(self):
        self.app.color = "yellow"

    def blueClicked(self):
        self.app.color = "light blue"

    def redClicked(self):
        self.app.color = "red"

    def greenClicked(self):
        self.app.color = "light green"
    
    def eraserClicked(self):
        self.app.color = "white"

    def render(self,canvas):
        x = 30
        y2 = 450
        y1 = y2 - 40
        y0 = y1 - 40
        y3 = y2 + 40
        y4 = y3 + 40
        y5 = y4 + 40
        canvas.create_oval(x - self.r, y0 - self.r, x + self.r, y0 + self.r,fill = "light grey",
        onClick = self.greyClicked, width = 0)
        canvas.create_oval(x - self.r,  y1 - self.r, x + self.r, y1 + self.r,fill = "yellow",
        onClick = self.yellowClicked, width = 0)
        canvas.create_oval(x - self.r, y2 - self.r,x + self.r, y2 + self.r,fill = "light blue",
        onClick = self.blueClicked, width = 0)
        canvas.create_oval(x - self.r, y3 - self.r, x + self.r, y3 + self.r,fill = "red",
        onClick = self.redClicked, width = 0)
        canvas.create_oval(x - self.r, y4 - self.r, x + self.r,  y4 + self.r,fill = "light green",
        onClick = self.greenClicked, width = 0)
        canvas.create_oval(x - self.r, y5 - self.r, x + self.r,  y5 + self.r,fill = "white",
        onClick = self.eraserClicked, width = 0)
        canvas.create_image(x - 1,y4 + 40,image = ImageTk.PhotoImage(self.eraser))

class Square(object):
    def __init__(self,app):
        self.app = app
        self.x = 450
        self.y = 15
        self.r = 12
        self.isJump = False
        self.velocity = 3
        self.isFall = False
        self.arcx = -10
        self.arcy = -10
        self.speed = 50
       
    def jump(self):
        """initial jump"""
        self.isJump = True
        self.y -= self.velocity
        self.velocity -= 1
    

        
    def jump2(self):
        """press space to jump"""
        if self.isJump:
            self.y -= self.speed

    def fall(self):
        self.y += 7
    
    def render(self,canvas):
        x0 = self.x - self.r
        y0 = self.y - self.r
        x1 = self.x + self.r
        y1 = self.y + self.r
        canvas.create_rectangle(x0,y0,x1,y1,fill = "black")
    
    def checkCollision(self):
        """check collision with different platforms and colors"""
        for arc in self.app.arcList:
            d = distance(self.x, self.y + self.r, arc.cX, arc.cY)
            # collide with horizontal grey 
            self.arcx = arc.xValue()
            self.arcy = arc.yValue()
            if arc.rightCollide() and (arc.cY - arc.r - 2 < self.y - self.r < arc.cY - arc.r + 2) and self.y < arc.cY:
                if arc.color == "yellow":
                    arc.color = "white"
                    self.app.score += 1
                if arc.color == "light green":
                    arc.color = "white"
                    self.speed = 100
                if arc.color == "light grey":
                    self.app.changeDirectionRight()
            if arc.leftCollide() and (arc.cY - arc.r - 2 < self.y - self.r < arc.cY - arc.r + 2) and self.y < arc.cY:
                if arc.color == "yellow":
                    arc.color = "white"
                    self.app.score += 1
                if arc.color == "light green":
                    arc.color = "white"
                    self.speed = 100
                if arc.color == "light grey":
                    self.app.changeDirectionLeft()
            if arc.isCollideDown() and (arc.r - 12 < d < arc.r + 12) and self.y < arc.cY:
                if arc.color == "light grey":
                    self.y = arc.cY - arc.r - self.r + 2
                    self.isFall = False
                    self.velocity = 2
                    # if arc.r - 30 < distance(self.x, self.y + self.r, arc.cX, arc.cY) < arc.r +35:
                    #     self.app.changeDirection = True
                elif arc.color == "white":
                    self.isFall = True
                    self.fall()
                elif arc.color == "red":
                    self.app.die = True
            

    def checkDie(self):
        """checks if the square is out of the screen"""
        if self.y > self.app.height - 20:
            self.app.die = True
    

class DrawMode(Mode):
    """player can create maps in this mode"""
    def appStarted(self):
        self.color = "white"
        self.draw = False
        self.baseGeometry = BaseGeometry(self,7,32)
        self.eraser = self.loadImage('eraser.png')    # citation at the top
        (w,h) = self.eraser.size
        self.finalW = 20
        self.eraser = self.scaleImage(self.eraser, self.finalW/w)    #rescale the picture
        self.paintBucket = PaintBucket(self)
        self.x = self.width // 2
        self.y = self.height - 100
        self.r = 20
        self.outline = True
        self.app.score = 0
    
    def modeActivated(self):
        self.appStarted()

    def mousePressed(self,event):
        pass

    def onClick(self):
        self.outline = False
        self.draw = True
        self.setActiveMode("gameDraw")
    
    def randomClicked(self):
        self.setActiveMode("mapGenerator")

    def saveClicked(self):
        self.unitArcList = unitArcList(self,self.baseGeometry.arcList,7,32)
        lst = self.unitArcList.colorList(self.baseGeometry.arcList)
        filename = input("Enter Level Name:")
        f = open(f"{filename}.txt","a+")
        for row in range(len(lst)):
            for col in range(len(lst[0])):
                f.write(str(lst[row][col]))

    def redrawAll(self,canvas):
        self.baseGeometry.render(canvas)
        self.paintBucket.render(canvas)
        x0 = self.x - 40
        y0 = self.y - self.r
        x1 = self.x + 40
        y1 = self.y + self.r
        canvas.create_rectangle(x0,y0,x1,y1, fill = "red", onClick = self.onClick)
        canvas.create_text((x1 - 40), (y1 - 20), text = "Play")
        x2 = x1 + 40
        x3 = x2 + 80
        canvas.create_rectangle(x2,y0,x3,y1, fill = "light blue", onClick = self.randomClicked)
        canvas.create_text((x3 - 40), (y1 - 20), text = "Random")
        x4 = x3 + 40
        x5 = x4 + 80
        y3 = self.y + self.r
        canvas.create_rectangle(x4,y0,x5,y1, fill = "orange", onClick = self.saveClicked)
        canvas.create_text((x5 - 40), (y1 - 20), text = "Save")
        

class Enemy(object):
    def __init__(self,app):
        self.app = app
        self.baseGeometry = self.app.baseGeometry
        self.mapList = self.app.unitArcList.colorList(self.app.arcList)
        self.positions = []
        for row in range(7):
            for col in range(32):
                if self.mapList[row][col] == 1:
                    self.positions.append((row,col))
        self.row, self.col = random.choice(self.positions)
        self.r = 12

    def move(self):
        self.squareRow, self.squareCol = self.app.unitArcList.positions()
        if self.col + 4 < self.squareCol:
            if self.mapList[math.floor(self.row)][math.floor(self.col) + 1] == 1:
                self.col += 0.25
            elif self.row < self.squareRow:
                if self.mapList[math.floor(self.row) + 1][math.floor(self.col) + 1] == 1:
                    self.row += 0.25
            elif self.row > self.squareRow:
                if self.mapList[math.floor(self.row) - 1][math.floor(self.col) + 1] == 1:
                    self.row -= 0.25
        elif self.col + 4 > self.squareCol:
            if self.mapList[math.floor(self.row)][math.floor(self.col) - 1] == 1:
                self.col -= 0.25
            elif self.row < self.squareRow:
                if self.mapList[math.floor(self.row) + 1][math.floor(self.col) - 1] == 1:
                    self.row += 0.25
            elif self.row > self.squareRow:
                if self.mapList[math.floor(self.row) - 1][math.floor(self.col) - 1] == 1:
                    self.row -= 0.25
        elif self.col + 4 == self.squareCol and self.row == self.squareRow:
            self.app.die = True
    
    def render(self,canvas):
        for i in range(len(self.baseGeometry.arcList)):
            row = i // 31
            col = i % 31
            if math.floor(self.row) == row + 1 and math.floor(self.col) == col:
                arc = self.baseGeometry.arcList[i]
                x0 = arc.cX - arc.r - 7.5
                y0 = arc.cY - arc.r - 7.5
                x1 = arc.cX + arc.r + 7.5
                y1 = arc.cY + arc.r + 7.5
                canvas.create_arc(x0,y0,x1,y1,style = basic_graphics.ARC,width = 15, start = 90 - arc.degree * arc.i + 2.5, extent = -arc.degree + 5, outline = "red")



class GameMode(Mode):
    """player can play the map in this mode"""
    def appStarted(self):
        self.MapGenerator = self.getMode("mapGenerator")
        self.baseGeometry = self.MapGenerator.baseGeometry
        self.arcList = self.baseGeometry.arcList
        self.arcList2 = self.MapGenerator.arcList
        self.row =17
        self.col = 32
        self.unitArcList = unitArcList(self,self.arcList,self.row,self.col)
        self.square = Square(self)
        self.square.isFall = False
        self.tap = 0
        self.die = False
        self.score = 0
        self.showSolution = False
        self.timerCalls = 0
        self.startRotate = False
        self.currRow, self.currCol = self.unitArcList.positions()
        self.enemyList = []
        self.enemyMove = False
        self.level = 2
        self.powerUp = 0
        self.mapMode = True
        # self.SmartEnemy = SmartEnemy(self)
        # self.enemyList.append(self.SmartEnemy)
        self.path = self.MapGenerator.path
        self.randomList = []
        
    def solutionClicked(self):
        self.showSolution = True

    def modeActivated(self):
        self.appStarted()

    def backClicked(self):
        self.setActiveMode("directory")

    def mousePressed(self,event):
        pass

    def changeDirectionRight(self):
        for arc in self.arcList:
            arc.changeDirectionRight()
        if self.mapMode:
            for arc in self.arcList2:
                arc.changeDirectionRight()
    
    def changeDirectionLeft(self):
        for arc in self.arcList:
            arc.speed = 0.1
        if self.mapMode:
            for arc in self.arcList2:
                arc.speed = 0.1

    def keyPressed(self,event):
        if event.key == "Space":
            self.startRotate = True
            self.enemyMove = True
            if self.tap >= 1:
                self.square.jump2()
                self.tap += 1
            else:
                self.square.jump()
                self.tap += 1
    
    def checkWin(self):
        pass

    def timerFired(self):
        if self.square.speed == 100:
            self.powerUp += 1
            if self.powerUp == 30:
                self.speed = 50
                self.powerUp = 0
        self.timerCalls += 1
        self.square.checkCollision()
        if self.square.isJump == True:
            self.square.jump()
        elif self.square.isFall == True:
            self.square.fall()
        self.square.checkDie()
        if self.die == True:
            self.setActiveMode("gameOver")
        if self.checkWin():
            self.setActiveMode("gameOver")
        if self.startRotate == True:
            for arc in self.arcList:
                arc.rotate()
            if self.mapMode:
                for arc in self.arcList2:
                    arc.rotate()
        if self.enemyMove:
            if self.timerCalls % 30 == 0:
                for enemy in self.enemyList:
                    enemy.move(enemy.row,enemy.col)

    def redrawAll(self,canvas):
        y0 = 10
        y1 = 60
        x2 = 840
        x3 = 890
        canvas.create_oval(x2,y0,x3,y1, fill = "light blue", width = 0, onClick = self.backClicked)
        self.baseGeometry.render(canvas)
        x0 = 450 - 75
        y0 = 450 - 75
        x1 = 450 + 75
        y1 = 450 + 75
        canvas.create_oval(x0,y0,x1,y1,fill = "white",width = 0)
        self.square.render(canvas)
        # self.unitArcList.render(canvas)
        for enemy in self.enemyList:
            enemy.render(canvas)
        if self.mapMode:
            y0 = 800 - 20
            y1 = 800 + 20
            x2 = 780
            x3 = 820
            canvas.create_rectangle(x2,y0,x3,y1, fill = "orange", onClick = self.solutionClicked)
            canvas.create_text((x3 - 20), (y1 - 20), text = "solution")
            for arc in self.arcList2:
                arc.render(canvas)
            x0 = 450 - 50
            y0 = 450 - 50
            x1 = 450 + 50
            y1 = 450 + 50
            canvas.create_oval(x0,y0,x1,y1,fill = "yellow",width = 0)
        if self.showSolution:
            for i in range(len(self.baseGeometry.arcList)):
                row = i // 31
                col = i % 31
                if (col,row) in self.path:
                    self.baseGeometry.arcList[i].color = "orange"
        # self.unitArcList.render(canvas)
        

class GameLevel(GameMode):
    """player can play the levels in this mode"""
    def appStarted(self):
        self.levelMode = self.getMode("levels")
        self.baseGeometry = self.levelMode.baseGeometry
        self.arcList = self.baseGeometry.arcList
        self.square = Square(self)
        self.square.isFall = False
        self.tap = 0
        self.die = False
        self.score = 0
        self.timerCalls = 0
        self.showSolution = False
        self.row = 7
        self.powerUp = 0
        self.col = 32
        self.mapMode = False
        self.unitArcList = unitArcList(self,self.arcList,self.row,self.col)
        self.startRotate = False
        self.currRow, self.currCol = self.unitArcList.positions()
        self.enemyList = []
        self.enemyMove = False
        self.level = 2
        # self.enemyList.append(SmartEnemy(self))
        # if self.level == 1:
        #     self.enemyList.append(Enemy(self))
        # elif self.level == 2:
        #     self.enemyList.append(Enemy(self))
        #     self.enemyList.append(SmartEnemy(self))
        # elif self.level == 3:
        #     self.enemyList.append(Enemy(self))
        #     self.enemyList.append(Enemy(self))
        #     self.enemyList.append(SmartEnemy(self))
    
    def modeActivated(self):
        self.appStarted()

    def checkWin(self):
        for arc in self.arcList:
            if arc.color == "yellow":
                return False
        return True
    
    def timerFired(self):
        if self.square.speed == 100:
            self.powerUp += 1
            if self.powerUp == 3000:
                self.speed = 50
                self.powerUp = 0
        self.timerCalls += 1
        self.square.checkCollision()
        if self.square.isJump == True:
            self.square.jump()
        elif self.square.isFall == True:
            self.square.fall()
        self.square.checkDie()
        if self.die == True:
            self.setActiveMode("gameOverLevel")
        if self.checkWin():
            self.setActiveMode("gameOverLevel")
        if self.startRotate == True:
            for arc in self.arcList:
                arc.rotate()
        if self.enemyMove:
            for enemy in self.enemyList:
                enemy.move()
        

class GameDraw(GameMode):
    """player can play the levels in this mode"""
    def appStarted(self):
        self.drawMode = self.getMode("draw")
        self.baseGeometry = self.drawMode.baseGeometry
        self.arcList = self.baseGeometry.arcList
        self.square = Square(self)
        self.square.isFall = False
        self.tap = 0
        self.die = False
        self.score = 0
        self.timerCalls = 0
        self.row =17
        self.col = 32
        self.unitArcList = unitArcList(self,self.arcList,self.row,self.col)
        self.startRotate = False
        self.currRow, self.currCol = self.unitArcList.positions()
        self.enemyList = []
        self.enemyMove = False
        self.level = 2
        self.mapMode = False
        self.showSolution = False
        self.powerUp = 0

    
    def checkWin(self):
        for arc in self.arcList:
            if arc.color == "yellow":
                return False
        return True    

    def timerFired(self):
        if self.square.speed == 80:
            self.powerUp += 1
            if self.powerUp == 30000:
                self.speed = 36
                self.powerUp = 0
        self.timerCalls += 1
        self.square.checkCollision()
        if self.square.isJump == True:
            self.square.jump()
        elif self.square.isFall == True:
            self.square.fall()
        self.square.checkDie()
        if self.die == True:
            self.setActiveMode("gameOverDraw")
        if self.checkWin():
            self.setActiveMode("gameOverDraw")
        if self.startRotate == True:
            for arc in self.arcList:
                arc.rotate()
        if self.enemyMove:
            for enemy in self.enemyList:
                enemy.move()

class GameOver(Mode):
    """tells the player the number of taps and scores earned"""
    def appStarted(self):
        self.gameMode = self.getMode("game")
        self.tap = self.gameMode.tap

    
    def backClicked(self):
        self.setActiveMode("directory")
    
    def redrawAll(self,canvas):
        canvas.create_text(self.width//2,self.height//2,text = f"taps: {self.tap}", font =80)
        y0 = 10
        y1 = 60
        x2 = 840
        x3 = 890
        canvas.create_oval(x2,y0,x3,y1, fill = "light blue", width = 0, onClick = self.backClicked)

class GameOverDraw(Mode):
    def appStarted(self):
        self.gameMode = self.getMode("gameDraw")
        self.tap = self.gameMode.tap
        self.score = self.gameMode.score
    
    def backClicked(self):
        self.setActiveMode("directory")
    
    def redrawAll(self,canvas):
        canvas.create_text(self.width//2,self.height//2,text = f"taps: {self.tap}", font =80)
        y0 = 10
        y1 = 60
        x2 = 840
        x3 = 890
        canvas.create_oval(x2,y0,x3,y1, fill = "light blue", width = 0, onClick = self.backClicked)

class GameOverLevel(Mode):
    def appStarted(self):
        self.gameMode = self.getMode("gameLevel")
        self.tap = self.gameMode.tap
        self.score = self.gameMode.score
    
    def backClicked(self):
        self.setActiveMode("directory")
    
    def redrawAll(self,canvas):
        canvas.create_text(self.width//2,self.height//2,text = f"taps: {self.tap}", font =80)
        y0 = 10
        y1 = 60
        x2 = 840
        x3 = 890
        canvas.create_oval(x2,y0,x3,y1, fill = "light blue", width = 0, onClick = self.backClicked)

class Levels(Mode):
    """levels page"""
    def appStarted(self):
        self.levelmo = False
        self.level = 2
        self.filename = "Level 01.txt"
        self.lst = [([0] * 32) for i in range(7)]
        self.gameLevel = self.getMode("gameLevel")
        self.color = "white"
        self.outline = False
    
    def modeActivated(self):
        self.appStarted()

    def click1(self):
        self.levelmo = True
        self.level = 1
        f = open("Level 01.txt","r")
        if f.mode == "r":
            contents = f.read()
        for i in range(len(contents)):
            row = i // 32
            col = i % 32
            self.lst[row][col] = int(contents[i])
        self.baseGeometry = BaseGeometry(self,7,32)
        for i in range(len(self.baseGeometry.arcList)):
            row = i // 32
            col = i % 32
            if self.lst[row][col] == 1:
                self.baseGeometry.arcList[i].color = "light grey"
            elif self.lst[row][col] == 2:
                self.baseGeometry.arcList[i].color = "yellow"
            else:
                self.baseGeometry.arcList[i].color = "white"
        self.setActiveMode("gameLevel")
    
    def click2(self):
        self.levelmo = True
        self.level = 2
        f = open("Level 04.txt","r")
        if f.mode == "r":
            contents = f.read()
        for i in range(len(contents)):
            row = i // 32
            col = i % 32
            self.lst[row][col] = int(contents[i])
        self.baseGeometry = BaseGeometry(self,7,32)
        self.x = self.width // 2
        self.y = self.height - 100
        for i in range(len(self.baseGeometry.arcList)):
            row = i // 32
            col = i % 32
            if self.lst[row][col] == 1:
                self.baseGeometry.arcList[i].color = "light grey"
            elif self.lst[row][col] == 2:
                self.baseGeometry.arcList[i].color = "yellow"
        self.setActiveMode("gameLevel")
    
    def click3(self):
        self.levelmo = True
        self.level = 3
        f = open("Level 05.txt","r")
        if f.mode == "r":
            contents = f.read()
        for i in range(len(contents)):
            row = i // 32
            col = i % 32
            self.lst[row][col] = int(contents[i])
        self.baseGeometry = BaseGeometry(self,7,32)
        self.x = self.width // 2
        self.y = self.height - 100
        for i in range(len(self.baseGeometry.arcList)):
            row = i // 32
            col = i % 32
            if self.lst[row][col] == 1:
                self.baseGeometry.arcList[i].color = "light grey"
            elif self.lst[row][col] == 2:
                self.baseGeometry.arcList[i].color = "yellow"
        self.setActiveMode("gameLevel")
    
    def click4(self):
        self.levelmo = True
        self.level = 3
        filename = input("enter file name:")
        f = open(f"{filename}.txt","r")
        if f.mode == "r":
            contents = f.read()
        for i in range(len(contents)):
            row = i // 32
            col = i % 32
            self.lst[row][col] = int(contents[i])
        self.baseGeometry = BaseGeometry(self,7,32)
        self.x = self.width // 2
        self.y = self.height - 100
        for i in range(len(self.baseGeometry.arcList)):
            row = i // 32
            col = i % 32
            if self.lst[row][col] == 1:
                self.baseGeometry.arcList[i].color = "light grey"
            elif self.lst[row][col] == 2:
                self.baseGeometry.arcList[i].color = "yellow"
        self.setActiveMode("gameLevel")
    
    def redrawAll(self,canvas):
        x0 = self.app.width // 3 * 0
        x1 = self.app.width // 3 * 1
        x2 = self.app.width // 3 * 2
        y0 = self.app.height // 3 * 0
        cx1 = x0 + self.app.width // 6
        cx2 = x1 + self.app.width // 6
        cx3 = x2 + self.app.width // 6
        cy = y0 + self.app.height // 6
        cy2 = cy + self.app.height // 3
        r = 60
        canvas.create_oval(cx1 - r, cy-r, cx1 + r, cy + r,fill = "light blue", width = 0,onClick = self.click1)
        canvas.create_oval(cx2 - r, cy-r, cx2 + r, cy + r,fill = "light blue", width = 0, onClick = self.click2)
        canvas.create_oval(cx3 - r, cy-r, cx3 + r, cy + r,fill = "light blue", width = 0,onClick = self.click3)
        canvas.create_oval(cx1 - r, cy2-r, cx1 + r, cy2 + r,fill = "light blue", width = 0,onClick = self.click4)
        for row in range(3):
            for col in range(3):
                x0 = self.app.width // 3 * row
                y0 = self.app.height // 3 * col
                cx = x0 + self.app.width // 6
                cy = y0 + self.app.height // 6
                r = 60
                canvas.create_oval(cx - r, cy-r, cx + r, cy + r,fill = "light blue", width = 0)
                canvas.create_text(cx, cy, text = f"{col * 3 + row + 1}")

class Directory(Mode):
    def appStarted(self):
        self.cX = self.width // 2
        self.cY = self.height
        self.r = 350
        self.title = self.loadImage("title.png")
        (w,h) = self.title.size
        self.finalW = 700
        self.title = self.scaleImage(self.title, self.finalW/w)
        self.drawMode = self.getMode("draw")

    def puzzleClick(self):
        self.setActiveMode("rectangularMap")

    def createClick(self):
        self.drawMode.drawmode = True
        self.setActiveMode("draw")
    
    def enemyClick(self):
        self.setActiveMode("levels")

    def redrawAll(self,canvas):
        canvas.create_rectangle(0,0,900,900,fill = "black")
        x0 = self.cX - self.r
        y0 = self.cY - self.r
        x1 = self.cX + self.r
        y1 = self.cY + self.r
        color = ["orange","blue","green"]
        canvas.create_arc(x0,y0,x1,y1,start = 55 * 0 + 0 * 10, width = 0, outline = "", extent = 55,  fill = "orange",
                    onClick = self.puzzleClick)
        canvas.create_arc(x0,y0,x1,y1,start = 55 * 1 + 1 * 10, width = 0, outline = "", extent = 55,  fill = "blue",
                    onClick = self.enemyClick)
        canvas.create_arc(x0,y0,x1,y1,start = 55 * 2 + 2 * 10, width = 0, outline = "", extent = 55,  fill = "green",
                    onClick = self.createClick)
        canvas.create_oval(x0 + 100,y0 + 100,x1 - 100,y1 - 100,fill = "black",width = 0)
        canvas.create_image(450,300,image = ImageTk.PhotoImage(self.title))

class unitArcList(object):
    """turn drawing into 2d List"""
    def __init__(self,app,lst,row,col):
        self.row = row
        self.col = col
        self.app = app
        self.unitList = [([0]* self.col) for i in range(self.row)]
        # self.arcList = self.app.arcList # r first and then angle
        self.arcList = lst
        for i in range(len(self.arcList)):
            row = i // 32
            col = i % 32
            if self.arcList[i].color == "light grey":
                self.unitList[row][col] = 1
            elif self.arcList[i].color == "yellow":
                self.unitList[row][col] = 2
    
    def colorList(self,lst):
        self.unitList = [([0]* self.col) for i in range(self.row)]
        for i in range(len(self.arcList)):
            row = i // 32
            col = i % 32
            if self.arcList[i].color == "light grey":
                self.unitList[row][col] = 1
            elif self.arcList[i].color == "yellow":
                self.unitList[row][col] = 2
        return self.unitList

    def positions(self):
        """return current positions of the square"""
        if self.app.square.y <= self.app.height / 2 - 37.5:
            self.currRow = (self.app.square.y - 112.5  + self.app.square.r) // 25 + 4
            for i in range(len(self.arcList)):
                row = i // 32
                col = i % 32
                if self.arcList[i].isCollideUp():
                    self.currCol = col
        return ((self.currRow, self.currCol))
    
    def render(self,canvas):
        for row in range(len(self.unitList)):
            i = 0
            for col in range(len(self.unitList[0])):
                x0 = 30 + 20 * col
                y0 = 750 + 10 * row
                x1 = x0 + 20
                y1 = y0 + 10
                n = row * 32 + col
                canvas.create_rectangle(x0,y0,x1,y1,fill = self.arcList[n].color)
                if (row,col) == self.positions():
                    canvas.create_rectangle(x0,y0,x1,y1,fill = "blue")

# inspiratoin source at the top
class CellColor(object):
    uncolored = 0
    colored = 1

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[0 for x in range(self.width)] for y in range(self.height)]

    def resetMaze(self, value):
        for y in range(self.height):
            for x in range(self.width):
                self.setMaze(x, y, value)

    def setMaze(self, x, y, value):
        if value == CellColor.uncolored:
            self.maze[y][x] = CellColor.uncolored
        else:
            self.maze[y][x] = CellColor.colored

    def visited(self, x, y):
        return self.maze[y][x] != 1

def checkNeighbors(maze, x, y, width, height, checklist):
    directions = []
    if x > 0:
        if not maze.visited(2 * (x - 1) + 1, 2 * y + 1):
            directions.append(0)
    if y > 0:
        if not maze.visited(2 * x + 1, 2 * (y - 1) + 1):
            directions.append(1)
    if x < width - 1:
        if not maze.visited(2 * (x + 1) + 1, 2 * y + 1):
            directions.append(2)
    if y < height - 1:
        if not maze.visited(2 * x + 1, 2 * (y + 1) + 1):
            directions.append(3)
    if len(directions):
        direction = random.choice(directions)
        if direction == 0: # check left
            maze.setMaze(2 * (x - 1) + 1, 2 * y + 1, CellColor.uncolored)
            maze.setMaze(2 * x, 2 * y + 1, CellColor.uncolored)
            checklist.append((x - 1, y))
        elif direction == 1: # check up
            maze.setMaze(2 * x + 1, 2 * (y - 1) + 1, CellColor.uncolored)
            maze.setMaze(2 * x + 1, 2 * y, CellColor.uncolored)
            checklist.append((x, y - 1))
        elif direction == 2: # check right
            maze.setMaze(2 * (x + 1) + 1, 2 * y + 1, CellColor.uncolored)
            maze.setMaze(2 * x + 2, 2 * y + 1, CellColor.uncolored)
            checklist.append((x + 1, y))
        elif direction == 3: # check below
            maze.setMaze(2 * x + 1, 2 * (y + 1) + 1, CellColor.uncolored)
            maze.setMaze(2 * x + 1, 2 * y + 2, CellColor.uncolored)
            checklist.append((x, y + 1))
        return True
    return False

def randomPrime(map, width, height):
    start_x, start_y = (random.randint(0, width - 1), random.randint(0, height - 1))
    map.setMaze(2 * start_x + 1, 2 * start_y + 1, CellColor.uncolored)
    checklist = [(start_x, start_y)]
    while len(checklist):
        entry = random.choice(checklist)
        if not checkNeighbors(map, entry[0], entry[1], width, height, checklist):
            checklist.remove(entry)

def do_random_prime(map):
    map.resetMaze(CellColor.colored)
    randomPrime(map, (map.width - 1) // 2, (map.height - 1) // 2)

def set_entrance_exit(maze):
    entrance = []
    for i in range(maze.height):
        if maze.maze[i][1] == 0:
            maze.setMaze(0, i, 0)
            entrance = [0, i]
            break
    exitxy = []
    for i in range(maze.height - 1, 0, -1):
        if maze.maze[i][maze.width - 2] == 0:
            maze.setMaze(maze.width - 1, i, 0)
            exitxy = [maze.width - 1, i]
            break
    return entrance, exitxy

def generate_maze(width=17, height=33):
    maze = Maze(width, height)
    do_random_prime(maze)
    entrance, exitxy = set_entrance_exit(maze)
    return maze.maze

def exitPosition(width=17, height=35):
    maze = Maze(width, height)
    do_random_prime(maze)
    entrance, exitxy = set_entrance_exit(maze)
    return exitxy

class solveMaze(object):
    def __init__(self):
        self.path=[]            

    def mark(self,maze,pos):  
        maze[pos[0]][pos[1]]=2
    
    def passable(self,maze,pos): 
        return maze[pos[0]][pos[1]]==0
    
    def find_path(self,maze,pos,end):
        dirs=[(0,1),(1,0),(0,-1),(-1,0)]
        self.mark(maze,pos)
        if pos==end:
            self.path.append(pos)
            return True
        for i in range(4):   
            nextp=pos[0]+dirs[i][0],pos[1]+dirs[i][1]
            if self.passable(maze,nextp):     
                if self.find_path(maze,nextp,end):
                    self.path.append(pos)
                    return True
        return False
    
    def get_path(self):
        return self.path

 
class MapGenerator(Mode): 
    """turn 2d list into drawings"""
    def appStarted(self): 
        self.lst = generate_maze(14,32)
        self.mapList = copy.deepcopy(self.lst)
        self.start= (1,1)
        self.exit=(29,11)
        self.color = "white"
        self.baseGeometry = BaseGeometry(self,13,31)
        self.outline = False
        for i in range(len(self.baseGeometry.arcList)):
            row = i // 31
            col = i % 31
            if self.lst[col][row] == 1:
                self.baseGeometry.arcList[i].color = "light grey"
        self.solution = solveMaze()
        self.solution.find_path(self.lst,self.start,self.exit)
        self.path = self.solution.get_path()
        self.arcList = []
        for i in range(32):
            if i != 29:
                self.arcList.append(Arc(self,75,i))

    def randomClick(self):
        self.appStarted()
    
    def startGameClick(self):
        self.gameMode = self.getMode("game")
        self.mapmode = True
        self.setActiveMode("game")

    def redrawAll(self,canvas):
        self.cX = 450
        self.cY = 450
        self.x  = 450
        self.y = 800
        self.r = 20
        x0 = 700
        y0 = self.y - self.r
        x1 = 740
        y1 = self.y + self.r
        x2 = x1 + 80
        x3 = x2 + 40
        x4 = x3 + 80
        x5 = x4 + 40
        canvas.create_rectangle(x0,y0,x1,y1, fill = "red", onClick = self.randomClick)
        canvas.create_text((x1 - 20), (y1 - 20), text = "redraw")
        canvas.create_rectangle(x2,y0,x3,y1, fill = "orange", onClick = self.startGameClick)
        canvas.create_text((x3 - 20), (y1 - 20), text = "play")
        x0 = self.cX - 75
        y0 = self.cY - 75
        x1 = self.cX + 75
        y1 = self.cY + 75
        for arc in self.baseGeometry.arcList:
            if arc.i == 30:
                arc.color = "yellow"
        self.baseGeometry.render(canvas)
        canvas.create_oval(x0,y0,x1,y1,fill = "white",width = 0)
        for arc in self.arcList:
            arc.color = "light grey"
            arc.render(canvas)
        x0 = self.cX - 50
        y0 = self.cY - 50
        x1 = self.cX + 50
        y1 = self.cY + 50
        canvas.create_oval(x0,y0,x1,y1,fill = "yellow",width = 0)


class solveMaze(object):
    def __init__(self):
        self.path=[]            
 
    def mark(self,maze,pos):  
        maze[pos[0]][pos[1]]=2
    
    def passable(self,maze,pos): 
        return maze[pos[0]][pos[1]]==0
    
    def find_path(self,maze,pos,end):
        dirs=[(0,1),(1,0),(0,-1),(-1,0)]
        self.mark(maze,pos)
        if pos==end:
            print(pos,end=" ")
            self.path.append(pos)
            return True
        for i in range(4):  
            nextp=pos[0]+dirs[i][0],pos[1]+dirs[i][1]
            if self.passable(maze,nextp):      
                if self.find_path(maze,nextp,end):
                    print(pos,end=" ")
                    self.path.append(pos)
                    return True
        return False
    
    def get_path(self):
        return self.path

    def see_path(self,maze,path):     
        for i,p in enumerate(self.path):
            if i==0:
                maze[p[0]][p[1]] ="E"
            elif i==len(path)-1:
                maze[p[0]][p[1]]="S"
            else:
                maze[p[0]][p[1]] =3
        print("\n")
        for r in maze:
            for c in r:
                if c==3:
                    print('\033[0;31m'+"*"+" "+'\033[0m',end="")
                elif c=="S" or c=="E":
                    print('\033[0;34m'+c+" " + '\033[0m', end="")
                elif c==2:
                    print('\033[0;32m'+"#"+" "+'\033[0m',end="")
                elif c==1:
                    print('\033[0;;40m'+" "*2+'\033[0m',end="")
                else:
                    print(" "*2,end="")
            print()


# algorithmic concepts and ideas from <mazes for programmers>  see top
class MazeGenerate(object):
	def __init__(self, width, height,start,destination):
		self.width = (width // 2) * 2 + 1 # odd if not odd
		self.height = (height // 2) * 2 + 1
		self.start = start
		self.destination = destination
		self.lst = []
		self.path = []

	def resizeList(self, width, height, mode, newList):
		self.path = []
		self.width = (width // 2) * 2 + 1
		self.height = (height // 2) * 2 + 1
		self.start = self.start
		self.destination = [self.height - 2, self.width - 1]
		self.generateList(mode, newList)

	def generateMazeDfs(self):
		self.matrix = -np.ones((self.height, self.width))
		self.matrix[self.start[0], self.start[1]] = 0
		self.matrix[self.destination[0], self.destination[1]] = 0
		visit_flag = [[0 for i in range(self.width)] for j in range(self.height)]
		def check(row, col, row2, col2):
			temp_sum = 0
			for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
				temp_sum += self.matrix[row2 + d[0]][col2 + d[1]]
			return temp_sum <= -3
		def dfs(row, col):
			visit_flag[row][col] = 1
			self.matrix[row][col] = 0
			if row == self.start[0] and col == self.start[1] + 1:
				return
			directions = [[0, 2], [0, -2], [2, 0], [-2, 0]]
			random.shuffle(directions)
			for d in directions:
				row2, col2 = row + d[0], col + d[1]
				if row2 > 0 and row2 < self.height - 1 and col2 > 0 and col2 < self.width - 1 and visit_flag[row2][col2] == 0 and check(row, col, row2, col2):
					if row == row2:
						visit_flag[row][min(col, col2) + 1] = 1
						self.matrix[row][min(col, col2) + 1] = 0
					else:
						visit_flag[min(row, row2) + 1][col] = 1
						self.matrix[min(row, row2) + 1][col] = 0
					dfs(row2, col2)
		dfs(self.destination[0], self.destination[1] - 1)
		self.matrix[self.start[0], self.start[1] + 1] = 0


	def generateMazePrim(self):
		self.matrix = -np.ones((self.height, self.width))
		def check(row, col):
			temp_sum = 0
			for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
				temp_sum += self.matrix[row + d[0]][col + d[1]]
			return temp_sum < -3
		queue = []
		row, col = (np.random.randint(1, self.height - 1) // 2) * 2 + 1, (np.random.randint(1, self.width - 1) // 2) * 2 + 1
		queue.append((row, col, -1, -1))
		while len(queue) != 0:
			row, col, r2, c2 = queue.pop(np.random.randint(0, len(queue)))
			if check(row, col):
				self.matrix[row, col] = 0
				if r2 != -1 and row == r2:
					self.matrix[row][min(col, c2) + 1] = 0
				elif r2!= -1 and col == c2:
					self.matrix[min(row, r2) + 1][col] = 0
				for d in [[0, 2], [0, -2], [2, 0], [-2, 0]]:
					row2, col2 = row + d[0], col + d[1]
					if row2 > 0 and row2 < self.height - 1 and col2 > 0 and col2 < self.width - 1 and self.matrix[row2][col2] == -1:
						queue.append((row2, col2, row, col))
		self.matrix[self.start[0], self.start[1]] = 0
		self.matrix[self.destination[0], self.destination[1]] = 0

	def findPath(self, destination):
		visited = [[0 for i in range(self.width)] for j in range(self.height)]
		def dfs(path):
			visited[path[-1][0]][path[-1][1]] = 1
			if path[-1][0] == destination[0] and path[-1][1] == destination[1]:
				self.path = path[:]
				return
			for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
				row, col = path[-1][0] + d[0], path[-1][1] + d[1]
				if row > 0 and row < self.height - 1 and col > 0 and col < self.width and visited[row][col] == 0 and self.matrix[row][col] == 0:
					dfs(path + [[row, col]])

if __name__ == '__main__':
	maze = MazeGenerate(20, 20,(1,1),(20,20))

class MapRectangularGameOver(Mode):
    def appStarted(self):
        pass
    
    def redrawAll(self,canvas):
        canvas.create_rectangle(0,0,900,900,fill = "white")

class moveEnemy(object):
    def __init__(self,app):
        self.app = app
        self.row = random.randint(0,29)
        self.col = random.randint(0,29)
        while self.app.map[self.row][self.col] !=  0:
            self.row = random.randint(0,29)
            self.col = random.randint(0,29)
        self.visited = []
    
    def moveToward(self):
        self.targetRow = self.app.moveSquare.row
        self.targetCol = self.app.moveSquare.col
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        if self.row == self.targetRow and self.col  == self.targetCol:
            self.app.die = True
            print("die")
            return
        if self.row < self.targetRow and self.app.map[self.row + 1][self.col] == 0:
            self.row += 1
        elif self.row > self.targetRow and self.app.map[self.row - 1][self.col] == 0:
            self.row -= 1
        elif self.row < self.targetCol and self.app.map[self.row][self.col + 1] == 0:
            self.col += 1
        elif self.row > self.targetCol and self.app.map[self.row][self.col - 1] == 0:
            self.row -= 1
        elif self.row == self.targetRow:
            if self.app.map[self.row][self.col + 1] == 0:
                self.col += 1
            elif self.app.map[self.row][self.col - 1] == 0:
                self.col -= 1
        elif self.col == self.targetCol:
            if self.app.map[self.row + 1][self.col] == 0:
                self.row += 1
            elif self.app.map[self.row - 1][self.col] == 0:
                self.row -= 1
        else:
            dx,dy = random.choice([(0,1),(0,-1),(1,0),(1,-1)])
            while self.app.map[self.row + dx][self.col + dy] != 0:
                dx,dy = random.choice([(0,1),(0,-1),(1,0),(1,-1)])
            if self.app.map[self.row + dx][self.col + dy] != 0:
                self.row += dx
                self.col += dy
            
        
            # self.row,self.col = random.choice([(self.row + 1,self.col),(self.row - 1,self.col),(self.row,self.col+1),(self.row, self.col - 1)]
            # while self.app.map[self.row][self.col] != 0:
            #     self.row,self.col = random.choice([(self.row + 1,self.col),(self.row - 1,self.col),(self.row,self.col+1),(self.row, self.col - 1)]
    
    def render(self,canvas):
        x0 = self.col * 28
        y0 = self.row * 28
        x1 = x0 + 28
        y1 = y0 + 28
        canvas.create_rectangle(x0,y0,x1,y1,fill = "red")

class SmartEnemy(moveEnemy):
    def __init__(self,app):
        self.app = app
        self.row = random.randint(0,29)
        self.col = random.randint(0,29)
        while self.app.map[self.row][self.col] !=  0:
            self.row = random.randint(0,29)
            self.col = random.randint(0,29)
        self.visited = []
        self.targetRow = self.app.moveSquare.row
        self.targetCol = self.app.moveSquare.col
        self.path = []
    
    def findPath(self,destination):
        if self.app.timerCalls % 50 == 0:
            self.targetRow,self.targetCol = self.target()
            destination = self.target()
        visited = [[0 for i in range(30)] for j in range(39)]
        def dfs(path):
            visited[path[-1][0]][path[-1][1]] = 1
            if path[-1][0] == destination[0] and path[-1][1] == destination[1]:
                self.path = path[:]
                return
            for d in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
                row, col = path[-1][0] + d[0], path[-1][1] + d[1]
                if row > 0 and row < 30 - 1 and col > 0 and col < 30 and visited[row][col] == 0 and self.app.map[row][col] == 0:
                    dfs(path + [[row, col]])

    def target(self):
        return self.app.moveSquare.row,self.app.moveSquare.col

    def move(self):
        print(self.path)
        if self.path != []:
            self.row,self.col = self.path[-2]

class moveSquare(object):
    def __init__(self,app):
        self.row, self.col = (1,1)
        self.app = app

class MapRectangularGenerator(Mode):
    def appStarted(self):
        self.maze = MazeGenerate(30,30,(1,1),(29,29))
        self.maze.generateMazeDfs()
        self.lst = self.maze.matrix
        self.color = "white"
        self.die = False
        self.maze.findPath(maze.destination)
        self.outline = False
        self.moveSquare = moveSquare(self)
        self.path = self.maze.path
        self.map = copy.deepcopy(self.lst)
        self.start= (1,1)
        self.exit=(29,29)
        self.moveEnemy = moveEnemy(self)
        self.smartEnemy = SmartEnemy(self)
        self.color = "white"
        self.solution = []
        self.timerCalls = 0
    
    def modeActivated(self):
        self.appStarted()

    def keyPressed(self,event):
        row = self.moveSquare.row 
        col = self.moveSquare.col 
        if event.key  ==  "Left":
            if self.map[row][col - 1] ==  0:
                self.moveSquare.col -= 1
        if event.key  ==  "Up":
            if self.map[row - 1][col] ==  0:
                self.moveSquare.row -= 1
        if event.key  ==  "Right":
            if self.map[row][col + 1] ==  0:
                self.moveSquare.col += 1
        if event.key  ==  "Down":
            if self.map[row + 1][col] ==  0:
                self.moveSquare.row  += 1
        if self.moveSquare.row == 29 and self.moveSquare.col == 29:
            self.setActiveMode("rectangleGameOver")
        if event.key ==  "1":
            self.setActiveMode("rectangularMap")
        if event.key ==  "2":
                self.setActiveMode("rectangularMap2")
        if event.key ==  "3":
                self.setActiveMode("directory")
    
    def timerFired(self):
        self.moveEnemy.moveToward()
        self.smartEnemy.move()
        self.smartEnemy.findPath((self.moveSquare.row,self.moveSquare.col))
        self.timerCalls += 1
        if self.die == True:
            self.setActiveMode("rectangleGameOver")

    def mousePressed(self,event):
        row = event.y // 28
        col = event.x // 28
        self.findSolution(row,col)
    
    def findSolution(self,row,col):
        self.maze.findPath((row,col))
        self.solution = self.maze.path

    def redrawAll(self,canvas):
        for row in range(len(self.map)):
                for col in range(len(self.map[0])):
                    x0 = col * 28
                    y0 = row * 28
                    x1 = x0 + 28
                    y1 = y0 + 28
                    if self.moveSquare.col == col and self.moveSquare.row == row:
                        color = "yellow"
                    elif self.map[row][col] == -1:
                        color = "black"
                    elif row == 29 and col == 29:
                        color =  "red"
                    else:
                        color = "white"
                    canvas.create_rectangle(x0,y0,x1,y1,fill = color)
        self.moveEnemy.render(canvas)


class MapRectangularGenerator2(MapRectangularGenerator):
    def appStarted(self):
        self.maze = MazeGenerate(30,30,(1,1),(29,29))
        self.maze.generateMazePrim()
        self.lst = self.maze.matrix
        self.color = "white"
        self.maze.findPath(maze.destination)
        self.outline = False
        self.moveSquare = moveSquare(self)
        self.path = self.maze.path
        self.map = copy.deepcopy(self.lst)
        self.start= (1,1)
        self.exit=(29,29)
        self.color = "white"
        self.solution = []
    
    
        
class runApp(ModalApp):
    def appStarted(self):
        self.addMode(DrawMode(name = "draw"))
        self.addMode(GameMode(name = "game"))
        self.addMode(GameOver(name = "gameOver"))
        self.addMode(MapGenerator(name = "mapGenerator"))
        self.addMode(Levels(name = "levels"))
        self.addMode(Directory(name = "directory"))
        self.addMode(GameLevel(name = "gameLevel"))
        self.addMode(GameDraw(name = "gameDraw"))
        self.addMode(GameOverDraw(name = "gameOverDraw"))
        self.addMode(GameOverLevel(name = "gameOverLevel"))
        self.addMode(MapRectangularGenerator(name = "rectangularMap"))
        self.addMode(MapRectangularGameOver(name = "rectangleGameOver"))
        self.addMode(MapRectangularGenerator2(name = "rectangularMap2"))
        self.setActiveMode("directory")
        

runApp(width = 900,height = 900)





