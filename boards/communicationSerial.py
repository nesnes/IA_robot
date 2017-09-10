import serial
import sys
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
            self.portserie = serial.Serial(port, baudrate, timeout=timeout, writeTimeout=timeout)
            self.portserie.flushInput()
            self.portserie.flushOutput()
            self.address = port
            self.connected = self.portserie.isOpen()
            self.thread = threading.Thread(target=self.__receiveLoop)
            self.thread.start()
            return self.connected
        except:
            #e = sys.exc_info()[0]
            #print e
            return False

    def disconnect(self):
        if self.portserie is None:
            return
        self.connected = False
        self.thread.join()
        self.portserie.close() #Close after join() to avoid Bad File Descriptor error in thread

    def sendMessage(self,message):
        if self.portserie is None or not self.connected:
            return
        if self.portserie.isOpen():
            try:
                self.portserie.write(message)
            except:
                print "Write timeout on " + self.address
        else:
            print "ERREUR: Impossible d'acceder au port serie"

    def __receiveLoop(self):
        while not self.portserie is None and self.connected and self.portserie.isOpen():
            message = self.portserie.readline()
            message = message.replace('\r\n','')
            self.portserie.flushInput() #?
            if message:
                self.addPendingMessage(message)
