import math

import numpy
from ligne import Ligne
from cercle import Cercle
from rectangle import Rectangle


class Collision:

    fenetre = None

    def __init__(self, fenetre = None):
        self.fenetre = fenetre

    def collisionEntre(self,forme1,forme2):
        return getattr(self,"collision"+forme1.__class__.__name__+forme2.__class__.__name__)(forme1,forme2)

    def contenuDans(self,x,y,forme):
        if isinstance(forme, Ligne):
            return False
        if isinstance(forme, Cercle):
            return forme.distanceAvec(Ligne("", x, y, x, y)) <= forme.rayon
        if isinstance(forme, Rectangle):
            return forme.x1 <= x and forme.x2 >= x and forme.y1 <= y and forme.y2 >= y
        ligne = Ligne("", x, y, forme.x, forme.y)
        return not self.collisionEntre(ligne, forme)

    def collisionLigneLigne(self,ligne1,ligne2):

        s10_x = ligne1.x2 - ligne1.x1
        s10_y = ligne1.y2 - ligne1.y1
        s32_x = ligne2.x2 - ligne2.x1
        s32_y = ligne2.y2 - ligne2.y1

        denom = s10_x * s32_y - s32_x * s10_y
        if denom == 0:
            return False # Collinear
        denomPositive = denom > 0

        s02_x = ligne1.x1 - ligne2.x1
        s02_y = ligne1.y1 - ligne2.y1
        s_numer = s10_x * s02_y - s10_y * s02_x
        if (s_numer < 0) == denomPositive:
            return False # No collision

        t_numer = s32_x * s02_y - s32_y * s02_x
        if (t_numer < 0) == denomPositive:
            return False # No collision

        if ((s_numer > denom) == denomPositive) or ((t_numer > denom) == denomPositive):
            return False # No collision

        # Collision detected
        return True

    def collisionRectangleLigne(self,rectangle,ligne):
        haut=Ligne("haut",rectangle.x1,rectangle.y1,rectangle.x2,rectangle.y1,"black")
        bas=Ligne("bas",rectangle.x1,rectangle.y2,rectangle.x2,rectangle.y2,"black")
        gauche=Ligne("gauche",rectangle.x1,rectangle.y1,rectangle.x1,rectangle.y2,"black")
        droite=Ligne("droite",rectangle.x2,rectangle.y1,rectangle.x2,rectangle.y2,"black")
        if self.collisionEntre(ligne,haut) or self.collisionEntre(ligne,bas) or self.collisionEntre(ligne,gauche) or self.collisionEntre(ligne,droite):
            return True
        return False

    def collisionLigneRectangle(self,ligne,rectangle):
        return self.collisionRectangleLigne(rectangle, ligne)

    def collisionRectangleRectangle(self,rectangle1,rectangle2):
        rect1 = rectangle1
        rect2 = rectangle2
        OutsideBottom = rect1.y2 < rect2.y1
        OutsideTop = rect1.y1 > rect2.y2
        OutsideLeft = rect1.x1 > rect2.x2
        OutsideRight = rect1.x2 < rect2.x1
        return not (OutsideBottom or OutsideTop or OutsideLeft or OutsideRight)

    def collisionCercleLigne(self,cercle,ligne):
        listeLigne = []
        if len(cercle.lineList)==0:
            nbrect = 8
            x = cercle.x + cercle.rayon *1.*math.sin(0)
            y = cercle.y + cercle.rayon *1. *math.cos(0)
            for i in numpy.arange(0,math.pi*2,math.pi/(nbrect+1)*2):
                x1 = cercle.x + cercle.rayon *1.*math.sin(i)
                y1 = cercle.y + cercle.rayon *1. *math.cos(i)
                ligne1 = Ligne("", x, y, x1, y1, "red")
                listeLigne.append(ligne1)
                x = x1
                y = y1

            x1 = cercle.x + cercle.rayon *1.*math.sin(0)
            y1 = cercle.y + cercle.rayon *1. *math.cos(0)
            listeLigne.append(Ligne("", x, y, x1, y1, "red"))
            cercle.lineList = listeLigne
            """if self.fenetre != None:
                for ligne1 in listeLigne:
                    ligne1.setCouleur("blue")
                    ligne1.dessiner(self.fenetre)"""
        else:
            listeLigne = cercle.lineList

        for ligne1 in listeLigne:
            if self.collisionEntre(ligne1,ligne):
                return True
        return False

    def collisionLigneCercle(self,ligne,cercle):
        return self.collisionCercleLigne(cercle,ligne)

    def collisionCercleCercle(self,cercle1,cercle2):
        distX = cercle1.x - cercle2.x
        distY = cercle1.y - cercle2.y
        dist = math.sqrt((distX * distX) + (distY * distY))
        return dist <= (cercle1.rayon + cercle2.rayon)

    def collisionCercleRectangle(self,cercle,rectangle):
        listCote = []
        listCote.append(Ligne("haut", rectangle.x1, rectangle.y1, rectangle.x2, rectangle.y1, "black"))
        listCote.append(Ligne("bas", rectangle.x1, rectangle.y2, rectangle.x2, rectangle.y2, "black"))
        listCote.append(Ligne("gauche", rectangle.x1, rectangle.y1, rectangle.x1, rectangle.y2, "black"))
        listCote.append(Ligne("droite", rectangle.x2, rectangle.y1, rectangle.x2, rectangle.y2, "black"))

        listeRect = []
        nbrect = 7
        for i in numpy.arange(0, math.pi, math.pi / (nbrect + 1)):
            x = cercle.rayon * 1. * math.sin(i)
            y = cercle.rayon * 1. * math.cos(i)
            rect = Rectangle("", cercle.x - x, cercle.y - y, cercle.x + x, cercle.y + y, "red")
            listeRect.append(rect)
        for cote in listCote:
            for rect in listeRect:
                if self.collisionEntre(rect,cote):
                    return True
        return False

    def collisionRectangleCercle(self,rectangle,cercle):
        return self.collisionCercleRectangle(cercle,rectangle)

    def collisionPolygoneLigne(self, polygone, ligne):
        count=0
        firstPoint = polygone.pointList[0]
        lastPoint = polygone.pointList[0]
        for point in polygone.pointList:
            count+=1
            if count == 1:
                continue
            currentLine = Ligne("", float(point["x"]), float(point["y"]), float(lastPoint["x"]), float(lastPoint["y"]))
            if self.collisionLigneLigne(currentLine, ligne):
                return True
            lastPoint = point
        currentLine = Ligne("", float(firstPoint["x"]), float(firstPoint["y"]), float(lastPoint["x"]), float(lastPoint["y"]))
        if self.collisionLigneLigne(currentLine, ligne):
            return True
        return False

    def collisionLignePolygone(self, ligne, polygone):
        return self.collisionPolygoneLigne(polygone, ligne)

    def collisionPolygonePolygone(self, polygone1, polygone2):
        count = 0
        firstPoint = polygone1.pointList[0]
        lastPoint = polygone1.pointList[0]
        for point in polygone1.pointList:
            count += 1
            if count == 1:
                continue
            currentLine = Ligne("", float(point["x"]), float(point["y"]), float(lastPoint["x"]), float(lastPoint["y"]))
            if self.collisionPolygoneLigne(polygone2, currentLine):
                return True
            lastPoint = point
        currentLine = Ligne("", float(firstPoint["x"]), float(firstPoint["y"]), float(lastPoint["x"]),
                            float(lastPoint["y"]))
        if self.collisionPolygoneLigne(polygone2, currentLine):
            return True
        return False

    def collisionPolygoneRectangle(self, polygone, rectangle):
        count=0
        firstPoint = polygone.pointList[0]
        lastPoint = polygone.pointList[0]
        for point in polygone.pointList:
            count+=1
            if count == 1:
                continue
            currentLine = Ligne("", float(point["x"]), float(point["y"]), float(lastPoint["x"]), float(lastPoint["y"]))
            if self.collisionLigneRectangle(currentLine, rectangle):
                return True
            lastPoint = point
        currentLine = Ligne("", float(firstPoint["x"]), float(firstPoint["y"]), float(lastPoint["x"]), float(lastPoint["y"]))
        if self.collisionLigneRectangle(currentLine, rectangle):
            return True
        return False

    def collisionRectanglePolygone(self, rectangle, polygone):
        return self.collisionPolygoneRectangle(polygone, rectangle)

    def collisionPolygoneCercle(self, polygone, cercle):
        count=0
        firstPoint = polygone.pointList[0]
        lastPoint = polygone.pointList[0]
        for point in polygone.pointList:
            count+=1
            if count == 1:
                continue
            currentLine = Ligne("", float(point["x"]), float(point["y"]), float(lastPoint["x"]), float(lastPoint["y"]))
            if self.collisionLigneCercle(currentLine, cercle):
                return True
            lastPoint = point
        currentLine = Ligne("", float(firstPoint["x"]), float(firstPoint["y"]), float(lastPoint["x"]), float(lastPoint["y"]))
        if self.collisionLigneCercle(currentLine, cercle):
            return True
        return False

    def collisionCerclePolygone(self, cercle, polygone):
        return self.collisionPolygoneCercle(polygone, cercle)
