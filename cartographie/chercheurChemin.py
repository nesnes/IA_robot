import copy
import time
from collections import deque
from cartographie.ligne import  Ligne
from cartographie.collison import Collision
from cartographie.graph import Graph
from cartographie.noeud import Noeud


class ChercheurChemin:

    def __init__(self, dimensions, listePointInteret, fenetre=None):
        self.largeur = int(dimensions[0])
        self.longueur = int(dimensions[1])
        self.listePointInteret = listePointInteret
        self.graph = Graph()
        self.fenetre = fenetre
        self.step = 40
        self.createGraph(self.listePointInteret)

    def createGraph(self, listePointInteret):
        self.graph = Graph()
        for x in range(0, self.largeur + 1, self.step):
            for y in range(0, self.longueur + 1, self.step):
                if( not self.pointContenuDans(x,y, listePointInteret)):
                    newNoeud = Noeud(x,y)
                    self.graph.addNoeud(newNoeud)
        self.graph.creerVoisins(self.step)

    def enCollisionCarte(self,ligne,_listePointInteret):
        tester = Collision(self.fenetre)
        listePointInteret=sorted(_listePointInteret, key=lambda pointInteret : Ligne("",ligne.x1,ligne.y1,ligne.x1,ligne.y1).distanceAvec(pointInteret.forme))
        for point in listePointInteret:
           if tester.collisionEntre(ligne,point.zoneEvitement.forme):
                return point
        return False

    def pointContenuDans(self,x,y,listePointInteret):
        tester = Collision()
        for element in listePointInteret:
            if tester.contenuDans(x,y,element.zoneEvitement.forme):
                return True

    def supprimerElementsContenant(self,x1,y1,x2,y2,listePointInteret):
        tester = Collision()
        for element in listePointInteret:
            if tester.contenuDans(x1,y1,element.zoneEvitement.forme):
                listePointInteret.remove(element)
            elif tester.contenuDans(x2,y2,element.zoneEvitement.forme):
                listePointInteret.remove(element)
        self.createGraph(self.listePointInteret)



    def trouverChemin(self,x1,y1,x2,y2,_listePointInteret, fenetre=None, depth=0):
        directLine = Ligne("",x1,y1,x2,y2)
        if not self.enCollisionCarte(directLine,_listePointInteret):
            return [directLine]
        self.graph.nettoyer()
        startNode = self.graph.trouverPointProche(x1,y1)
        endNode = self.graph.trouverPointProche(x2,y2)
        if startNode == None or endNode == None:
            print "Start or end node not found"
            return None
        listnoeud = deque()
        listnoeud.append(startNode)
        self.graph.marquer(startNode)
        while len(listnoeud)>0:
            currentNode = listnoeud.popleft()
            if currentNode == endNode:
                break
            for noeud in self.graph.getVoisin(currentNode):
                if not self.graph.estMaquer(noeud):
                    self.graph.setPere(noeud, currentNode)
                    self.graph.marquer(noeud)
                    listnoeud.append(noeud)
        listChemin = []
        lastNode = endNode
        currentNode = self.graph.getPere(endNode)
        if currentNode == None:
            pass
        elif self.graph.getPere(currentNode) == None:
            #from endNode
            listChemin.append(Ligne("", x2, y2, lastNode.x, lastNode.y))
            #trip
            listChemin.append(Ligne("", lastNode.x, lastNode.y, currentNode.x, currentNode.y))
            #to endNode
            listChemin.append(Ligne("", currentNode.x, currentNode.y, x1, y1))
        else:
            #from endNode
            listChemin.append(Ligne("", x2, y2, lastNode.x, lastNode.y))
            while self.graph.getPere(currentNode) != None:
                ligne = Ligne("", lastNode.x, lastNode.y, currentNode.x, currentNode.y)
                listChemin.append(ligne)
                lastNode = currentNode
                currentNode = self.graph.getPere(currentNode)
            # to endNode
            listChemin.append(Ligne("", currentNode.x, currentNode.y, x1, y1))
        self.simplifierChemin(listChemin,self.listePointInteret)
        listChemin.reverse()
        return listChemin


    def simplifierChemin(self, tabchemin, listPointInteret):
        tabLen = len(tabchemin)-1
        i=-1
        while i <= tabLen-2:
            i+=1
            line = Ligne("",tabchemin[i].x1,tabchemin[i].y1,tabchemin[i+1].x2,tabchemin[i+1].y2,"")
            #line.setCouleur("white")
            #line.dessiner(self.fenetre)
            if not self.enCollisionCarte(line,listPointInteret):
                tabchemin.remove(tabchemin[i+1])
                tabchemin.remove(tabchemin[i])
                tabchemin.insert(i,line)
                tabLen = tabchemin.__len__()-1
                i=-1
        return tabchemin
