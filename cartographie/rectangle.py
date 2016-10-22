from cartographie.forme import *
#from cercle import Cercle


class Rectangle(Forme):
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
        couleur = newCouleur

    def dessiner(self, fenetre):
        fenetre.drawRectangle(self.nom, self.x1, self.y1, self.x2, self.y2, self.couleur)

    """def enCollision(self, forme):
        if isinstance(forme, Rectangle):
            return self.__enCollisionRectangle(forme)
        elif isinstance(forme, Cercle):
            return self.__enCollisionCercle(forme)
        else :
            return forme.enCollision(self)

    def __enCollisionRectangle(self, forme):
        rect1 = self
        rect2 = forme
        OutsideBottom = rect1.y2 < rect2.y1
        OutsideTop = rect1.y1 > rect2.y2
        OutsideLeft = rect1.x1 > rect2.x2
        OutsideRight = rect1.x2 < rect2.x1
        return not (OutsideBottom or OutsideTop or OutsideLeft or OutsideRight)

    def __enCollisionCercle(self, forme):
        rectangle = self
        listCote = []
        listCote.append(Ligne("haut", rectangle.x1, rectangle.y1, rectangle.x2, rectangle.y1, "black"))
        listCote.append(Ligne("bas", rectangle.x1, rectangle.y2, rectangle.x2, rectangle.y2, "black"))
        listCote.append(Ligne("gauche", rectangle.x1, rectangle.y1, rectangle.x1, rectangle.y2, "black"))
        listCote.append(Ligne("droite", rectangle.x2, rectangle.y1, rectangle.x2, rectangle.y2, "black"))

        cercle = forme
        listeRect = []
        nbrect = 7
        for i in numpy.arange(0, math.pi, math.pi / (nbrect + 1)):
            x = cercle.rayon * 1. * math.sin(i)
            y = cercle.rayon * 1. * math.cos(i)
            rect = Rectangle("", cercle.x - x, cercle.y - y, cercle.x + x, cercle.y + y, "red")
            listeRect.append(rect)
        for cote in listCote:
            for rect in listeRect:
                if cote.__enCollisionRectangle(rect):
                    return True
        return False"""