from boards.board import Board
import time

class ControlPanel(Board):

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        Board.__init__(self, nom, fonction, communication, param1, param2)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication

    def getColor(self):
        if self.isConnected():
            self.sendMessage("color get\r\n")
            color = ""
            color = self.receiveMessage()  # "color 0" or "color 1"
            if "color" not in color: #if ERROR is received, retry
                time.sleep(0.1)
                return self.getColor()
            if "1" in color:
                return 1
            return 0

    def getStartSignal(self):
        if self.isConnected():
            self.sendMessage("start get\r\n")
            start = ""
            start = self.receiveMessage()  # "start 1" or "start 0"
            if "start" not in start: #if ERROR is received, retry
                time.sleep(0.1)
                return self.getStartSignal()
            if "1" in start:
                return True
        return False

    def setScore(self, score):
        if self.isConnected():
            self.sendMessage("score set" + str(score) + "\r\n")
            return True
        return False

    def displayMessage(self, message):
        if self.isConnected():
            self.sendMessage("#" + str(message) + "\r\n")
            return True
        return False
