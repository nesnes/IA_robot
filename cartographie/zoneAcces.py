from zone import Zone
from ligne import Ligne
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
        str = u''.join([u'{',
            u'"type":"line",',
            u'"name":"{}",'.format(""),
            u'"x1":{},'.format(self.x),
            u'"y1":{},'.format(self.y),
            u'"x2":{},'.format(line.x2),
            u'"y2":{},'.format(line.y2),
            u'"color":"{}"'.format("blue"),
            u'}'])
        return str