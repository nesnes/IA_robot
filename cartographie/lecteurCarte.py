import xml.etree.ElementTree as ET
import math
from cartographie.cercle import Cercle
from cartographie.polygone import Polygone
from cartographie.rectangle import Rectangle
from zoneAcces import ZoneAcces
from cartographie.zoneEvitement import ZoneEvitement
from cartographie.pointInteret import PointInteret


class LecteurCarte:
    distanceEvitement = 0

    def __init__(self,fichier, largeurRobot):
        self.fichier = fichier
        self.tree = ET.parse(fichier)
        self.distanceEvitement = largeurRobot

    def getTaille(self):
        return [self.tree.getroot().get("largeur"),self.tree.getroot().get("hauteur")]

    def getFond(self):
        if "fond" in self.tree.getroot().attrib:
            return self.tree.getroot().get("fond")
        else:
            return ""

    def lire(self):
        root = self.tree.getroot()
        listePointInteret = []

        if root.tag == "carte":
            for child in root:
                if child.tag == "PointInteret":
                    listePointInteret.append(self.__getPointInteret(child))
        return listePointInteret

    def __getPointInteret(self,pointInteret):
        nom = pointInteret.get("nom")
        type = pointInteret.get("type")
        couleur = pointInteret.get("couleur")
        valeur = pointInteret.get("valeur")
        action = pointInteret.get("action")
        forme = None
        zoneAcces = None
        zoneEvitement = None
        for noeud in pointInteret:
            if noeud.tag == "forme":
                for _forme in noeud:
                    forme = self.getForme(nom,_forme,couleur)
            elif noeud.tag == "zoneAcces":
                for _zoneAcces in noeud:
                    zoneAcces = ZoneAcces(self.getForme("",_zoneAcces,"white"),float(noeud.get("angle")))
            elif noeud.tag == "zoneEvitement":
                for _zoneEvitement in noeud:
                    zoneEvitement = ZoneEvitement(self.getForme("",_zoneEvitement,"red"))
        if zoneEvitement == None:
            zoneEvitement = self.createZoneEvitement(forme)
        return PointInteret(nom,forme,zoneAcces,zoneEvitement,valeur,action,type,couleur)


    def getForme(self,nom,forme,couleur):
        if forme.tag == "cercle":
            x=int(forme.get("x"))
            y=int(forme.get("y"))
            rayon=int(forme.get("rayon"))
            return Cercle(nom,x,y,rayon,couleur)
        elif forme.tag == "rectangle":
            x1=int(forme.get("x1"))
            y1=int(forme.get("y1"))
            x2=int(forme.get("x2"))
            y2=int(forme.get("y2"))
            return Rectangle(nom,x1,y1,x2,y2,couleur)
        elif forme.tag == "polygone":
            polygone = Polygone(nom, couleur)
            for point in forme:
                polygone.addPoint(float(point.get("x")), float(point.get("y")))
            return polygone

    def createZoneEvitement(self,forme):
        if isinstance(forme, Cercle):
            rayon = forme.rayon + self.distanceEvitement
            return ZoneEvitement(Cercle("",forme.x,forme.y,rayon,"red"))
        elif isinstance(forme, Rectangle):
            x1 = forme.x1 - self.distanceEvitement
            x2 = forme.x2 + self.distanceEvitement
            y1 = forme.y1 - self.distanceEvitement
            y2 = forme.y2 + self.distanceEvitement
            return ZoneEvitement(Rectangle("",x1,y1,x2,y2,"red"))
        elif isinstance(forme, Polygone):
            return self.createEvitementPolygone(forme)

    def createEvitementPolygone(self, forme):
        polygone = Polygone("", "red")
        precision = 5
        newPoints=[]
        #Creation des contour: eloignement des cotes
        for i in range(0, len(forme.pointList)):
            if i>0:
                lastPoint = forme.pointList[i-1]
            else:
                lastPoint = forme.pointList[len(forme.pointList)-1]
            point = forme.pointList[i]
            lx = float(lastPoint["x"])
            ly = float(lastPoint["y"])
            x = float(point["x"])
            y = float(point["y"])
            dx = x-lx
            dy = y-ly
            dist = math.sqrt(pow(dx, 2) + pow(dy, 2))
            newDist = self.distanceEvitement
            dx *= -1
            ax = lx + (newDist / dist) * dy
            ay = ly + (newDist / dist) * dx
            bx = x + (newDist / dist) * dy
            by = y + (newDist / dist) * dx
            newPoints.append([ax, ay])
            newPoints.append([bx, by])
        #Creation des contours des coins
        for i in range(0, len(newPoints), 2):
            if i>0:
                lastPoint = newPoints[i-1]
            else:
                lastPoint = newPoints[len(newPoints)-1]
            polyPoint = forme.pointList[i/2-1]
            px = float(polyPoint["x"])
            py = float(polyPoint["y"])
            point = newPoints[i]
            lx = float(lastPoint[0])
            ly = float(lastPoint[1])
            x = float(point[0])
            y = float(point[1])
            polygone.addPoint(lx, ly)
            for p in range(1, precision+1):
                f1=(1.0/float(precision+1))*(p)
                f2=1 - f1
                cx = (lx*f2 + x*f1) - px
                cy = (ly*f2 + y*f1) - py
                dist = math.sqrt(pow(cx, 2) + pow(cy, 2))
                newDist = self.distanceEvitement
                cx = (newDist / dist) * cx
                cy = (newDist / dist) * cy
                cx += px
                cy += py
                polygone.addPoint(cx, cy)
            polygone.addPoint(x, y)
        return ZoneEvitement(polygone)