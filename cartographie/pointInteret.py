import hashlib

class PointInteret:

    def __init__(self,nom="no name",forme=None,zoneAcces=None,zoneEvitement=None,valeur=None,action=None,type=None,couleur=None):
        self.nom = nom
        self.type = type
        self.couleur = couleur
        self.forme = forme
        self.zoneAcces = zoneAcces
        self.zoneEvitement = zoneEvitement
        self.valeur = valeur
        self.action = action
        self.id = ""
        self.getID()

    def dessiner(self,fenetre):
        if self.zoneEvitement!=None:self.zoneEvitement.dessiner(fenetre)
        if self.zoneAcces!=None:self.zoneAcces.dessiner(fenetre)
        if self.forme!=None:self.forme.dessiner(fenetre)

    def getID(self):
        if self.id == "":
            id = str(self.forme.x)
            id += "_" + str(self.forme.y)
            id += "_" + self.nom
            id += "_" + self.couleur
            id += "_" + self.type
            id += "_" + str(self.valeur)
            self.id = hashlib.md5(id).hexdigest()[0:6]
        return self.id
