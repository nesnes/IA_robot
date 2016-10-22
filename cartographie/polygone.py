from cartographie.forme import *

class Polygone(Forme):
    def __init__(self, nom, couleur="black"):
        self.nom = nom
        self.x = 0.0
        self.y = 0.0
        self.pointList = []
        self.couleur = couleur

    def addPoint(self, x, y):
        self.pointList.append({"x": x, "y": y})
        self.x += x/float(len(self.pointList)+1)
        self.y += y/float(len(self.pointList)+1)

    def setCouleur(self, newCouleur):
        couleur = newCouleur

    def dessiner(self, fenetre):
        if len(self.pointList) > 1 :
            fenetre.drawPoly(self.nom, self.pointList, self.couleur)