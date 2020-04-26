from forme import *

class Polygone(Forme):
    def __init__(self, nom, couleur="black", couleur_ui=""):
        self.nom = nom
        self.x = 0.0
        self.y = 0.0
        self.pointList = []
        self.couleur = couleur
        self.couleur_ui = couleur_ui if couleur_ui != "" else couleur

    def addPoint(self, x, y):
        self.pointList.append({"x": x, "y": y})
        self.x = (x + self.x * float(len(self.pointList)-1)) / float(len(self.pointList))
        self.y = (y + self.y * float(len(self.pointList)-1)) / float(len(self.pointList))

    def setCouleur(self, newCouleur):
        couleur = newCouleur

    def dessiner(self, fenetre):
        if len(self.pointList) > 1 :
            fenetre.drawPoly(self.nom, self.pointList, self.couleur_ui)

    def toJson(self):
        str = u'{'
        str += u'"type":"poly",'
        str += u'"name":"{}",'.format(self.nom)
        str += u'"points":['
        for i in range(0, len(self.pointList)):
            str += u'{'
            str += u'"x":{},'.format(self.pointList[i]["x"])
            str += u'"y":{}'.format(self.pointList[i]["y"])
            str += u'}'
            if i < len(self.pointList)-1:
                str += u','
        str += u'],'
        str += u'"color":"{}"'.format(self.couleur_ui)
        str += u'}'
        return str