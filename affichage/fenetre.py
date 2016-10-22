from affichage.graphics import *


class Fenetre:
    offset = 0
    def __init__(self,largeur,hauteur,ratio,offset):
        self.offset = offset
        self.largeur = self.offset + float(largeur) + self.offset
        self.hauteur = self.offset + float(hauteur) + self.offset
        self.ratio = float(ratio)
        self.win = GraphWin('Carte', int(self.largeur*self.ratio), int(self.hauteur*self.ratio)) # give title and dimensions
        self.win.setBackground('white')

    def drawCircle(self,nom,x,y,rayon,color):
        x +=  self.offset
        y +=  self.offset
        circle = Circle(Point(x*self.ratio,y*self.ratio), rayon*self.ratio) # set center and radius
        circle.setFill(color)
        circle.draw(self.win)
        if len(nom) > 1:
            taille=rayon*2/len(nom)*self.ratio
            if taille < 5:taille=5
            if taille > 36:taille=36
            titre = Text(Point((x-len(nom)/taille)*self.ratio,y*self.ratio), nom)
            titre.setSize(int(taille))
            titre.draw(self.win)

    def drawRectangle(self,nom,x1,y1,x2,y2,color):
        x1 +=  self.offset
        y1 +=  self.offset
        x2 +=  self.offset
        y2 +=  self.offset
        rect = Rectangle(Point(x1*self.ratio, y1*self.ratio),Point(x2*self.ratio, y2*self.ratio))
        rect.setFill(color)
        rect.draw(self.win)
        if len(nom) > 1:
            taille=(x2*self.ratio-x1*self.ratio)*2/len(nom)
            if taille < 5:taille=5
            if taille > 36:taille=36
            titre = Text(Point((x1*self.ratio+(x2*self.ratio-x1*self.ratio)/2)-len(nom)/taille,y1*self.ratio+(y2*self.ratio-y1*self.ratio)/2), nom)
            titre.setSize(int(taille))
            titre.draw(self.win)

    def drawLine(self,nom,x1,y1,x2,y2,color):
        x1 +=  self.offset
        y1 +=  self.offset
        x2 +=  self.offset
        y2 +=  self.offset
        line = Line(Point(x1*self.ratio, y1*self.ratio),Point(x2*self.ratio, y2*self.ratio))
        line.setOutline(color)
        line.draw(self.win)
        if len(nom) > 1:
            taille=(x2*self.ratio-x1*self.ratio)*2/len(nom)
            if taille < 5:taille=5
            if taille > 36:taille=36
            titre = Text(Point((x1*self.ratio+(x2*self.ratio-x1*self.ratio)/2)-len(nom)/taille,y1*self.ratio+(y2*self.ratio-y1*self.ratio)/2), nom)
            titre.setSize(int(taille))
            titre.draw(self.win)

    def drawPoly(self, nom, points, color):
        pointList = []
        center = {"x": 0.0, "y": 0.0}
        maxX=0
        minX=self.largeur
        for point in points:
            x = (self.offset + float(point["x"]))*self.ratio
            y = (self.offset + float(point["y"]))*self.ratio
            pointList.append(Point(x, y))
            center["x"] += x
            center["y"] += y
            if maxX < x :
                maxX = x
            if minX > x :
                minX = x
        center["x"] /= float(len(pointList))
        center["y"] /= float(len(pointList))
        poly = Polygon(pointList)
        poly.setFill(color)
        poly.draw(self.win)
        if len(nom) > 1:
            taille=((maxX - minX)*self.ratio)*2/len(nom)
            if taille < 5:taille=5
            if taille > 36:taille=36
            titre = Text(Point((center["x"]-len(nom)/taille)*self.ratio, center["y"]*self.ratio), nom)
            titre.setSize(int(taille))
            titre.draw(self.win)

    def drawImage(self, path):
        fond = Image(Point((self.largeur/2)*self.ratio, (self.hauteur/2)*self.ratio), path)
        #fond.setWidth(self.largeur*self.ratio)
        fond.draw(self.win)


    """

    mouth = Oval(Point(30, 90), Point(50, 85)) # set corners of bounding box
    mouth.setFill("red")
    mouth.draw(win)

    
    self.win.getMouse()
    self.win.close()"""
