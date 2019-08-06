from boards.board import Board
import time


class BrasRobotTheo(Board):

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        Board.__init__(self, nom, fonction, communication, param1, param2)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication
        

    def armSetServo(self, side, servo, angle):
        if self.isConnected():
            self.sendMessage("setArmServo {} {} {}\r\n".format(side, servo, angle))
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armSetServo("+ack+")"
                return self.armSetServo(side, servo, angle)
            return True
        return False
        

    def armGetServos(self, side):
        if self.isConnected():
            self.sendMessage("getServos {}\r\n".format(side))
            ack = self.receiveMessage()
            print ack
            return True
        return False

    def pumpOn(self, side):
        if self.isConnected():
            self.sendMessage("pump on {}\r\n".format(side))
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry pumpOn("+ack+")"
                return self.pumpOn(side)
            return True
        return False

    def pumpOff(self, side):
        if self.isConnected():
            self.sendMessage("pump off {}\r\n".format(side))
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry pumpOff("+ack+")"
                return self.pumpOff(side)
            return True
        return False

    def enableAutoGrab(self):
        if self.isConnected():
            self.sendMessage("arm enableAutoGrab\r\n")
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry enableAutoGrab("+ack+")"
                return self.enableAutoGrab()
            return True
        return False

    def disableAutoGrab(self):
        if self.isConnected():
            self.sendMessage("arm disableAutoGrab\r\n")
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry disableAutoGrab("+ack+")"
                return self.disableAutoGrab()
            return True
        return False

    def armDefault(self, side):
        if self.isConnected():
            self.sendMessage("arm default {}\r\n".format(side))
            time.sleep(0.3)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armDefault("+ack+")"
                return self.armDefault(side)
            return True
        return False

    def armWallGrab(self, side):
        if self.isConnected():
            self.sendMessage("arm wallGrab {}\r\n".format(side))
            time.sleep(0.3)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armWallGrab("+ack+")"
                return self.armWallGrab(side)
            return True
        return False

    def armThrow(self, side):
        if self.isConnected():
            self.sendMessage("arm throw {}\r\n".format(side))
            time.sleep(0.3)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry throw("+ack+")"
                return self.armThrow(side)
            return True
        return False

    def armFloorGrabPrepare(self, side):
        if self.isConnected():
            self.sendMessage("arm floorGrabPrepare {}\r\n".format(side))
            time.sleep(0.3)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armFloorGrabPrepare("+ack+")"
                return self.armFloorGrabPrepare(side)
            return True
        return False

    def armFloorGrab(self, side):
        if self.isConnected():
            self.sendMessage("arm floorGrab {}\r\n".format(side))
            time.sleep(0.3)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armFloorGrab("+ack+")"
                return self.armFloorGrab(side)
            return True
        return False

    def armWallDeposit(self, side):
        if self.isConnected():
            self.sendMessage("arm wallDeposit {}\r\n".format(side))
            time.sleep(0.3)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armWallDeposit("+ack+")"
                return self.armWallDeposit(side)
            return True
        return False

    def armWallDepositLow(self, side):
        if self.isConnected():
            self.sendMessage("arm wallDepositLow {}\r\n".format(side))
            time.sleep(0.3)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armWallDepositLow("+ack+")"
                return self.armWallDepositLow(side)
            return True
        return False


    def armDepositPrepare(self, side):
        if self.isConnected():
            self.sendMessage("arm stockDepositPrepare {}\r\n".format(side))
            time.sleep(1)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armDepositPrepare("+ack+")"
                return self.armDepositPrepare(side)
            return True
        return False

    def armStock(self, side, index):
        if self.isConnected() and index>0 and index <4:
            self.sendMessage("arm stock{} {}\r\n".format(int(index), side))
            print("arm stock{} {}\r\n".format(int(index), side))
            time.sleep(0.5)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armStock("+ack+")"
                return self.armStock(side, index)
            return True
        return False

    