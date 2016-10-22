import math

from cartographie.forme import *
from math import atan2, degrees, pi

#from rectangle import Rectangle
#from cercle import Cercle

class Ligne(Forme):
    def __init__(self, nom, x1=0, y1=0, x2=0, y2=0, couleur="black"):
        self.nom = nom
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x = (x1+x2)/2
        self.y = (y1+y2)/2
        self.couleur = couleur

    def setCouleur(self, newCouleur):
        self.couleur = newCouleur

    def dessiner(self, fenetre):
        fenetre.drawLine(self.nom, self.x1, self.y1, self.x2, self.y2, self.couleur)

    def getlongeur(self):
        x=max(self.x1,self.x2)-min(self.x1,self.x2)
        y=max(self.y1,self.y2)-min(self.y1,self.y2)
        return math.sqrt(math.pow(x,2)+math.pow(y,2))

    def getAngle(self):
        angle = 0.
        x1=self.x1
        y1=self.y1
        x2=self.x2
        y2=self.y2
        dx = x2 - x1
        dy = y2 - y1
        rads = atan2(dy,dx)
        rads += pi/2
        rads %= 2*pi
        degs = degrees(rads)
        degs -= 90
        if degs > 180:
            degs = -360 + degs
        if degs < -180:
            degs = 360 + degs
        #if(x1>x2):
        #   degs *= -1
        return degs
        """
        if   x1<x2 and y1<y2:
            angle = math.atan((y2-y1)/(x2-x1))
        elif x1<x2 and y1>y2:
            angle = math.atan((y1-y2)/(x2-x1))
        elif x1>x2 and y1>y2:
            angle = math.pi - math.atan((y1-y2)/(x1-x2))
        elif x1>x2 and y1<y2:
            angle = -math.pi + math.atan((y2-y1)/(x1-x2))
        elif x1==x2 and y1<y2:
            angle = -math.pi/2
        elif x1==x2 and y1>y1:
            angle = math.pi/2
        elif x1<x2 and y1==y2:
            angle = 0
        elif x1>x2 and y1==y2:
            angle = math.pi

        return angle/-0.0174532925"""

    def rotate(self,angle=0):
        radangle=angle*0.0174532925 #degree vers radian
        longeur=self.getlongeur()
        self.x2=self.x1 + longeur*math.cos(radangle)
        self.y2=self.y1 + longeur*math.sin(radangle)

    def resize(self,size):
        #x1 and y1 should not change, only x2 and y2
        angle = self.getAngle()
        self.x2 = self.x1+size*math.cos(angle)
        self.y2 = self.y1+size*math.sin(angle)


    """def enCollision(self, forme):
        if isinstance(forme, Rectangle):
            return self.__enCollisionRectangle(forme)
        elif isinstance(forme, Cercle):
            return self.__enCollisionCercle(forme)
        elif isinstance(forme, Ligne):
            return self.__enCollisionLigne(forme)

    def perp(self, a ) :
        b = numpy.empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    def __enCollisionLigne(self, forme):
        ligne1 = self
        ligne2 = forme
        a1 = numpy.array( [ligne1.x1, ligne1.y1] )
        a2 = numpy.array( [ligne1.x2, ligne1.y2] )
        b1 = numpy.array( [ligne2.x1, ligne2.y1] )
        b2 = numpy.array( [ligne2.x2, ligne2.y2] )
        da = a2-a1
        db = b2-b1
        dp = a1-b1
        dap = self.perp(da)
        denom = numpy.dot( dap, db)
        num = numpy.dot( dap, dp )
        point =  (num / denom)*db + b1
        print point
        if point[0] in numpy.arange(a1[0],a2[0]) and point[0] in numpy.arange(b1[0],b2[0]):
            return True
        if point[1] in numpy.arange(a1[1],a2[1]) and point[1] in numpy.arange(b1[1],b2[1]):
            return True
        return False

    def __enCollisionRectangle(self, forme):
        rectangle = forme
        haut=Ligne("haut",rectangle.x1,rectangle.y1,rectangle.x2,rectangle.y1,"black")
        bas=Ligne("bas",rectangle.x1,rectangle.y2,rectangle.x2,rectangle.y2,"black")
        gauche=Ligne("gauche",rectangle.x1,rectangle.y1,rectangle.x1,rectangle.y2,"black")
        droite=Ligne("droite",rectangle.x2,rectangle.y1,rectangle.x2,rectangle.y2,"black")
        if self.__enCollisionLigne(haut) or self.__enCollisionLigne(bas) or self.__enCollisionLigne(gauche) or self.__enCollisionLigne(droite):
            return True
        return False

    def __enCollisionCercle(self, forme):
        cercle = forme
        listeRect = []
        nbrect = 7
        for i in numpy.arange(0,math.pi,math.pi/(nbrect+1)):
            x = cercle.rayon *1.*math.sin(i)
            y = cercle.rayon *1. *math.cos(i)
            rect = Rectangle("", cercle.x-x, cercle.y-y, cercle.x+x, cercle.y+y, "red")
            listeRect.append(rect)
        for rect in listeRect:
            if self.__enCollisionRectangle(rect):
                return True
        return False"""