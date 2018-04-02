import abc


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

    def receiveMessage(self):
        while not self.isMessageAvailable():
            pass
        return self.__getFirstPendingMessage()

    def isConnected(self):
        return self.connected

    def isMessageAvailable(self):
        return len(self.pendingMessageList)

    def addPendingMessage(self, message):
        self.pendingMessageList.append(message)

    def __getFirstPendingMessage(self):
        return self.pendingMessageList.pop(0)
