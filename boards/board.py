import time
import serial.tools.list_ports
from boards.communicationSerial import CommunicationSerial
from boards.communicationI2C import CommunicationI2C
from webInterface.interface import RunningState
import webInterface


class Board:

    serialConnectionList = []
    baudrate = 115200
    adresse = 0x00

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        self.nom = nom
        self.fonction = fonction
        self.communication = communication
        self.connection = None
        self.param1 = param1
        self.param2 = param2
        if communication == "serial":
            Board.baudrate = param1
            self.connection = CommunicationSerial(self.param1)
        if communication == "i2c":
            Board.adresse = param1
            self.connection = CommunicationI2C(self.nom, self.param1)

    def connect(self):
        if self.communication == "serial":
            if len(Board.serialConnectionList) == 0:
                Board.updateSerialConnectionList()
            ports = serial.tools.list_ports.comports()
            for device in Board.serialConnectionList:
                if device[0] == self.nom:
                    self.connection = device[1]
                    print(self.nom + " connected")
                    return True
        if self.communication == "i2c":
            return self.connection.connect()
        return False

    def getId(self):
        if self.isConnected():
            self.sendMessage("id\r\n")
            echo = ""
            echo = self.receiveMessage()
            if "ERROR" in echo:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry getId("+echo+")"
                return self.getId()
            return echo

    def disconnect(self):
        return self.connection.disconnect()

    def isConnected(self):
        if self.connection:
            return self.connection.isConnected()
        return False

    def sendMessage(self, message):
        result = self.connection.sendMessage(message)
        #print "\t \t ----> ("+self.nom+") " + message
        return result


    def isMessageAvailable(self):
        return self.connection.isMessageAvailable()

    def receiveMessage(self, timeout=1):
        msg = self.connection.receiveMessage(timeout)
        #print "\t \t <---- " + msg + "("+self.nom+")"
        return msg

    @staticmethod
    def updateSerialConnectionList():
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if all(s not in port[0] for s in ("ttyUSB", "usbmodem", "usbserial", "COM")):
                continue

            print port
            connection = CommunicationSerial(Board.baudrate)
            found = False
            if connection.connect(port[0],Board.baudrate, 2):
                time.sleep(2.5)  # giving 2s to initiate the connection
                testCount = 0
                while testCount < 5 and not connection.isMessageAvailable():
                    if webInterface.instance and webInterface.instance.runningState == RunningState.STOP:
                        return
                    testCount += 1
                    print "test", testCount
                    connection.sendMessage("id\r\n")
                    id = connection.receiveMessage(1)
                    if id != "" and not "ERROR" in id:
                        print("Found " + id + " on " + port[0])
                        Board.serialConnectionList.append([id, connection])
                        found = True
                        break
                    else:
                        print "No answer..."
            if not found:
                connection.disconnect()
