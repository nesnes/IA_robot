from boards.board import Board


class BallGatherAlex(Board):

    def __init__(self, nom, fonction, communication):
        Board.__init__(self, nom, fonction, communication)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication

    def getColor(self):
        if self.isConnected():
            self.sendMessage("color get\r\n")
            color = ""
            while "color" not in color:
                color = self.receiveMessage()  # "color 0" or "color 1"
                if "1" in color:
                    return 1
            return 0

    def getStartSignal(self):
        if self.isConnected():
            self.sendMessage("start get\r\n")
            start = ""
            while "start" not in start:
                start = self.receiveMessage()  # "start 1" or "start 0"
            if "1" in start:
                return True
        return False

    def setScore(self, score):
        if self.isConnected():
            self.sendMessage("score set" + str(score) + "\r\n")
            return True
        return False

    def displayMessage(self, message):
        if self.isConnected():
            self.sendMessage("#" + str(message) + "\r\n")
            return True
        return False
