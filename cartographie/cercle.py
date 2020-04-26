from forme import *


class Cercle(Forme):

    def __init__(self,nom="no name",x=0,y=0,rayon=0,couleur="black",couleur_ui=""):
        self.nom = nom
        self.x = x
        self.y = y
        self.rayon = rayon
        self.couleur = couleur
        self.couleur_ui = couleur_ui if couleur_ui != "" else couleur
        self.lineList = []

    def resetLineList(self):
        self.lineList = []

    def setCouleur(self,newCouleur):
        couleur = newCouleur

    def dessiner(self,fenetre):
        fenetre.drawCircle(self.nom,self.x,self.y, self.rayon,self.couleur_ui)

    def toJson(self):
        str = u''.join([u'{',
            u'"type":"circle",',
            u'"name":"{}",'.format(self.nom),
            u'"x":{},'.format(self.x),
            u'"y":{},'.format(self.y),
            u'"radius":{},'.format(self.rayon),
            u'"color":"{}"'.format(self.couleur_ui),
            u'}'])
        return str

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
