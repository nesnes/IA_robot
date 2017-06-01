from cartographie.lecteurCarte import LecteurCarte
from affichage.fenetre import Fenetre

class AfficheurCarte:
    def __init__(self,fichier = None,listePointInteret = None, ratio = 0.25, offset = 0):
        self.carte = LecteurCarte(fichier,0)
        self.fond = self.carte.getFond()
        dimension = self.carte.getTaille()
        self.fenetre = Fenetre(dimension[0], dimension[1],ratio, offset)
        self.listePointInteret = listePointInteret

    def afficherCarte(self):
        if self.fond != "":
            self.fenetre.drawImage(self.fond)
        for p in self.listePointInteret:
            if p.zoneEvitement != None:
                p.zoneEvitement.dessiner(self.fenetre)
        for p in self.listePointInteret:
            if p.forme != None:
                p.forme.dessiner(self.fenetre)
        for p in self.listePointInteret:
            if p.zoneAcces != None:
                p.zoneAcces.dessiner(self.fenetre)
