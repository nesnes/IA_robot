import copy
import time
import pickle
import sys
import os
import xml.etree.ElementTree as ET
from collections import deque
from cartographie.ligne import  Ligne
from cartographie.collison import Collision
from cartographie.graph import Graph
from cartographie.noeud import Noeud


class ChercheurChemin:

    def __init__(self, dimensions, mapHash, listePointInteret, fenetre=None):
        self.largeur = int(dimensions[0])
        self.longueur = int(dimensions[1])
        self.mapHash = mapHash
        self.listePointInteret = listePointInteret
        self.graph = Graph()
        self.fenetre = fenetre
        self.step = 40
        self.graphFile = "preComputedMap.graph"
        savedGraph = None
        graphLoaded = False
        t = time.time()
        if not self.loadGraph():
            print "Graph file can't be used, need to compute it"
            self.createGraph(self.listePointInteret)
            self.saveGraph()
            print "Graph saved ("+self.mapHash+")"
        else:
            print "Graph loaded from file ("+self.mapHash+")"
        print "LoadTime: " + str(time.time() - t)

    def saveGraph(self):
        file = open(self.graphFile, "w")
        if file:
            file.write(self.graph.serialize(self.mapHash))
            return True
        return False

    def loadGraph(self):
        if not os.path.isfile(self.graphFile):
            return False
        tree = ET.parse(self.graphFile)
        root = tree.getroot()
        if root.tag == "graph":
            if root.get("hash") != self.mapHash:
                return False
            self.graph = Graph()
            self.graph.initFromSerialization(root, self.listePointInteret)
        else:
            return False
        return True

    def createGraph(self, listePointInteret):
        self.graph = Graph()
        for x in range(0, self.largeur + 1, self.step):
            for y in range(0, self.longueur + 1, self.step):
                objects = self.pointContenuListe(x, y, listePointInteret)
                newNoeud = Noeud(x,y)
                newNoeud.colisionObject = objects
                self.graph.addNoeud(newNoeud)
        self.graph.creerVoisins(self.step)

    def enCollisionCarte(self,ligne,_listePointInteret, ignoreEvitmentZone=False):
        tester = Collision(self.fenetre)
        listePointInteret=sorted(_listePointInteret, key=lambda pointInteret : Ligne("",ligne.x1,ligne.y1,ligne.x1,ligne.y1).distanceAvec(pointInteret.forme))
        for point in listePointInteret:
            if ignoreEvitmentZone:
                if tester.collisionEntre(ligne, point.forme):
                    return point
            else:
                if tester.collisionEntre(ligne,point.zoneEvitement.forme):
                    return point
        return False

    def pointContenuDans(self,x,y,listePointInteret):
        tester = Collision()
        for element in listePointInteret:
            if tester.contenuDans(x,y,element.zoneEvitement.forme):
                return element
        return None

    def pointContenuListe(self,x,y,listePointInteret):
        tester = Collision()
        elementList = []
        for element in listePointInteret:
            if tester.contenuDans(x,y,element.zoneEvitement.forme):
                elementList.append(element)
        return elementList

    def updateNodesRemovingElement(self, element, listePointInteret):
        tmpList = list(listePointInteret)  # copy
        tmpList.remove(element)
        for key, noeud in self.graph.listeNoeud.iteritems():
            if element in noeud.colisionObject:
                noeud.colisionObject.remove(element)#line added during cup 2017
                tester = Collision(self.fenetre)
                line = Ligne("", noeud.x, noeud.y, noeud.x, noeud.y)
                tmpList = sorted(tmpList,key=lambda pointInteret: line.distanceAvec(pointInteret.forme))
                for point in listePointInteret:
                    if tester.collisionEntre(line, point.zoneEvitement.forme):
                        noeud.colisionObject = point
                        break

    def supprimerElementsContenant(self,x1,y1,x2,y2,listePointInteret):
        tester = Collision()
        for element in listePointInteret:
            if tester.contenuDans(x1,y1,element.zoneEvitement.forme):
                self.updateNodesRemovingElement(element, listePointInteret)
                listePointInteret.remove(element)
            elif (x1 != x2 or y1 != y2) and tester.contenuDans(x2,y2,element.zoneEvitement.forme):
                self.updateNodesRemovingElement(element, listePointInteret)
                listePointInteret.remove(element)
        self.createGraph(self.listePointInteret)



    def trouverChemin(self,x1,y1,x2,y2,_listePointInteret):
        directLine = Ligne("",x1,y1,x2,y2)
        if not self.enCollisionCarte(directLine,_listePointInteret):
            return [directLine]
        self.graph.nettoyer()
        #Point contained in objects
        startElements = self.pointContenuListe(x1, y1, _listePointInteret)
        endElements = self.pointContenuListe(x2, y2, _listePointInteret)
        blockingElements = startElements + endElements

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
                    addNode = True
                    if len(noeud.colisionObject) != 0:
                        for elem in noeud.colisionObject:
                            if not elem in blockingElements:
                                self.graph.marquer(noeud)
                                addNode = False
                                break
                    if(addNode):
                        self.graph.setPere(noeud, currentNode)
                        self.graph.marquer(noeud)
                        listnoeud.append(noeud)
        listPoint = []
        lastNode = endNode
        currentNode = self.graph.getPere(endNode)
        if currentNode == None:
            pass
        elif self.graph.getPere(currentNode) == None:
            #from endNode
            listPoint.append([x2, y2])
            #trip
            listPoint.append([lastNode.x, lastNode.y])
            listPoint.append([currentNode.x, currentNode.y])
            #to startNode
            listPoint.append([x1, y1])
        else:
            #from endNode
            listPoint.append([x2, y2])
            listPoint.append([lastNode.x, lastNode.y])
            #trip
            while self.graph.getPere(currentNode) != None:
                listPoint.append([currentNode.x, currentNode.y])
                currentNode = self.graph.getPere(currentNode)
            # to startNode
            listPoint.append([x1, y1])

        tmpList = list(_listePointInteret)

        for elem in blockingElements:
            try:    
                tmpList.remove(elem)
            except ValueError:
                print(elem) 

        listPoint.reverse()
        listChemin = []
        for i in range(1, len(listPoint)):
            p1 = listPoint[i-1]
            p2 = listPoint[i]
            line = Ligne("", p1[0], p1[1], p2[0], p2[1])
            listChemin.append(line)
        self.simplifierChemin(listChemin, tmpList)

        return listChemin


    def simplifierChemin(self, tabchemin, listPointInteret):
        i=-1
        while i < len(tabchemin)-2:
            i+=1
            l1 = tabchemin[i]
            l2 = tabchemin[i+1]
            line = Ligne("",l1.x1, l1.y1, l2.x2, l2.y2, "")
            #line.setCouleur("white")
            #line.dessiner(self.fenetre)
            if not self.enCollisionCarte(line,listPointInteret):
                tabchemin.insert(i,line)
                tabchemin.remove(l1)
                tabchemin.remove(l2)
                i=-1
        return tabchemin
