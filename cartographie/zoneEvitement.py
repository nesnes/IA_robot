from zone import Zone

class ZoneEvitement(Zone):

    def __init__(self,forme):
        self.forme = forme

    def dessiner(self,fenetre):
        self.forme.dessiner(fenetre)
