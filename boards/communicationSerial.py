import serial
import threading
from boards.communication import Communication
class CommunicationSerial(Communication):

    def __init__(self):
        Communication.__init__(self, "serial")
        self.portserie = None
        self.address = ""
        if self.portserie == '':
            return

    def connect(self, port, baudrate=115200, timeout=0.2):
        try:
            self.portserie = serial.Serial(port, baudrate, timeout=timeout)
            self.portserie.flushInput()
            self.portserie.flushOutput()
            self.address = port
            self.connected = self.portserie.isOpen()
            self.thread = threading.Thread(target=self.__receiveLoop())
            self.thread.start()
            return self.connected
        except:
            return False

    def disconnect(self):
        if self.portserie is None:
            return
        self.portserie.close()
        self.connected = False
        self.thread.join()

    def sendMessage(self,message):
        if self.portserie is None or not self.connected:
            return
        if self.portserie.isOpen():
            self.portserie.write(message)
        else:
            print "ERREUR: Impossible d'acceder au port serie"

    def __receiveLoop(self):
        while not self.portserie is None and self.connected and self.portserie.isOpen():
            message = self.portserie.readline()
            #self.portserie.flushInput()
            self.__addPendingMessage(message)
