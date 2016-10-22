import math

import numpy

from cartographie.ligne import Ligne

from cartographie.rectangle import Rectangle


class Collision:

    fenetre = None

    def __init__(self, fenetre = None):
        self.fenetre = fenetre

    def collisionEntre(self,forme1,forme2):
        return getattr(self,"collision"+forme1.__class__.__name__+forme2.__class__.__name__)(forme1,forme2)

    def contenuDans(self,x,y,forme):
        return getattr(self,"contient"+forme.__class__.__name__)(x,y,forme)

    def contientRectangle(self,x,y,rectangle):
        contient = False
        if rectangle.x1<=x and rectangle.x2>=x   and   rectangle.y1<=y and rectangle.y2>=y:
            contient = True
        return contient

    def contientLigne(self,x,y,ligne):
        return False

    def contientCercle(self,x,y,cercle):
        dist = cercle.distanceAvec(Ligne("",x,y,x,y,""))
        if(dist <= cercle.rayon):
            return True
        return False

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
        return  self.collisionRectangleLigne(rectangle,ligne)

    def collisionRectangleRectangle(self,rectangle1,rectangle2):
        rect1 = self
        rect2 = forme
        OutsideBottom = rect1.y2 < rect2.y1
        OutsideTop = rect1.y1 > rect2.y2
        OutsideLeft = rect1.x1 > rect2.x2
        OutsideRight = rect1.x2 < rect2.x1
        return not (OutsideBottom or OutsideTop or OutsideLeft or OutsideRight)

    def collisionCercleLigne(self,cercle,ligne):
        listeLigne = []
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

        for ligne1 in listeLigne:
            """if self.fenetre != None:
                ligne.setCouleur("blue")
                ligne.dessiner(self.fenetre)"""
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