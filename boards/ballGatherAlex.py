from boards.board import Board
import time

class BallGatherAlex(Board):

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        Board.__init__(self, nom, fonction, communication, param1, param2)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication

    def getColor(self):
        if self.isConnected():
            self.sendMessage("ball color get\r\n")
            color = self.receiveMessage()  # "ball color 0" or "ball color 1"
            if "color" not in color:
                time.sleep(0.1)
                print "retry getColor("+color+")"
                return self.getColor()
            if "1" in color:
                return 1
            if "2" in color:
                return 2
            if "3" in color:
                return 3
            return 0

    def getTrapColor(self):
        if self.isConnected():
            self.sendMessage("trap color get\r\n")
            color = self.receiveMessage()  # "ball color 0" or "ball color 1"
            if "color" not in color:
                time.sleep(0.1)
                print "retry getTrapColor("+color+")"
                return self.getTrapColor()
            if "1" in color:
                return 1
            if "2" in color:
                return 2
            if "3" in color:
                return 3
            return 0

    def getCannonColor(self):
        if self.isConnected():
            self.sendMessage("cannon color get\r\n")
            color = self.receiveMessage()  # "ball color 0" or "ball color 1"
            if "color" not in color:
                time.sleep(0.1)
                print "retry getCannonColor("+color+")"
                return self.getCannonColor()
            if "1" in color:
                return 1
            if "2" in color:
                return 2
            if "3" in color:
                return 3
            return 0

    def getGatherColor(self):
        if self.isConnected():
            self.sendMessage("gather color get\r\n")
            color = self.receiveMessage()  # "ball color 0" or "ball color 1"
            if "color" not in color:
                time.sleep(0.1)
                print "retry getGatherColor("+color+")"
                return self.getGatherColor()
            if "1" in color:
                return 1
            if "2" in color:
                return 2
            if "3" in color:
                return 3
            return 0

    def bacOpen(self):
        if self.isConnected():
            self.sendMessage("bac open\r\n")
            ack = self.receiveMessage()  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry bacOpen("+ack+")"
                return self.bacOpen()
            return True
        return False

    def bacEmpty(self):
        if self.isConnected():
            self.sendMessage("bac empty\r\n")
            ack = self.receiveMessage()  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry bacEmpty("+ack+")"
                return self.bacEmpty()
            return True
        return False

    def bacGather(self):
        if self.isConnected():
            self.sendMessage("bac gather\r\n")
            time.sleep(1)
            ack = self.receiveMessage()  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry bacGather("+ack+")"
                return self.bacGather()
            return True
        return False

    def bacClose(self):
        if self.isConnected():
            self.sendMessage("bac close\r\n")
            ack = self.receiveMessage()  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry bacClose("+ack+")"
                return self.bacClose()
            return True
        return False

    def trapOpen(self):
        if self.isConnected():
            self.sendMessage("trap open\r\n")
            ack = self.receiveMessage()  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry trapOpen("+ack+")"
                return self.trapOpen()
            return True
        return False

    def trapClose(self):
        if self.isConnected():
            self.sendMessage("trap close\r\n")
            ack = self.receiveMessage()  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry trapClose("+ack+")"
                return self.trapClose()
            return True
        return False

    def cannonOpen(self):
        if self.isConnected():
            self.sendMessage("cannon open\r\n")
            ack = self.receiveMessage()  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry cannonOpen("+ack+")"
                return self.cannonOpen()
            return True
        return False

    def cannonClose(self):
        if self.isConnected():
            self.sendMessage("cannon close\r\n")
            ack = self.receiveMessage()  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry cannonClose("+ack+")"
                return self.cannonOpen()
            return True
        return False

    def setCannonSpeed(self, speed):
        if self.isConnected():
            self.sendMessage("cannon speed {}\r\n".format(speed))
            ack = self.receiveMessage()  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry setCannonSpeed("+ack+")"
                return self.setCannonSpeed(speed)
            if speed > 0:
                time.sleep(0.5)
            return True
        return False

    def stepperSlot(self):
        if self.isConnected():
            self.sendMessage("stepper slot\r\n")
            ack = self.receiveMessage(3)  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry stepperSlot("+ack+")"
                return self.stepperSlot()
            return True
        return False

    def stepperGather(self):
        if self.isConnected():
            self.sendMessage("stepper gather\r\n")
            ack = self.receiveMessage(4)  # "OK"
            if "OK" not in ack:
                time.sleep(0.1)
                print "retry stepperGather("+ack+")"
                return self.stepperGather()
            return True
        return False
