from boards.board import Board


class ControlPanel(Board):

    def __init__(self, nom, fonction, communication):
        Board.__init__(self, nom, fonction, communication)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication

    def getColor(self):
        if self.isConnected():
            self.sendMessage(">color get\r\n")
            color = ""
            while not color.__contains__("color"):
                color = self.receiveMessage() #"color 0" or "color 1"
            return color

    def getStartSignal(self):
        if self.isConnected():
            self.sendMessage(">start get\r\n")
            start = ""
            while not start.__contains__("start"):
                start = self.receiveMessage() #"start 1" or "start 0"
            if start.__contains__("1"):
                return True
        return False
