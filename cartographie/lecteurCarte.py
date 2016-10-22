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
            polygone = Polygone("", "red")
            for point in forme.pointList:
                x = float(point["x"]) - forme.x
                y = float(point["y"]) - forme.y
                dist = math.sqrt(pow(x, 2) + pow(y, 2))
                newDist = dist + self.distanceEvitement
                x = (newDist / dist) * x
                y = (newDist / dist) * y
                x += forme.x
                y += forme.y
                polygone.addPoint(x, y)
            return ZoneEvitement(polygone)
