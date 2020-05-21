import copy
import time
import pickle
import sys
import os
import math
import numpy
import xml.etree.ElementTree as ET
from collections import deque
try:
    from cartographie.ligne import Ligne
    from cartographie.cercle import Cercle
    from cartographie.rectangle import Rectangle
    from cartographie.polygone import Polygone
    from cartographie.collison import Collision
except ImportError:
    from ligne import Ligne
    from cercle import Cercle
    from rectangle import Rectangle
    from polygone import Polygone
    from collison import Collision


class ChercheurChemin:

    def __init__(self, dimensions, mapHash, listePointInteret, fenetre=None):
        self.largeur = int(dimensions[0])
        self.longueur = int(dimensions[1])
        self.mapHash = mapHash
        self.listePointInteret = listePointInteret
        self.fenetre = fenetre
        self.collider = Collision(fenetre)

    #Based on object shapes
    #@profile
    def enCollisionCarte(self,ligne,_listePointInteret, ignoreEvitmentZone=False):
        collisionEntre = self.collider.collisionEntre #local var perf optim
        listePointInteret=sorted(_listePointInteret, key=lambda pointInteret : Ligne("",ligne.x1,ligne.y1,ligne.x1,ligne.y1).distanceAvec(pointInteret.forme))
        for point in listePointInteret:
            if ignoreEvitmentZone:
                if collisionEntre(ligne, point.forme):
                    return point
            else:
                if collisionEntre(ligne,point.zoneEvitement.forme):
                    return point
        return False

    def pointContenuDans(self,x,y,listePointInteret):
        contenuDans = self.collider.contenuDans #local var perf optim
        for element in listePointInteret:
            if contenuDans(x,y,element.zoneEvitement.forme):
                return element
        return None

    def pointContenuListe(self,x,y,listePointInteret):
        contenuDans = self.collider.contenuDans #local var perf optim
        elementList = []
        for element in listePointInteret:
            if contenuDans(x,y,element.zoneEvitement.forme):
                elementList.append(element)
        return elementList

    """def updateNodesRemovingElement(self, element, listePointInteret):
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
                        break"""

    """def supprimerElementsContenant(self,x1,y1,x2,y2,listePointInteret):
        for element in listePointInteret:
            if self.collider.contenuDans(x1,y1,element.zoneEvitement.forme):
                self.updateNodesRemovingElement(element, listePointInteret)
                listePointInteret.remove(element)
            elif (x1 != x2 or y1 != y2) and self.collider.contenuDans(x2,y2,element.zoneEvitement.forme):
                self.updateNodesRemovingElement(element, listePointInteret)
                listePointInteret.remove(element)
        self.createGraph(self.listePointInteret)"""

    def extendLinePoint(self, forme, x, y):
        ligne = Ligne("", forme.x, forme.y, x, y)
        ligne.resize(ligne.getlongeur()+30)
        point = {"x":ligne.x2, "y":ligne.y2}
        return point

    def resetCollisonLists(self, listePointInteret):
        for a in listePointInteret:
            a.collisionList = None

    #@profile
    def computeCollisonList(self, element, listePointInteret):
        if not element.collisionList is None:
            return
        
        collisionEntre = self.collider.collisionEntre #local var perf optim
        element.collisionList = []
        elementf = element.zoneEvitement.forme if element.zoneEvitement else element.forme
        for b in listePointInteret:
            if b.getID() == element.getID():
                continue
            bf = b.zoneEvitement.forme if b.zoneEvitement else b.forme
            if collisionEntre(elementf, bf):
                element.collisionList.append(b)

    #@profile
    def trouverChemin(self,x1,y1,x2,y2,_listePointInteret):
        collisionEntre = self.collider.collisionEntre #local var perf optim
        startElements = self.pointContenuListe(x1, y1, _listePointInteret)
        endElements = self.pointContenuListe(x2, y2, _listePointInteret)
        blockingElements = startElements + list(set(endElements) - set(startElements)) #merge removing duplicates
        t = time.time()
        #self.computeElementsCollisonList(_listePointInteret)
        #print "Init Collisions: " + str(time.time() - t)
        

        listePointInteret=sorted(_listePointInteret, key=lambda pointInteret : Ligne("",x1,y1,x1,y1).distanceAvec(pointInteret.forme))
        self.resetCollisonLists(listePointInteret)
        #self.fenetre = None
        initLine = Ligne("",x1,y1,x2,y2)
        if self.fenetre:
            initLine.setCouleur("violet")
            initLine.dessiner(self.fenetre)
        pathList = [[initLine]]
        countTest = 0
        tl = time.time()
        while len(pathList)>0:
            #print("{} loop: {}".format(time.time()-tl, countTest))
            tl = time.time()
            countTest += 1
            #print(pathList)
            path = pathList.pop(0) #get firt path
            if self.fenetre:
                #self.fenetre.clear()
                for l in path:
                    l.setCouleur("blue")
                    l.dessiner(self.fenetre)
                self.fenetre.win.redraw()
                #time.sleep(0.02)
            ligne = path.pop() #get last line
            collidePoint = self.enCollisionCarte(ligne, listePointInteret, False)
            if not collidePoint:
                path.append(ligne)
                #print countTest
                t = time.time()
                self.simplifierChemin(path, listePointInteret, blockingElements)
                #print "\tSimplifyPathTime: " + str(time.time() - t)
                #print "Chemin Simplified len ", len(path)
                return path
            else:
                collidedObjects = [collidePoint]
                self.computeCollisonList(collidePoint, listePointInteret)
                collidedObjects += collidePoint.collisionList
                #find objects coliding current object
                """for obj in listePointInteret:
                    if obj == collidePoint:
                        continue
                    formeCollidePoint = collidePoint.zoneEvitement.forme if collidePoint.zoneEvitement else collidePoint.forme
                    formeObj = obj.zoneEvitement.forme if obj.zoneEvitement else obj.forme
                    if self.collider.collisionEntre(formeCollidePoint, formeObj):
                        collidedObjects.append(obj)"""
                
                points = []
                for collidedObj in collidedObjects:
                    #List collided object's points
                    objectPoints = []
                    forme = collidedObj.zoneEvitement.forme if collidedObj.zoneEvitement else collidedObj.forme                    
                    #print("colided with {} {}".format(forme.__class__.__name__, collidedObj.nom ))
                    if isinstance(forme, Ligne): 
                        objectPoints.append(self.extendLinePoint(forme, forme.x1, forme.y1))
                        objectPoints.append(self.extendLinePoint(forme, forme.x2, forme.y2))
                    if isinstance(forme, Rectangle): 
                        objectPoints.append(self.extendLinePoint(forme, forme.x1, forme.y1))
                        objectPoints.append(self.extendLinePoint(forme, forme.x2, forme.y1))
                        objectPoints.append(self.extendLinePoint(forme, forme.x1, forme.y2))
                        objectPoints.append(self.extendLinePoint(forme, forme.x2, forme.y2))
                    if isinstance(forme, Polygone): 
                        for p in forme.pointList:
                            objectPoints.append(self.extendLinePoint(forme, p["x"], p["y"]))
                    if isinstance(forme, Cercle): 
                        nbpoint = 8
                        for i in numpy.arange(0,math.pi*2,math.pi*2/(nbpoint+1)):
                            x = forme.x + forme.rayon *1.*math.sin(i)
                            y = forme.y + forme.rayon *1. *math.cos(i)
                            objectPoints.append(self.extendLinePoint(forme, x, y))
                            """c = Cercle("", x, y, 10, "white")
                            c.dessiner(self.fenetre)
                            self.fenetre.win.redraw()"""
                    
                    #Exclude points colliding with direct line
                    for p in objectPoints:
                        #Exclude out of table
                        if p["x"]<0 or p["x"]>self.largeur or p["y"]<0 or p["y"]>self.longueur:
                            continue
                        #Exclude same point
                        if ligne.x1 == p["x"] and ligne.y1 == p["y"]:
                            continue
                        #Exclude point already in path
                        found = False
                        for l in path:
                            if (l.x1 == p["x"] and l.y1 == p["y"]) or (l.x2 == p["x"] and l.y2 == p["y"]):
                                found = True
                                break
                        if found:
                            continue
                        #Exculde from collisions
                        directLine = Ligne("",ligne.x1,ligne.y1,p["x"],p["y"])
                        if collisionEntre(directLine, forme):
                            continue
                        if self.enCollisionCarte(directLine, listePointInteret, False):
                            continue
                        if self.fenetre:
                            c = Cercle("", p["x"], p["y"], 10, "black")
                            c.dessiner(self.fenetre)
                            self.fenetre.win.redraw()
                        points.append(p)
                
                for p in points:
                    """c = Cercle("", p["x"], p["y"], 10, "orange")
                    c.dessiner(self.fenetre)
                    self.fenetre.win.redraw()"""
                    newPath = list(path)
                    newPath.append(Ligne("", ligne.x1, ligne.y1, p["x"], p["y"]))
                    newPath.append(Ligne("", p["x"], p["y"], ligne.x2, ligne.y2))
                    pathList.append(newPath)
                #Explore Paths with points
                #print("points: {}".format(len(points)))

                #Remove path ending at same point
                pai = 0
                while pai<len(pathList):
                    pa = pathList[pai]
                    #Look if other path reach same line
                    pa_length = 0
                    stop=False
                    lai = 0
                    while lai<len(pa)-1:
                        la = pa[lai]
                        pa_length+= la.getlongeur()
                        #look for same line in other path
                        pbi = 0
                        while pbi<len(pathList):
                            if pai == pbi:
                                pbi+=1
                                continue
                            pb = pathList[pbi]
                            pb_length = 0
                            lbi = 0
                            while lbi<len(pb)-1:
                                lb = pb[lbi]
                                pb_length+= lb.getlongeur()
                                if la.x1 == lb.x1 and la.y1 == lb.y1 and la.x2 == lb.x2 and la.y2 == lb.y2:
                                    if pa_length<pb_length:
                                        pbi-=1
                                        pathList.pop(pbi)
                                        break
                                    else:
                                        pathList.pop(pai)
                                        pai-=1
                                        stop = True
                                        break
                                lbi+=1
                            if stop:
                                break
                            pbi+=1
                        lai+=1
                        if stop:
                            break
                    pai+=1


                shortestPathMap = {}
                conservedPath = []
                """for currentPath in pathList:
                    length = 0
                    endLine = None
                    for l in range(1, len(currentPath)):
                        if l == len(currentPath)-1:
                            endLine = currentPath[l]
                        else:
                            length += currentPath[l].getlongeur()
                    if not endLine:
                        conservedPath.append(currentPath)
                        continue
                    x = endLine.x1
                    y = endLine.y1
                    key = str(x)+","+str(y)
                    if (key in shortestPathMap and shortestPathMap[key]["length"] > length) or not key in shortestPathMap:
                        shortestPathMap[key] = {"length": length, "path": currentPath}
                for key, noeud in shortestPathMap.iteritems():
                    conservedPath.append(noeud["path"])
                pathList = conservedPath"""
                    
        return []

        """
        print "\tFinilizePathTime: " + str(time.time() - t)
        t = time.time()
        self.simplifierChemin(listChemin, tmpList, blockingElements)
        print "\tSimplifyPathTime: " + str(time.time() - t)
        print "Chemin Simplified len ", len(listChemin)

        return listChemin"""


    def simplifierChemin(self, tabchemin, listPointInteret, blockingElements=None):
        i=-1
        while i < len(tabchemin)-2:
            i+=1
            l1 = tabchemin[i]
            l2 = tabchemin[i+1]
            line = Ligne("",l1.x1, l1.y1, l2.x2, l2.y2, "")
            """line.setCouleur("blue")
            line.dessiner(self.fenetre)"""
            if not self.enCollisionCarte(line,listPointInteret):
            #if not self.enCollisionGraph(line, blockingElements):
                tabchemin.insert(i,line)
                tabchemin.remove(l1)
                tabchemin.remove(l2)
                i=-1
        return tabchemin

if __name__ == "__main__":
    from lecteurCarte import LecteurCarte

    fichierCarte = "../cartes/carte_2019_GoodEnough.xml"
    screen = True
    fenetre = None
    print "Reading map file"
    carte = LecteurCarte(fichierCarte, 150)
    listePointInteret = carte.lire()  # chargement de la carte
    if len(listePointInteret) == 0:
        print "ERROR: Empty map"

    if screen:
        print "Creating map view"
        #import parent folder
        import os,sys,inspect
        current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir) 
        from affichage.afficheurCarte import AfficheurCarte
        affichage = AfficheurCarte(fichierCarte, listePointInteret, 0.25, 300)
        fenetre = affichage.fenetre
        affichage.afficherCarte()  # affichage de la carte

        # creation du pathfinding
        print "Initializing pathfinding"
        chercher = ChercheurChemin(carte.getTaille(), carte.getHash(), listePointInteret, fenetre)

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
                if listMouvement is None or len(listMouvement) == 0:
                    print "WARNING Path Not Found"
                else:
                    for ligne in listMouvement:
                        ligne.setCouleur("green")
                        ligne.dessiner(fenetre)
                t = time.time()
                fenetre.win.redraw()
                print "RedrawTime: " + str(time.time() - t)