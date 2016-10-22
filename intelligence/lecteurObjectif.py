import xml.etree.ElementTree as ET

from intelligence.objectif import Objectif
from intelligence.action import Action
from intelligence.parametre import Parametre


class LecteurObjectif:

    def __init__(self,fichier):
        self.fichier = fichier
        self.tree = ET.parse(fichier)

    def lire(self):
        root = self.tree.getroot()
        listeObjectifs = []

        if root.tag == "listeObjectif":
            for child in root:
                if child.tag == "objectif":
                    listeObjectifs.append(self.__getObjectif(child))
        return listeObjectifs

    def __getObjectif(self,objectif):
        nom = objectif.get("nom")
        points = objectif.get("points")
        temp = objectif.get("temp")
        dependDe = objectif.get("dependDe")
        tabActions = []

        for noeud in objectif:
            if noeud.tag == "action":
                    tabActions.append(self._getAction(noeud))

        return Objectif(nom,points,temp,dependDe,tabActions)

    def _getAction(self,_action):
        methode=_action.get("methode")
        couleur=_action.get("couleur")
        if couleur == None:
            couleur=''
        tabParam = []
        tabActionsOnError = []
        for param in _action:
            if param.tag == "onError":
                for errorAction in param:
                    tabActionsOnError.append(self._getAction(errorAction))
            else:
                nom=param.get("nom")
                type=param.get("type")
                value=param.get("value")
                if type == "int":
                    value=int(value)
                if type == "float":
                    value=float(value)
                tabParam.append(Parametre(nom,type,value))

        return Action(methode,couleur,tabParam,tabActionsOnError)

