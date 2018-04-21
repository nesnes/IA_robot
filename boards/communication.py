import abc
import time

class Communication:
    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        self.name = name
        self.connected = False
        self.pendingMessageList = []

    @abc.abstractmethod
    def disconnect(self):
        raise NotImplementedError("Please Implement this method")

    @abc.abstractmethod
    def sendMessage(self, message):
        raise NotImplementedError("Please Implement this method")

    def receiveMessage(self, maxTime):
        timeout = 0
        while not self.isMessageAvailable() and timeout < maxTime:
            timeout += 0.1
            time.sleep(0.1)
        if self.isMessageAvailable():
            return self.__getFirstPendingMessage()
        return ""

    def isConnected(self):
        return self.connected

    def isMessageAvailable(self):
        return len(self.pendingMessageList)

    def addPendingMessage(self, message):
        self.pendingMessageList.append(message)

    def __getFirstPendingMessage(self):
        return self.pendingMessageList.pop(0)
