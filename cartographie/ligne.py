import math
from forme import *

from math import atan2, degrees, pi

#from rectangle import Rectangle
#from cercle import Cercle

class Ligne(Forme):
    def __init__(self, nom, x1=0, y1=0, x2=0, y2=0, couleur="black", couleur_ui=""):
        self.nom = nom
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x = (x1+x2)/2
        self.y = (y1+y2)/2
        self.couleur = couleur
        self.couleur_ui = couleur_ui if couleur_ui != "" else couleur

    def setCouleur(self, newCouleur):
        self.couleur = newCouleur

    def dessiner(self, fenetre):
        fenetre.drawLine(self.nom, self.x1, self.y1, self.x2, self.y2, self.couleur_ui)

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
        radangle = self.getAngle() * 0.0174532925  # degree vers radian
        self.x2 = self.x1+size*math.cos(radangle)
        self.y2 = self.y1+size*math.sin(radangle)

    def toJson(self):
        str = u''.join([u'{',
            u'"type":"line",',
            u'"name":"{}",'.format(self.nom),
            u'"x1":{},'.format(self.x1),
            u'"y1":{},'.format(self.y1),
            u'"x2":{},'.format(self.x2),
            u'"y2":{},'.format(self.y2),
            u'"color":"{}"'.format(self.couleur_ui),
            u'}'])
        return str
