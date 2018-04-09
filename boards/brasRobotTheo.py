from boards.board import Board
import time


class BrasRobotTheo(Board):

    def __init__(self, nom, fonction, communication):
        Board.__init__(self, nom, fonction, communication)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication

    def grabCube(self, x, y, angle):
        if self.isConnected():
            self.sendMessage("arm grab {} {} {}\r\n".format(x,y,angle))
            return 1
        return 0

    def setFindCubePosition(self):
        if self.isConnected():
            self.sendMessage("arm find cube\r\n")
            time.sleep(0.3)
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
