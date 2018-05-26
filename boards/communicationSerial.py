import serial
import threading
import time
from boards.communication import Communication


class CommunicationSerial(Communication):

    def __init__(self, baudrate=115200):
        Communication.__init__(self, "serial")
        self.portserie = None
        self.address = ""
        self.baudrate = baudrate
        self.timeout = 0.2
        if self.portserie == '':
            return

    def connect(self, port, baudrate=None, timeout=0.2):
        try:
            if baudrate is None:
                baudrate = self.baudrate
            else:
                self.baudrate = baudrate
            self.timeout = timeout
            self.portserie = serial.Serial(port, baudrate, timeout=timeout, writeTimeout=timeout)
            self.portserie.flushInput()
            self.portserie.flushOutput()
            self.address = port
            self.connected = self.portserie.isOpen()
            self.thread = threading.Thread(target=self.__receiveLoop)
            self.thread.start()
            return self.connected
        except:
            # e = sys.exc_info()[0]
            # print e
            return False

    def disconnect(self):
        if self.portserie is None:
            return
        self.connected = False
        self.thread.join()
        self.portserie.close()  # Close after join() to avoid Bad File Descriptor error in thread

    def sendMessage(self, message):
        #time.sleep(0.02)
        while len(self.pendingMessageList): #empty receive list
            self.pendingMessageList.pop(0)
        if self.portserie is None or not self.connected:
            print "send message, not connected"
            return
        if self.portserie.isOpen():
            try:
                self.portserie.write(message)
                #print self.name, ">", message
            except:
                print "Write timeout on " + self.address
                self.disconnect()
                self.connect(self.address,self.baudrate, 1)
                if self.connected:
                    print "reconnected " + self.address

        else:
            print "ERREUR: Impossible d'acceder au port serie"

    def __receiveLoop(self):
        while self.portserie is not None and self.connected and self.portserie.isOpen():
            message = ""
            try:
                message = self.portserie.readline()
                message = message.replace('\r\n', '')
                self.portserie.flushInput()  # ?
            except Exception as e:
                pass
            if message:
                self.addPendingMessage(message)
                #print self.name, "<", message
        if not self.portserie.isOpen():
            print "reconnecting " + self.address
            self.portserie.close()
            self.connect(self.portserie, self.baudrate, self.timeout)


