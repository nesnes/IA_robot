import time
import serial.tools.list_ports
from boards.communicationSerial import CommunicationSerial


class Board:

    serialConnectionList = []
    baudrate = 115200

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
        return False

    def disconnect(self):
        return self.connection.disconnect()

    def isConnected(self):
        return self.connection.isConnected()

    def sendMessage(self, message):
        return self.connection.sendMessage(message)

    def isMessageAvailable(self):
        return self.connection.isMessageAvailable()

    def receiveMessage(self, timeout=1):
        return self.connection.receiveMessage(timeout)

    @staticmethod
    def updateSerialConnectionList():
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if all(s not in port[0] for s in ("tty", "usbmodem", "usbserial", "COM")):
                continue
            connection = CommunicationSerial(Board.baudrate)
            found = False
            if connection.connect(port[0],Board.baudrate):
                time.sleep(2.5)  # giving 2s to initiate the connection (that's a lot!)
                connection.sendMessage("id\r\n")
                time.sleep(0.5)  # giving 500ms to answer (that's a lot too!)
                while connection.isMessageAvailable():
                    id = connection.receiveMessage(1)
                    print("Found " + id + " on " + port[0])
                    Board.serialConnectionList.append([id, connection])
                    found = True
            if not found:
                connection.disconnect()
