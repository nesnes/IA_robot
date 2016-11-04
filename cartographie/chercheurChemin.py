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
                if( not self.pointContenuDans(x,y, self.listePointInteret)):
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

    '''def trouverChemin(self,x1,y1,x2,y2,_listePointInteret, fenetre=None, depth=0):
        if depth > 50:
            return None
        #print depth
        self .fenetre = fenetre
        listePointInteret = list(_listePointInteret) #value copy (so the list is editable)
        tester = Collision()
        tabchemin = []
        trouve = False
        dessin = False
        self.supprimerElementsContenant(x1,y1,x2,y2,listePointInteret)
        ligne = Ligne("",x1,y1,x2,y2,"blue")
        if dessin: ligne.dessiner(fenetre)

        if  x1 == x2 and y1 == y2: # if goes to the same position
            return tabchemin

        if( not self.enCollisionCarte(ligne,listePointInteret)): #if there is not collision in strait line
            tabchemin.append(Ligne("",x1,y1,x2,y2))
            return tabchemin
        if(depth<30):
            ligne.resize(ligne.getlongeur()/2)
        elif(depth%2==0):
            ligne.resize(ligne.getlongeur()/2)
        angle = 0
        bestAngle = None
        for size in range(1,2,1):
            while angle <= 180:
                if depth<30:
                    angle += 5
                else:
                    angle += 2.5
                if(angle >= 180 and bestAngle == None):
                    angle = 0
                    ligne.resize(ligne.getlongeur()/2)

                newLine =copy.copy(ligne)
                newLine1=copy.copy(ligne)
                newLine2=copy.copy(ligne)
                angle1=newLine.getAngle()+angle*-1
                newLine1.rotate(angle1)
                angle2=newLine.getAngle()+angle
                newLine2.rotate(angle2)
                distLine = Ligne("",newLine.x2,newLine.y2,newLine.x2,newLine.y2,"").distanceAvec(Ligne("",x2,y2,x2,y2))
                distLine2 = Ligne("",newLine2.x2,newLine2.y2,newLine2.x2,newLine2.y2,"").distanceAvec(Ligne("",x2,y2,x2,y2))
                distLine1 = Ligne("",newLine1.x2,newLine1.y2,newLine1.x2,newLine1.y2,"").distanceAvec(Ligne("",x2,y2,x2,y2))

                collisionLine1 = self.enCollisionCarte(newLine1,listePointInteret)
                collisionLine2 = self.enCollisionCarte(newLine2,listePointInteret)

                #draw the failed lines
                if collisionLine1:
                    newLine1.setCouleur("orange")
                    if dessin: newLine1.dessiner(fenetre)
                else:
                    newLine1.setCouleur("purple")
                    if dessin: newLine1.dessiner(fenetre)

                if collisionLine2:
                    newLine2.setCouleur("yellow")
                    if dessin: newLine2.dessiner(fenetre)
                else:
                    newLine2.setCouleur("purple")
                    if dessin: newLine2.dessiner(fenetre)

                # best angle
                if bestAngle != None:
                    bestLine = copy.copy(ligne)
                    bestLine.rotate(bestAngle)
                    bestDist = Ligne("",bestLine.x2,bestLine.y2,bestLine.x2,bestLine.y2,"").distanceAvec(Ligne("",x2,y2,x2,y2))
                    if bestDist > distLine2 and not collisionLine2:
                        bestAngle = angle2
                        bestDist = distLine2
                    if bestDist > distLine1 and not collisionLine1 :
                        bestAngle = angle1
                        bestDist = distLine1
                else:
                    if not collisionLine1:
                        bestAngle = angle1
                    if not collisionLine2:
                        bestAngle = angle2
                    if not collisionLine1 and not collisionLine2:
                        if distLine2 < distLine1:
                            bestAngle = angle2
                        else:
                            bestAngle = angle1

        bestLine=copy.copy(ligne)
        bestLine.rotate(bestAngle)
        if dessin:
            bestLine.setCouleur("black")
            bestLine.dessiner(fenetre)
        tabchemin.append(bestLine)
        nextChemin = self.trouverChemin(bestLine.x2,bestLine.y2,x2,y2,listePointInteret,fenetre, depth+1)
        if nextChemin == None:
            return None
        else:
            for l in nextChemin:
                tabchemin.append(l)
        self.simplifierChemin(tabchemin,listePointInteret)
        return tabchemin'''
