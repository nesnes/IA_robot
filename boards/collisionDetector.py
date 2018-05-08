from boards.board import Board
from intelligence.telemetre import Telemetre
import time

class CollisionDetector(Board):

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        Board.__init__(self, nom, fonction, communication, param1, param2)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication

    def updateTelemetre(self, listTelemetre):
        if self.isConnected():
            self.sendMessage("distances get\r\n")
            distances = self.receiveMessage()  # "distances 0;1.2;0.4"... in the order of the IDs
            if "distances" not in distances: #if ERROR is received, retry
                time.sleep(0.1)
                print "retry ("+distances+")"
                return self.updateTelemetre(listTelemetre)
            listDistances = distances.split(" ")[1].split(";")
            count = 0
            for value in listDistances:
                for telemeter in listTelemetre:
                    if telemeter.id == count:
                        telemeter.setValue(float(listDistances[count]))
                count += 1
            return True
