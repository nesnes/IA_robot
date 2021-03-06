import time
import serial.tools.list_ports
from webInterface.interface import RunningState
import webInterface
from functools import wraps
import time


class RetryException(Exception):
    pass


def retry(tries=3, delay=0.5):
    """Retry calling the decorated function using an exponential backoff.
    :param tries: number of times to try (not retry) before giving up
    :param delay: initial delay between retries in seconds
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except RetryException, e:
                    print("{}, retry {}/{} in {} seconds...".format(f.__name__, tries-mtries+1, tries, mdelay))
                    time.sleep(mdelay)
                    mtries -= 1
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


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
        if webInterface.instance and webInterface.instance.runningParameters.robotConnected:
            if communication == "serial":
                from boards.communicationSerial import CommunicationSerial
                Board.baudrate = param1
                self.connection = CommunicationSerial(self.param1)
            if communication == "i2c":
                from boards.communicationI2C import CommunicationI2C
                Board.adresse = param1
                self.connection = CommunicationI2C(self.nom, self.param1)
            if communication == "lidarX2":
                from boards.lidarX2 import LidarX2
                self.connection = LidarX2(self.param1)

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
        if self.communication == "lidarX2":
            return self.connection.connect()
        return False

    def getId(self):
        if self.isConnected():
            self.sendMessage("id")
            echo = ""
            echo = self.receiveMessage()
            if "ERROR" in echo:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry getId("+echo+")"
                return self.getId()
            print echo
            return echo

    def disconnect(self):
        if self.connection:
            return self.connection.disconnect()
        return True

    def isConnected(self):
        if self.connection:
            return self.connection.isConnected()
        return False

    def sendMessage(self, message):
        result = False
        if self.connection:
            result = self.connection.sendMessage(message)
        #print "\t \t ----> ("+self.nom+") " + message
        return result


    def isMessageAvailable(self):
        if self.connection:
            return self.connection.isMessageAvailable()
        return False

    def receiveMessage(self, timeout=1):
        msg = ""
        if self.connection:
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
