from forme import *

class Rectangle(Forme):
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
        couleur = newCouleur

    def dessiner(self, fenetre):
        fenetre.drawRectangle(self.nom, self.x1, self.y1, self.x2, self.y2, self.couleur_ui)


    def toJson(self):
        str = u''.join([u'{',
            u'"type":"rect",',
            u'"name":"{}",'.format(self.nom),
            u'"x":{},'.format(self.x1),
            u'"y":{},'.format(self.y1),
            u'"width":{},'.format(self.x2-self.x1),
            u'"height":{},'.format(self.y2-self.y1),
            u'"color":"{}"'.format(self.couleur_ui),
            u'}'])
        return str
