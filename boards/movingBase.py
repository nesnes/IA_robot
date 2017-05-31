from boards.board import Board

class MovingBase(Board):

    def __init__(self, nom, fonction, communication):
        Board.__init__(self, nom, fonction, communication)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication
        self.isXYSupported = self.__getXYSupport()

    def enableMovements(self):
        if self.isConnected():
            self.sendMessage("move enable\r\n")
            echo = ""
            while "move OK" not in echo:
                echo = self.receiveMessage()  # "move OK"
            return True

    def disableMovements(self):
        if self.isConnected():
            self.sendMessage("move disable\r\n")
            echo = ""
            while "move OK" not in echo:
                echo = self.receiveMessage()  # "move OK"
            return True

    def setPosition(self, x, y, angle):
        if self.isConnected():
            self.sendMessage("position set "+str(x)+";"+str(y)+";"+str(angle)+"\r\n")
            echo = ""
            while "position OK" not in echo:
                echo = self.receiveMessage() #"position OK"
            return True

    def getPositionXY(self):
        if self.isConnected():
            self.sendMessage("position getXY\r\n")
            position = ""
            while "position" not in position:
                position = self.receiveMessage() #"position x;y;angle;speed"
            values = position.split(" ")[1].split(";")
            x = float(values[0])
            y = float(values[1])
            angle = float(values[2])
            speed = float(values[3])
            return x, y, angle, speed

    def getPositionDistanceAngle(self):
        if self.isConnected():
            self.sendMessage("position getDA\r\n")
            position = ""
            while "position" not in position:
                position = self.receiveMessage() #"position distance;angle;speed"
            values = position.split(" ")[1].split(";")
            distance = float(values[0])
            angle = float(values[1])
            speed = float(values[2])
            return distance, angle, speed

    def startMovementXY(self, x, y, angle, speed):
        if self.isConnected():
            if self.isXYSupported:
                self.sendMessage("move setXY " + str(x) + ";" + str(y) + ";" + str(angle) + ";" + str(speed) + "\r\n")
                echo = ""
                while "move OK" not in echo:
                    echo = self.receiveMessage()  # "move OK"
                return True
            else:
                print("ERROR: XY move not supported")
                return False

    def startMovementDistanceAngle(self, distance, angle, speed):
        if self.isConnected():
            self.sendMessage("move setDA " + str(distance) + ";" + str(angle) + ";" + str(speed) + "\r\n")
            echo = ""
            while "move OK" not in echo:
                echo = self.receiveMessage()  # "move OK"
            return True

    def getMovementStatus(self):
        if self.isConnected():
            self.sendMessage("move status\r\n")
            status = ""
            while "move" not in status:
                status = self.receiveMessage()  # "move running" "move stuck" "move finished"
            return status.split(" ")[1]

    def getSpeed(self):
        if self.isConnected():
            self.sendMessage("speed get\r\n")
            speed = ""
            while "speed" not in speed:
                speed = self.receiveMessage()  # "speed 0.3"
            value = float(speed.split(" ")[1])
            return value

    def emergencyBreak(self):
        if self.isConnected():
            self.sendMessage("move break\r\n")
            echo = ""
            while "move OK" not in echo:
                echo = self.receiveMessage()  # "move OK"
            return True

    def startRepositioningMovement(self, distance, speed=0.2): #recallage. Movement where the robot is expected to be stuck
        if self.isConnected():
            self.sendMessage("move setRM " + str(distance) + ";" + str(speed) + "\r\n")
            echo = ""
            while "move OK" not in echo:
                echo = self.receiveMessage()  # "move OK"
            return True

    def __getXYSupport(self):
        if self.isConnected():
            self.sendMessage("support XY\r\n")
            support = ""
            while "support" not in support:
                support = self.receiveMessage()  # "support 0" or "support 1"
            if "1" in support:
                return True
            return False
