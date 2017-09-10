import glob
import time
import serial.tools.list_ports
from boards.communicationSerial import CommunicationSerial


class Board:

    serialConnectionList = []

    def __init__(self, nom, fonction, communication):
        self.nom = nom
        self.fonction = fonction
        self.communication = communication
        self.connection = None
        if communication == "serial":
            self.connection = CommunicationSerial()

    def connect(self):
        if self.communication == "serial":
            if len(Board.serialConnectionList) == 0:
                Board.updateSerialConnectionList()
            ports = serial.tools.list_ports.comports()
            for device in Board.serialConnectionList:
                if device[0] == self.nom:
                    self.connection = device[1]
                    print(self.nom+" connected")
                    return True
        return False


    def disconnect(self):
        return self.connection.disconnect()

    def isConnected(self):
        return self.connection.isConnected()

    def sendMessage(self, message):
        return self.connection.sendMessage(message)

    def isMessageAvailable(self):
        return self.connection.isMessageAvailable()

    def receiveMessage(self):
        return self.connection.receiveMessage()

    @staticmethod
    def updateSerialConnectionList():
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if all(s not in port[0] for s in ("tty", "usbmodem", "usbserial", "COM")):
                continue
            connection = CommunicationSerial()
            found = False
            if connection.connect(port[0]):
                time.sleep(2)  # giving 2s to initiate the connection (that's a lot!)
                connection.sendMessage("id\r\n")
                time.sleep(0.2)  # giving 200ms to answer (that's a lot too!)
                while connection.isMessageAvailable():
                    id = connection.receiveMessage()
                    print("Found " + id + " on " + port[0])
                    Board.serialConnectionList.append([id, connection])
                    found = True
            if not found:
                connection.disconnect()