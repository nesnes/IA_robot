import copy
import time
import pickle
import sys
import os
import xml.etree.ElementTree as ET
from collections import deque
from cartographie.ligne import Ligne
from cartographie.cercle import Cercle
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
        self.step = 80
        self.graphFile = "preComputedMap.graph"
        self.collider = Collision(fenetre)
        self.callCount = {}
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
        tree = None
        try:
            tree = ET.parse(self.graphFile)
        except:
            return False

        root = tree.getroot()
        if root.tag == "graph":
            if root.get("hash") != self.mapHash or not root.get("step"):
                return False
            self.graph = Graph()
            self.graph.initFromSerialization(root, self.listePointInteret)
        else:
            return False
        return True

    def createGraph(self, listePointInteret):
        self.graph = Graph()
        self.graph.step = self.step
        for x in range(0, self.largeur + 1, self.step):
            for y in range(0, self.longueur + 1, self.step):
                objects = self.pointContenuListe(x, y, listePointInteret)
                newNoeud = Noeud(x,y)
                newNoeud.colisionObject = objects
                self.graph.addNoeud(newNoeud)
        self.graph.creerVoisins(self.step)

    #Based on object shapes
    def enCollisionCarte(self,ligne,_listePointInteret, ignoreEvitmentZone=False):
        self.callCount["enCollisionCarte"]=self.callCount["enCollisionCarte"]+1 if "enCollisionCarte" in self.callCount else 1
        listePointInteret=sorted(_listePointInteret, key=lambda pointInteret : Ligne("",ligne.x1,ligne.y1,ligne.x1,ligne.y1).distanceAvec(pointInteret.forme))
        for point in listePointInteret:
            if ignoreEvitmentZone:
                if self.collider.collisionEntre(ligne, point.forme):
                    return point
            else:
                if self.collider.collisionEntre(ligne,point.zoneEvitement.forme):
                    return point
        return False

    #Based on nearests graph points (faster than shape based)
    def enCollisionGraph(self,ligne, blockingElements=None):
        self.callCount["enCollisionGraph"]=self.callCount["enCollisionGraph"]+1 if "enCollisionGraph" in self.callCount else 1
        resolution=self.step
        for i in range(resolution, int(ligne.getlongeur())+resolution, resolution):
            subLine=Ligne("", ligne.x1, ligne.y1, ligne.x2, ligne.y2)
            subLine.resize(float(i))
            node = self.graph.trouverPointProche(subLine.x2, subLine.y2)
            if len(node.colisionObject)>0:
                if blockingElements is None:
                    return True
                else:
                    for elem in node.colisionObject:
                        if not elem in blockingElements:
                            return True
            """if self.fenetre:
                subCircle=Cercle("", subLine.x2, subLine.y2,resolution/2, "blue")
                subCircle.dessiner(self.fenetre)
                subLine.setCouleur("violet")
                subLine.dessiner(self.fenetre)
                ligne.setCouleur("orange")
                ligne.dessiner(self.fenetre)"""
        return False



    def pointContenuDans(self,x,y,listePointInteret):
        for element in listePointInteret:
            if self.collider.contenuDans(x,y,element.zoneEvitement.forme):
                return element
        return None

    def pointContenuListe(self,x,y,listePointInteret):
        elementList = []
        for element in listePointInteret:
            if self.collider.contenuDans(x,y,element.zoneEvitement.forme):
                elementList.append(element)
        return elementList

    def updateNodesRemovingElement(self, element, listePointInteret):
        tmpList = list(listePointInteret)  # copy
        tmpList.remove(element)
        for key, noeud in self.graph.listeNoeud.iteritems():
            if element in noeud.colisionObject:
                noeud.colisionObject.remove(element)#line added during cup 2017
                line = Ligne("", noeud.x, noeud.y, noeud.x, noeud.y)
                tmpList = sorted(tmpList,key=lambda pointInteret: line.distanceAvec(pointInteret.forme))
                for point in listePointInteret:
                    if self.collider.collisionEntre(line, point.zoneEvitement.forme):
                        noeud.colisionObject = point
                        break

    def supprimerElementsContenant(self,x1,y1,x2,y2,listePointInteret):
        for element in listePointInteret:
            if self.collider.contenuDans(x1,y1,element.zoneEvitement.forme):
                self.updateNodesRemovingElement(element, listePointInteret)
                listePointInteret.remove(element)
            elif (x1 != x2 or y1 != y2) and self.collider.contenuDans(x2,y2,element.zoneEvitement.forme):
                self.updateNodesRemovingElement(element, listePointInteret)
                listePointInteret.remove(element)
        self.createGraph(self.listePointInteret)



    def trouverChemin(self,x1,y1,x2,y2,_listePointInteret):
        t = time.time()
        directLine = Ligne("",x1,y1,x2,y2)
        if not self.enCollisionCarte(directLine,_listePointInteret):
            return [directLine]
        print "\tPath Direct test Time: " + str(time.time() - t)
        t = time.time()
        self.graph.nettoyer()
        print "\tPath clean graph Time: " + str(time.time() - t)
        t = time.time()
        #Point contained in objects
        startElements = self.pointContenuListe(x1, y1, _listePointInteret)
        endElements = self.pointContenuListe(x2, y2, _listePointInteret)
        blockingElements = startElements + list(set(endElements) - set(startElements)) #merge removing duplicates
        print "\tPath contain lookup Time: " + str(time.time() - t)
        t = time.time()

        startNode = self.graph.trouverPointProche(x1,y1)
        endNode = self.graph.trouverPointProche(x2,y2)
        print "\tPath close node lookup Time: " + str(time.time() - t)
        t = time.time()
        if startNode == None or endNode == None:
            print "Start or end node not found"
            return None
        listnoeud = deque()
        listnoeud.append(startNode)
        self.graph.marquer(startNode)
        print "\tInitPathTime: " + str(time.time() - t)

        t = time.time()
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

        print "\tSearchPathTime: " + str(time.time() - t)
        t = time.time()
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
                print "ChercheurChemin Err:"+elem.nom #shouldn't pop anymore

        listPoint.reverse()
        listChemin = []
        for i in range(1, len(listPoint)):
            p1 = listPoint[i-1]
            p2 = listPoint[i]
            line = Ligne("", p1[0], p1[1], p2[0], p2[1])
            listChemin.append(line)
        print "Chemin len ", len(listChemin)

        print "\tFinilizePathTime: " + str(time.time() - t)
        t = time.time()
        self.simplifierChemin(listChemin, tmpList, blockingElements)
        print "\tSimplifyPathTime: " + str(time.time() - t)
        print "Chemin Simplified len ", len(listChemin)

        return listChemin


    def simplifierChemin(self, tabchemin, listPointInteret, blockingElements=None):
        i=-1
        while i < len(tabchemin)-2:
            i+=1
            l1 = tabchemin[i]
            l2 = tabchemin[i+1]
            line = Ligne("",l1.x1, l1.y1, l2.x2, l2.y2, "")
            """line.setCouleur("blue")
            line.dessiner(self.fenetre)"""
            #if not self.enCollisionCarte(line,listPointInteret):
            if not self.enCollisionGraph(line, blockingElements):
                tabchemin.insert(i,line)
                tabchemin.remove(l1)
                tabchemin.remove(l2)
                i=-1
        return tabchemin

if __name__ == "__main__":
    from cartographie.lecteurCarte import LecteurCarte

    fichierCarte = "../cartes/carte_2019_GoodEnough.xml"
    screen = True
    drawGraph = True
    fenetre = None
    print "Reading map file"
    carte = LecteurCarte(fichierCarte, 150)
    listePointInteret = carte.lire()  # chargement de la carte
    if len(listePointInteret) == 0:
        print "ERROR: Empty map"

    if screen:
        print "Creating map view"
        from affichage.afficheurCarte import AfficheurCarte
        affichage = AfficheurCarte(fichierCarte, listePointInteret, 0.25, 300)
        fenetre = affichage.fenetre
        affichage.afficherCarte()  # affichage de la carte

        # creation du pathfinding
        print "Initializing pathfinding"
        chercher = ChercheurChemin(carte.getTaille(), carte.getHash(), listePointInteret, fenetre)
        if drawGraph:
            chercher.graph.dessiner(fenetre)

        if fenetre:
            fenetre.win.redraw()

        # Interact with map
        if screen:
            while True:
                click1 = fenetre.win.getMouse()
                click2 = fenetre.win.getMouse()
                x1 = click1.getX() / fenetre.ratio - fenetre.offset
                y1 = click1.getY() / fenetre.ratio - fenetre.offset
                x2 = click2.getX() / fenetre.ratio - fenetre.offset
                y2 = click2.getY() / fenetre.ratio - fenetre.offset
                print "({} {}) ({}, {})".format(x1, y1, x2, y2)

                t = time.time()
                count = 1
                for i in range(0, count, 1):
                    listMouvement = chercher.trouverChemin(x1, y1, x2, y2, listePointInteret)
                print "PathTime: " + str((time.time() - t)/count)
                print "enCollisionCarte called : " + str(chercher.callCount["enCollisionCarte"])
                if listMouvement is None or len(listMouvement) == 0:
                    print "WARNING Path Not Found"
                else:
                    for ligne in listMouvement:
                        ligne.setCouleur("green")
                        ligne.dessiner(fenetre)
                t = time.time()
                fenetre.win.redraw()
                print "RedrawTime: " + str(time.time() - t)