from cartographie.lecteurCarte import LecteurCarte
from affichage.fenetre import Fenetre

class AfficheurCarte:
    def __init__(self,fichier = None,listePointInteret = None, ratio = 0.25, offset = 0):
        self.carte = LecteurCarte(fichier,0)
        dimension = self.carte.getTaille()
        self.fenetre = Fenetre(dimension[0], dimension[1],ratio, offset)
        self.listePointInteret = listePointInteret

    def afficherCarte(self):
        #self.fenetre.drawImage('affichage/fond.gif')
        for p in self.listePointInteret:
            if p.zoneEvitement != None:
                p.zoneEvitement.dessiner(self.fenetre)
        for p in self.listePointInteret:
            if p.zoneAcces != None:
                p.zoneAcces.dessiner(self.fenetre)
        for p in self.listePointInteret:
            if p.forme != None:
                p.forme.dessiner(self.fenetre)