from cartographie.ligne import Ligne
from intelligence.robot import Robot

class Telemetre:

    def __init__(self, nom, id,  x, y, angle):
        self.nom = nom
        self.id = id
        self.x = x
        self.y = y
        self.angle = angle
        self.value = 0

    def setValue(self, value):
        self.value = value

    def getValue(self):
        return self.value

    def getLine(self, value, robot):
        line = Ligne("", 0, 0, 0, 0)
        return line