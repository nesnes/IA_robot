from cartographie.forme import *

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
