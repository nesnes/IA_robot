from cartographie.forme import *


class Cercle(Forme):
	
    def __init__(self,nom="no name",x=0,y=0,rayon=0,couleur="black"):
        self.nom = nom
        self.x = x
        self.y = y
        self.rayon = rayon
        self.couleur = couleur
        
    def setCouleur(self,newCouleur):
        couleur = newCouleur

    def dessiner(self,fenetre):
        fenetre.drawCircle(self.nom,self.x,self.y, self.rayon,self.couleur)

    """def enCollision(self, forme):
        if isinstance(forme, Cercle):
            return self.__enCollisionCercle(forme)
        else :
            return forme.enCollision(self)

    def __enCollisionCercle(self, forme):
        cercle1 = self
        cercle2 = forme
        distX = cercle1.x - cercle2.x
        distY = cercle1.y - cercle2.y
        dist = math.sqrt((distX * distX) + (distY * distY))
        return dist <= (cercle1.rayon + cercle2.rayon)"""