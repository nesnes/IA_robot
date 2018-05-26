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
                print "retry grabCube("+ack+")"
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
                print "retry setFindCubePosition("+ack+")"
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
                print "retry setDefaultPosition("+ack+")"
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
                print "retry openTower("+ack+")"
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
                print "retry closeTower("+ack+")"
                return self.closeTower()
            return True
        return False

    def addGolden1(self):
        if self.isConnected():
            self.sendMessage("arm add golden 1\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage(5)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.5)
                print "retry addGolden1("+ack+")"
                return self.addGolden1()
            return True
        return False

    def addGolden2(self):
        if self.isConnected():
            self.sendMessage("arm add golden 2\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage(5)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.5)
                print "retry addGolden2("+ack+")"
                return self.addGolden2()
            return True
        return False

    def openBall(self):
        if self.isConnected():
            self.sendMessage("arm ball open\r\n")
            time.sleep(0.3)
            ack = self.receiveMessage(5)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry openBall("+ack+")"
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
                print "retry openBallRetract("+ack+")"
                return self.openBallRetract()
            return True
        return False

    def pushInterrupteur(self):
        if self.isConnected():
            self.sendMessage("arm inter push\r\n")
            time.sleep(1.2)
            ack = self.receiveMessage(3)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry pushInterrupteur("+ack+")"
                return self.pushInterrupteur()
            return True
        return False

    def abeillePrepare(self):
        if self.isConnected():
            self.sendMessage("arm abeille prepare\r\n")
            time.sleep(1)
            ack = self.receiveMessage(3)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry abeillePrepare("+ack+")"
                return self.abeillePrepare()
            return True
        return False

    def abeillePrepareGreen(self):
        if self.isConnected():
            self.sendMessage("arm abeille pregreen\r\n")
            time.sleep(1)
            ack = self.receiveMessage(3)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry abeillePrepareGreen("+ack+")"
                return self.abeillePrepareGreen()
            return True
        return False

    def abeilleFinal(self):
        if self.isConnected():
            self.sendMessage("arm abeille final\r\n")
            time.sleep(1)
            ack = self.receiveMessage(3)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry abeilleFinal("+ack+")"
                return self.abeilleFinal()
            return True
        return False

    def abeilleFinalGreen(self):
        if self.isConnected():
            self.sendMessage("arm abeille fingreen\r\n")
            time.sleep(1)
            ack = self.receiveMessage(3)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry abeilleFinalGreen("+ack+")"
                return self.abeilleFinalGreen()
            return True
        return False

    def abeilleClose(self):
        if self.isConnected():
            self.sendMessage("arm abeille close\r\n")
            time.sleep(1.3)
            ack = self.receiveMessage(3)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry abeilleClose("+ack+")"
                return self.abeilleClose()
            return True
        return False

    def distributeurPrepare(self):
        if self.isConnected():
            self.sendMessage("arm distributeur prepare\r\n")
            time.sleep(0.5)
            ack = self.receiveMessage(3)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry distributeurPrepare("+ack+")"
                return self.distributeurPrepare()
            return True
        return False

    def distributeurFinal(self):
        if self.isConnected():
            self.sendMessage("arm distributeur final\r\n")
            time.sleep(0.5)
            ack = self.receiveMessage(3)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry distributeurFinal("+ack+")"
                return self.distributeurFinal()
            return True
        return False
