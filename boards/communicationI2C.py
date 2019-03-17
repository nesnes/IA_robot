import os
isRaspberry = "arm" in os.popen("uname -m").read()
if isRaspberry:
    from smbus import SMBus
import threading
import time
from boards.communication import Communication
#from communication import Communication


class CommunicationI2C(Communication):

    def __init__(self, name="i2c", address="0x00"):
        Communication.__init__(self, name)
        self.bus = None
        self.address = int(address, 16)
        self.timeout = 0.2
        self.stopThread = False
        self.rwMutex = threading.Lock()
        
        
    def connect(self, address=0x00, timeout=0.2):
        try:
            if address is 0x00:
                address = self.address
            else:
                self.address = address
            self.timeout = timeout
            print "opening i2c ", self.address
            self.bus = SMBus(1)
            self.rwMutex.acquire()
            try:
                self.bus.read_byte(self.address)
                self.connected = True
            except:
                self.connected = False
            self.rwMutex.release()
            print "connected", self.connected
            self.thread = threading.Thread(target=self.__receiveLoop)
            self.thread.start()
            return self.connected
        except:
            # e = sys.exc_info()[0]
            # print e
            return False

    def disconnect(self):
        if self.bus is None:
            return
        self.stopThread = True
        self.thread.join()
        self.connected = False

    def sendMessage(self, message):
        while len(self.pendingMessageList): #empty receive list
            self.pendingMessageList.pop(0)
        if self.bus is None or not self.connected:
            print "send message, not connected"
            return
        
        if len(message) > 30:
            print "Too long(",len(message),") ", message
            return
        
        #print "sending: ", message
        self.rwMutex.acquire()
        #print self.name, "Locked W"
        try:
            #print self.name, "try W"
            self.bus.write_i2c_block_data(self.address, 68, map(ord, message))
            #print self.name, "wrote"
            time.sleep(0.01)
            #print self.name, ">", message
        except:
            print "Write failed on ", self.address
            self.rwMutex.release()
            self.disconnect()
            self.connect(self.address, 1)
            if self.connected:
                print "reconnected ", self.address
        else:
            #print self.name, "About Unlocked W"
            self.rwMutex.release()
            #print self.name, "Unlocked W"

    def __receiveLoop(self):
        errorDetected = False
        while self.bus is not None and self.connected and not self.stopThread:
            time.sleep(0.015)
            message = ""
            self.rwMutex.acquire()
            try:
                message = self.bus.read_i2c_block_data(self.address, 0, 30)
                time.sleep(0.005)
                message = "".join(map(chr, message))
                if "\r\n" not in message:
                    message = ""
                message = message.replace('\r\n', '')
                message = message.replace(chr(255), '')
                message = message.replace(chr(0), '')
            except Exception as e:
                errorDetected = True
            self.rwMutex.release()
            if message and len(message)>0:
                self.addPendingMessage(message)
                #print self.name, "<", message
        if errorDetected and not self.stopThread:
            print "recv reconnecting ", self.address
            self.connect(self.address, self.timeout)

if __name__ == '__main__':
    com1 = CommunicationI2C("test_bras ", "0x06")
    com1.connect()
    i=0
    while i<5:
        com1.sendMessage("arm default L\r\n")
        com1.receiveMessage(1)
        com1.sendMessage("arm default M\r\n")
        com1.receiveMessage(1)
        com1.sendMessage("arm default R\r\n")
        com1.receiveMessage(1)
        com1.sendMessage("arm wallGrab L\r\n")
        com1.receiveMessage(1)
        com1.sendMessage("arm wallGrab M\r\n")
        com1.receiveMessage(1)
        com1.sendMessage("arm wallGrab R\r\n")
        com1.receiveMessage(1)
        time.sleep(0.5)
        i+=1
    com1.disconnect()
