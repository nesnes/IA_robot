import glob
import time
import serial.tools.list_ports
from boards.communicationSerial import CommunicationSerial


class Board:

    def __init__(self, nom, fonction, communication):
        self.nom = nom
        self.fonction = fonction
        self.communication = communication
        self.connection = None
        if communication == "serial":
            self.connection = CommunicationSerial()

    def connect(self):
        if self.communication == "serial":
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if not port[0].__contains__("tty") and not port[0].__contains__("usbmodem") and not port[0].__contains__("COM"):
                    continue
                if self.connection.connect(port[0]):
                    self.connection.sendMessage("id\r\n")
                    time.sleep(0.1) #giving 100ms to answer (that's a lot!)
                    while self.connection.isMessageAvailable():
                        id = self.connection.receiveMessage()
                        if id == self.nom:
                            print(self.nom+" connected on port " + port[0])
                            return True
                    self.connection.disconnect()
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