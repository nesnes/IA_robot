from cartographie.ligne import Ligne

class Telemetre:

    def __init__(self, nom, id,  x, y, angle, minValue=0, maxValue=0):
        self.nom = nom
        self.id = id
        self.x = x
        self.y = y
        self.angle = angle
        self.value = 0
        self.minValue = minValue
        self.maxValue = maxValue
        self.forme = None
        self.color = "green"

    def setValue(self, value):
        self.value = value

    def getValue(self):
        return self.value

    def isValid(self):
        if self.value > 0 and self.value > self.minValue:
            if self.maxValue > 0:
                return self.value < self.maxValue
            else:
                return True
        return False