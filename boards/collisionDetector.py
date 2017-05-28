from boards.board import Board
from intelligence.telemetre import Telemetre

class CollisionDetector(Board):

    def __init__(self, nom, fonction, communication):
        Board.__init__(self, nom, fonction, communication)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication

    def updateTelemetre(self, listTelemetre):
        if self.isConnected():
            self.sendMessage("distances get\r\n")
            distances = ""
            while not distances.__contains__("distances"):
                distances = self.receiveMessage() #"distances 0;1.2;0.4"... in the order of the IDs
            listDistances = distances.split(" ")[1].split(";")
            count = 0
            for value in listDistances:
                for telemeter in listTelemetre:
                    if telemeter.id == count:
                        telemeter.setValue(float(listDistances[count]))
                count += 1
            return True
