from cartographie.lecteurCarte import LecteurCarte
from cartographie.chercheurChemin import ChercheurChemin
from intelligence.lecteurObjectif import LecteurObjectif
from intelligence.robot import Robot
from threading import Thread
import time
import signal
import sys

stopThread=False
def signal_handler(signal, frame):
    global stopThread
    stopThread=True
    print("Exit requested, stopping IA...")
    time.sleep(0.5)
    print("Done.")
    exit()

def waitForFunnyAction(executeurObjectif):
    global stopThread
    print "Funny Action thread running"
    objectifFunnyAction = None
    for objectif in executeurObjectif.listeObjectifs:
        if objectif.nom == "Funny Action":
            objectifFunnyAction = objectif
    if objectifFunnyAction == None:
        print("WARNING, no Funny Action found in objectif list. The objectif name must be \"Funny Action\"")
        return
    while executeurObjectif.robot.getRunningTime() <= executeurObjectif.matchDuration and not stopThread:
        time.sleep(0.5)
    if(stopThread):
        return
    print("Starting Funny Action...")
    objectifFunnyAction.executer(executeurObjectif.robot)

class ExecuteurObjectif:

    def __init__(self,robot,ojectifs,carte, chercheurChemin, fenetre=None):
        self.robot = robot
        self.fichierObjectifs = ojectifs
        self.fichierCarte = carte
        self.matchDuration = 90
        self.fenetre = fenetre

        chercher = chercheurChemin
        lecteurObjectif = LecteurObjectif(self.fichierObjectifs, robot, self.matchDuration)
        carte = LecteurCarte(self.fichierCarte, robot.largeur)

        self.listePointInteret  = carte.lire()
        self.listeObjectifs = lecteurObjectif.lire()

    def selectionnerObjectif(self, listObjectif):
        listPossible = []
        for objectif in listObjectif:
            if objectif.nom == "Attente du GO":
                if not objectif.isFini():
                    return objectif
            elif objectif.isPossible():
                listPossible.append(objectif)
        listPossibleOrdered = sorted(listPossible, key=lambda objetcif: objectif.estimateValue())
        for objectif in listPossibleOrdered:
            if objectif.nom == "Funny Action":
                continue
            return objectif
        return None

    def executerObjectifs(self):
        #thread de funny Action
        signal.signal(signal.SIGINT, signal_handler)
        self.funnyThread = Thread(target=waitForFunnyAction, args=(self,))
        self.funnyThread.start()

        #Mode intellingent, execution selon estimation temp/point
        listeObjectifEchoue = []
        listeObjectifs = list(self.listeObjectifs)
        while self.robot.getRunningTime() < self.matchDuration:
            objectif = self.selectionnerObjectif(listeObjectifs)
            if objectif == None:
                print("No possible objectif, looking in failed ones... ")
                listeObjectifs += listeObjectifEchoue
                listeObjectifEchoue = []
                objectif = self.selectionnerObjectif(listeObjectifs)
            if objectif == None:
                print("No possible Objectif for the moment... time="+str(self.robot.getRunningTime())+"s")
                time.sleep(1)
                continue
            print "\n-------",objectif.nom,"-------"
            objectifFinished = False
            while not objectifFinished and self.robot.getRunningTime() < self.matchDuration: #tant que les actions de l'objectif n'ont pas ete faites
                objectifFinished = False
                succes = objectif.executerActionSuivante(self.robot)    #executer l'action suivante
                time.sleep(0.05)
                if(self.fenetre != None):
                    self.fenetre.win.redraw()
                if not succes: #en cas d'echec, on repousse l'objectif
                    print "\t!!!warning: action impossible pour le moment, arret de l'objectif"
                    #objectif.enPause()
                    objectif.reset()
                    listeObjectifEchoue.append(objectif)
                    listeObjectifs.remove(objectif)
                    break
                if succes and objectif.isFini():
                    objectifFinished = True
                    if objectif.repetitions > 0:
                        objectif.repetitions -= 1
                        objectif.reset()
                    else:
                        listeObjectifs.remove(objectif) #on retire l'objectif reussi
        print "Fin du match"

    def afficherObjectifs(self, listeObjectifs=None):
        if(listeObjectifs == None):
            listeObjectifs = self.listeObjectifs
        print "Objectifs de", self.fichierObjectifs
        i=0
        for objectif in listeObjectifs:
            i=i+1
            print i,":",objectif.nom, objectif.etat
