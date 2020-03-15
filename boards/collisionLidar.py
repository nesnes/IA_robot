from boards.board import Board
from intelligence.telemetre import Telemetre
import time

class CollisionLidar(Board):

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        Board.__init__(self, nom, fonction, communication, param1, param2)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication
        self.angleDict = {}
        for i in range(0,360,1):
            self.angleDict[i] = 0

    def updateTelemetre(self, listTelemetre):
        if self.isConnected():
            measures = self.receiveMessage()
            for m in measures:
                self.angleDict[round(m.angle)] = m.distance
                for telemeter in listTelemetre:
                    if telemeter.id == round(m.angle):
                        telemeter.setValue(m.distance)
            return True
        return False
