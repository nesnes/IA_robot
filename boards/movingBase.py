from boards.board import Board
from boards.board import RetryException
from boards.board import retry
import time


class MovingBase(Board):

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        Board.__init__(self, nom, fonction, communication, param1, param2)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication
        self._isXYSupported = None
        self._isPathSupported = None

    @retry()
    def enableMovements(self):
        if self.isConnected():
            self.sendMessage("move enable")
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo: #if ERROR is received, retry
                raise RetryException
            return True

    @retry()
    def disableMovements(self):
        if self.isConnected():
            self.sendMessage("move disable")
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo: #if ERROR is received, retry
                raise RetryException
            return True

    @retry()
    def setPosition(self, x, y, angle):
        if self.isConnected():
            self.sendMessage("pos set {:.0f} {:.0f} {:.0f}".format(x, y, angle))
            echo = ""
            echo = self.receiveMessage()  # "position OK"
            if "pos OK" not in echo: #if ERROR is received, retry
                raise RetryException
            return True

    @retry()
    def setSpin(self, direction, speed):
        if self.isConnected():
            self.sendMessage("spin {:.0f} {:.0f}".format(direction, speed))
            echo = ""
            echo = self.receiveMessage()  # "spin OK"
            if "spin OK" not in echo: #if ERROR is received, retry
                raise RetryException
            return True

    @retry()
    def getPositionXY(self):
        if self.isConnected():
            self.sendMessage("pos getXY")
            position = ""
            position = self.receiveMessage()  # "position x;y;angle;speed"
            if "pos" not in position: #if ERROR is received, retry
                raise RetryException
            #print position
            values = position.split(" ")
            x = float(values[1])
            y = float(values[2])
            angle = float(values[3])
            speed = float(values[4])/10.0
            return x, y, angle, speed

    @retry()
    def getPositionDistanceAngle(self):
        if self.isConnected():
            self.sendMessage("pos getDA")
            position = ""
            position = self.receiveMessage()  # "position distance;angle;speed"
            if "pos" not in position: #if ERROR is received, retry
                raise RetryException
            values = position.split(" ")
            distance = float(values[1])
            angle = float(values[2])
            speed = float(values[3])/10.0
            return distance, angle, speed

    @retry()
    def startMovementXY(self, x, y, angle, speed):
        if self.isConnected():
            if self.isXYSupported():
                self.sendMessage("move XY {:.0f} {:.0f} {:.0f} {:.0f}".format(x,y,angle,speed*10.0))
                echo = ""
                echo = self.receiveMessage()  # "move OK"
                if "move OK" not in echo:  # if ERROR is received, retry
                    raise RetryException
                return True
            else:
                print("ERROR: XY move not supported")
                return False

    @retry()
    def startMovementDistanceAngle(self, distance, angle, speed):
        if self.isConnected():
            self.sendMessage("move DA {:.0f} {:.0f} {:.0f}".format(distance,angle,speed*10.0))
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo:  # if ERROR is received, retry
                raise RetryException
            return True

    @retry()
    def getMovementStatus(self):
        if self.isConnected():
            self.sendMessage("move status")
            status = ""
            status = self.receiveMessage()  # "move running" "move stuck" "move finished"
            if "move" not in status:  # if ERROR is received, retry
                raise RetryException
            return status.split(" ")[1]

    @retry()
    def getSpeed(self):
        if self.isConnected():
            self.sendMessage("speed get")
            speed = ""
            speed = self.receiveMessage()  # "speed 0.3"
            if "speed" not in speed:  # if ERROR is received, retry
                raise RetryException
            value = float(speed.split(" ")[1])/10.0
            return value

    @retry()
    def emergencyBreak(self):
        if self.isConnected():
            self.sendMessage("move break")
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo:  # if ERROR is received, retry
                raise RetryException
            return True

    @retry()
    def startRepositioningMovement(self, distance, speed=0.2):  # recallage. Movement where the robot is expected to be stuck
        if self.isConnected():
            self.sendMessage("move RM {:.0f} {:.0f}".format(distance,speed*10))
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo:  # if ERROR is received, retry
                raise RetryException
            return True

    @retry()
    def isXYSupported(self):
        if self._isXYSupported is None and self.isConnected():
            self._isXYSupported = False
            self.sendMessage("support XY")
            support = ""
            support = self.receiveMessage()  # "support 0" or "support 1"
            if "support" not in support:  # if ERROR is received, retry
                raise RetryException
            if "1" in support:
                self._isXYSupported = True
        return self._isXYSupported

    @retry()
    def isPathSupported(self):
        if self._isPathSupported is None and self.isConnected():
            self._isPathSupported = False
            self.sendMessage("support Path")
            support = ""
            support = self.receiveMessage()  # "support 0" or "support 1"
            if "support" not in support:  # if ERROR is received, retry
                raise RetryException
            if "1" in support:
                self._isPathSupported = True
        return self._isPathSupported

    @retry()
    def startMovementPath(self, pathArray):
        if self.isConnected():
            if self.isPathSupported():
                command = "move setPath {}|".format(len(pathArray))
                for move in pathArray:
                    command += "{};{};{};{}|".format(move.x,move.y,move.angle, move.speed)
                self.sendMessage(command)
                echo = ""
                echo = self.receiveMessage()  # "move OK"
                if "move OK" not in echo:  # if ERROR is received, retry
                    raise RetryException
                return True
            else:
                print("ERROR: XY move not supported")
                return False