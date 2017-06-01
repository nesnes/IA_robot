import math

class Noeud:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.listVoisin = []
        self.visite=False
        self.pere = None
        self.colisionObject = []
        self.id = str(self.x) + "," + str(self.y)

    def getID(self):
        return self.id

    def serialize(self):
        serialization = "<n"
        serialization += " id='" + self.getID() + "'"
        serialization += " x='" + str(self.x) + "'"
        serialization += " y='" + str(self.y) + "'"
        serialization += " v='"
        i = 0
        for voisin in self.listVoisin:
            if i != 0: serialization += ";"
            serialization += voisin.getID()
            i+=1
        serialization += "'"
        serialization += " c='"
        i = 0
        for object in self.colisionObject:
            if i != 0: serialization += ";"
            serialization += object.getID()
            i+=1
        serialization += "'"

        serialization += "/>"
        return serialization

    def addVoisin(self, voisin):
        if not voisin in self.listVoisin:
            self.listVoisin.append(voisin)

    def distanceAvec(self, noeud):
        x = max(self.x, noeud.x) - min(self.x, noeud.x)
        y = max(self.y, noeud.y) - min(self.y, noeud.y)
        return math.sqrt(math.pow(x, 2) + math.pow(y, 2))

    def distanceAvecXY(self, x, y):
        x = max(self.x, x) - min(self.x, x)
        y = max(self.y, y) - min(self.y, y)
        return math.sqrt(math.pow(x, 2) + math.pow(y, 2))

    def dessiner(self, fenetre, color="black"):
        size = 5
        if(color == "black" and len(self.colisionObject) != 0):
            color = "purple"
        fenetre.drawLine("", self.x-size, self.y-size, self.x+size, self.y+size, color)
        fenetre.drawLine("", self.x+size, self.y-size, self.x-size, self.y+size, color)
