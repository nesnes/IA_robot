import copy
import time
from cartographie.ligne import  Ligne
from cartographie.collison import Collision


class ChercheurChemin:
    def enCollisionCarte(self,ligne,_listePointInteret):
        tester = Collision(self.fenetre)
        listePointInteret=sorted(_listePointInteret, key=lambda pointInteret : Ligne("",ligne.x1,ligne.y1,ligne.x1,ligne.y1).distanceAvec(pointInteret.forme))
        for point in listePointInteret:
           if tester.collisionEntre(ligne,point.zoneEvitement.forme):
                return point
        return False

    def supprimerElementsContenant(self,x1,y1,x2,y2,listePointInteret):
        tester = Collision()
        for element in listePointInteret:
            if tester.contenuDans(x1,y1,element.zoneEvitement.forme):
                listePointInteret.remove(element)
            elif tester.contenuDans(x2,y2,element.zoneEvitement.forme):
                listePointInteret.remove(element)

    def trouverChemin(self,x1,y1,x2,y2,_listePointInteret, fenetre=None, depth=0):
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
        return tabchemin

    def simplifierChemin(self, tabchemin, listPointInteret):
        tabLen = tabchemin.__len__()-1
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