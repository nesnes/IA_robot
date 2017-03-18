from cartographie.noeud import Noeud

class Graph:

    def __init__(self):
        self.listeNoeud = {}

    def serialize(self, hash):
        serialization = "<graph"
        serialization += " hash='" + hash + "'"
        serialization += " >\r\n"
        for key, noeud in self.listeNoeud.iteritems():
            serialization += noeud.serialize() + "\r\n"
        serialization += "</graph>"
        return serialization

    def initFromSerialization(self, serialization, listePointInteret):
        listVoisin = {}
        listColision = {}
        for node in serialization:
            if node.tag == "n":
                x = int(node.get("x"))
                y = int(node.get("y"))
                newNoeud = Noeud(x, y)
                self.addNoeud(newNoeud)
                listVoisin[newNoeud.getID()] = []
                listColision[newNoeud.getID()] = []
                voisinIds = node.get("v").split(";")
                colisionIds = node.get("c").split(";")
                if voisinIds[0] != '':
                    for id in voisinIds:
                        listVoisin[newNoeud.getID()].append(id)
                if colisionIds[0] != '':
                    for id in colisionIds:
                        listColision[newNoeud.getID()].append(id)
        for nodeId, idList in listVoisin.iteritems():
            currentNode = self.listeNoeud[nodeId]
            for idNode in idList:
                currentNode.listVoisin.append(self.listeNoeud[idNode])
        mapPointInteret = {}
        for point in listePointInteret:
            mapPointInteret[point.getID()] = point
        for nodeId, idList in listColision.iteritems():
            currentNode = self.listeNoeud[nodeId]
            for idObject in idList:
                currentNode.colisionObject.append(mapPointInteret[idObject])

    def addNoeud(self, noeud):
        self.listeNoeud[str(noeud.x)+","+str(noeud.y)] = noeud

    def getKey(self, x, y):
        return str(x) + "," + str(y)

    def getNoeud(self, x, y):
        return self.listeNoeud[self.getKey(x, y)]

    def dessiner(self, fenetre):
        for key, noeud in self.listeNoeud.iteritems():
            noeud.dessiner(fenetre)

    def creerVoisins(self, step):
        for key, noeud in self.listeNoeud.iteritems():
            x = noeud.x
            y = noeud.y
            voisins = [[-1,0],[1,0],[0,-1],[0,1], [-1,-1],[1,1],[1,-1],[-1,1]]
            for position in voisins:
                if self.getKey(x+position[0]*step, y+position[1]*step) in self.listeNoeud:
                    noeud.addVoisin(self.getNoeud(x+position[0]*step, y+position[1]*step))

    def trouverPointProche(self, x, y):
        nearest = None
        minDist = 999999
        for key, noeud in self.listeNoeud.iteritems():
            dist = noeud.distanceAvecXY(x,y)
            if minDist > dist:
                nearest = noeud
                minDist = dist
        return nearest

    def marquer(self, noeud):
        noeud.visite = True

    def estMaquer(self, noeud):
        return noeud.visite

    def setPere(self, noeud, pere):
        noeud.pere = pere

    def getPere(self, noeud):
        return noeud.pere

    def getVoisin(self, noeud):
        return noeud.listVoisin

    def nettoyer(self):
        for key, noeud in self.listeNoeud.iteritems():
            noeud.visite = False
            noeud.pere = None
