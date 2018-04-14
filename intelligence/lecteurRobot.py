import xml.etree.ElementTree as ET
from intelligence.robot import Robot
from intelligence.variable import Variable
from intelligence.position import Position
from intelligence.telemetre import Telemetre
from boards.board import Board
import boards
import robots


class LecteurRobot:

    def __init__(self, fichier):
        self.fichier = fichier
        self.tree = ET.parse(fichier)
        self.robot = None
        self.nom = ""
        self.port = ""
        self.port2 = ""
        self.rayon = 0
        self.defaultColor = ""
        self.available_boards = {board.__name__.lower(): board for board in boards.__all__}
        self.available_robots = {robot.__name__.lower(): robot for robot in robots.__all__}

    def lire(self):
        root = self.tree.getroot()

        if root.tag == "robot":
            self.nom = root.get("nom")
            self.rayon = float(root.get("rayon"))
            self.port = root.get("port")
            self.port2 = root.get("port2")
            self.defaultColor = root.get("defaultColor")

            # find the requested Robot python class
            robotClass = self.available_robots.get(self.nom.lower(), Robot)  # find a class with the board name else use the default Robot

            self.robot = robotClass(self.nom, self.rayon)
            self.robot.couleur = self.defaultColor
            self.robot.port2 = self.port2
            for child in root:
                if child.tag == "equipement":
                    self.__getEquipement(child)
                elif child.tag == "position":
                    self.__getPosition(child)
                elif child.tag == "board":
                    self.__getBoard(child)
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
            id = int(equipement.get("id"))
            x = float(equipement.get("x"))
            y = float(equipement.get("y"))
            angle = float(equipement.get("angle"))
            min=0
            max=0
            if equipement.get("min") is not None:
                min = float(equipement.get("min"))
            if equipement.get("max") is not None:
                max = float(equipement.get("max"))
            telemetre = Telemetre(nom, id, x, y, angle, min, max)
            self.robot.listTelemetre.append(telemetre)

    def __getPosition(self, position):
        nom = position.get("nom")
        couleur = position.get("couleur")
        x = float(position.get("x"))
        y = float(position.get("y"))
        angle = float(position.get("angle"))
        newPosition = Position(nom, couleur, x, y, angle)
        self.robot.listPosition.append(newPosition)

    def __getBoard(self, board):
        nom = board.get("nom")
        fonction = board.get("fonction")
        communication = board.get("communication")
        baudrate = 115200
        if "serial" in communication:
            if board.get("baudrate"):
                baudrate = board.get("baudrate")

        newBoard = None

        # find a class with the board name
        boardClass = self.available_boards.get(nom.lower())

        if boardClass is None:  # else find a class with the function name else use default board
            boardClass = self.available_boards.get(fonction.lower(), Board)

        print nom, "loaded as", boardClass

        if "serial" in communication:
            newBoard = boardClass(nom, fonction, communication, baudrate)
        else:
            newBoard = boardClass(nom, fonction, communication)
        self.robot.listBoard.append(newBoard)
