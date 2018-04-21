from boards.board import Board
import time


class BrasRobotTheo(Board):

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        Board.__init__(self, nom, fonction, communication, param1, param2)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication

    def grabCube(self, x, y, angle):
        if self.isConnected():
            self.sendMessage("arm grab {} {} {}\r\n".format(x,y,angle))
            ack = self.receiveMessage(5)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                return self.grabCube(x, y, angle)
            return True
        return False

    def setFindCubePosition(self):
        if self.isConnected():
            self.sendMessage("arm find cube\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage()
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                return self.setFindCubePosition()
            return True
        return False

    def setDefaultPosition(self):
        if self.isConnected():
            self.sendMessage("arm default\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage()
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                return self.setDefaultPosition()
            return True
        return False

    def openTower(self):
        if self.isConnected():
            self.sendMessage("tower open\r\n")
            time.sleep(0.5)
            ack = self.receiveMessage()
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                return self.openTower()
            return True
        return False

    def closeTower(self):
        if self.isConnected():
            self.sendMessage("tower close\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage()
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                return self.closeTower()
            return True
        return False

    def addGolden1(self):
        if self.isConnected():
            self.sendMessage("arm add golden 1\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage(5)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                return self.addGolden1()
            return True
        return False

    def addGolden2(self):
        if self.isConnected():
            self.sendMessage("arm add golden 2\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage(5)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                return self.addGolden1()
            return True
        return False

    def openBall(self):
        if self.isConnected():
            self.sendMessage("arm ball open\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage(5)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                return self.openBall()
            return True
        return False

    def openBallRetract(self):
        if self.isConnected():
            self.sendMessage("arm ball retract\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage(5)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                return self.openBallRetract()
            return True
        return False
