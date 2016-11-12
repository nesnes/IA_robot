import xml.etree.ElementTree as ET
from intelligence.robot import Robot
from intelligence.variable import Variable
from intelligence.position import Position
from intelligence.telemetre import Telemetre

class LecteurRobot:

    def __init__(self, fichier):
        self.fichier = fichier
        self.tree = ET.parse(fichier)
        self.robot = None
        self.nom = ""
        self.port = ""
        self.rayon = 0

    def lire(self):
        root = self.tree.getroot()

        if root.tag == "robot":
            self.nom = root.get("nom")
            self.rayon = float(root.get("rayon"))
            self.port = root.get("port")
            self.defaultColor = root.get("defaultColor")
            self.robot = Robot(self.nom, self.port, self.rayon)
            self.robot.couleur = self.defaultColor
            for child in root:
                if child.tag == "equipement":
                    self.__getEquipement(child)
                elif child.tag == "position":
                    self.__getPosition(child)
        else:
            print("Error, not a robot description file")
        return self.robot

    def __getEquipement(self, equipement):
        nom = equipement.get("nom")
        type = equipement.get("type")
        if type == "variable":
            valeur = float(equipement.get("valeur"))
            maxVal = float(equipement.get("max"))
            variable = Variable(nom, valeur, maxVal)
            self.robot.listVariables.append(variable)
        if type == "telemetre":
            id = equipement.get("id")
            x = float(equipement.get("x"))
            y = float(equipement.get("y"))
            angle = float(equipement.get("angle"))
            telemetre = Telemetre(nom, id, x, y, angle)
            self.robot.listTelemetre.append(telemetre)

    def __getPosition(self, position):
        nom = position.get("nom")
        couleur = position.get("couleur")
        x = float(position.get("x"))
        y = float(position.get("y"))
        angle = float(position.get("angle"))
        newPosition = Position(nom, couleur, x, y, angle)
        self.robot.listPosition.append(newPosition)

