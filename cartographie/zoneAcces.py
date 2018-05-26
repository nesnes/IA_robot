from cartographie.zone import Zone
from cartographie.ligne import Ligne
class ZoneAcces(Zone):

    def __init__(self,forme, angle):
        self.forme = forme
        self.x = forme.x
        self.y = forme.y
        self.angle = angle

    def dessiner(self,fenetre):
        self.forme.dessiner(fenetre)
        line = Ligne("",self.x,self.y,self.x+100,self.y,"blue")
        line.rotate(self.angle)
        line.dessiner(fenetre)

    def toJson(self):
        line = Ligne("", self.x, self.y, self.x + 100, self.y, "blue")
        line.rotate(self.angle)
        str = u'{'
        str += u'"type":"line",'
        str += u'"name":"{}",'.format("")
        str += u'"x1":{},'.format(self.x)
        str += u'"y1":{},'.format(self.y)
        str += u'"x2":{},'.format(line.x2)
        str += u'"y2":{},'.format(line.y2)
        str += u'"color":"{}"'.format("blue")
        str += u'}'
        return str