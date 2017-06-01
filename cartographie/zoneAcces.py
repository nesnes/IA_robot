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
