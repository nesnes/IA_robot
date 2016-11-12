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
    while executeurObjectif.robot.getRunningTime() <= executeurObjectif.matchDuration and not stopThread:
        time.sleep(0.5)
    if(stopThread):
        return
    for objectif in executeurObjectif.listeObjectifs:
        if objectif.nom == "Funny Action":
            objectif.executer(executeurObjectif.robot)

class ExecuteurObjectif:

    def __init__(self,robot,ojectifs,carte, chercheurChemin):
        self.robot = robot
        self.fichierObjectifs = ojectifs
        self.fichierCarte = carte
        self.matchDuration = 90

        chercher = chercheurChemin
        lecteurObjectif = LecteurObjectif(self.fichierObjectifs, robot, self.matchDuration)
        carte = LecteurCarte(self.fichierCarte, robot.largeur)

        self.listePointInteret  = carte.lire()
        self.listeObjectifs = lecteurObjectif.lire()

    def executerObjectifs(self):
    	#thread de funny Action
        signal.signal(signal.SIGINT, signal_handler)
    	self.funnyThread = Thread(target=waitForFunnyAction, args=(self,))
    	self.funnyThread.start()
    
        #Mode automate, execution dans l'ordre
        listeObjectifEchoue = []
        i=0
        while i < len(self.listeObjectifs) and self.robot.getRunningTime() < self.matchDuration:     #on parcours chaque objectifs
            objectif = self.listeObjectifs[i]
            if objectif.nom == "Funny Action":
                i += 1
                continue
            print "\n-------",objectif.nom,"-------"
            while not objectif.isFini() and self.robot.getRunningTime() < self.matchDuration: #tant que les actions de l'objectif n'ont pas ete faites
                succes = objectif.executerActionSuivante(self.robot)    #executer l'action suivante

                #if not succes:                                          #en cas d'echec, essayer de nouveau
                #    print "\twarning: nouvel essaie"
                #    succes = objectif.executerActionSuivante(self.robot)#on essaye a nouveau

                if not succes:                                          #en cas d'echec, on met l'objectif en pause
                    print "\t!!!warning: action impossible pour le moment, mise en pause de l'objectif"
                    #objectif.enPause()
                    objectif.reset()
                    listeObjectifEchoue.append(objectif)
                    self.listeObjectifs.remove(objectif)
                    i=-1
                    break

                if succes and objectif.isFini():
                    self.listeObjectifs.remove(objectif)                #on retire l'objectif reussi
                    i=-1
                    """j = self.listeObjectifs.index(objectif) #on repouse l'execution de l'objectif <---v
                    if j < len(self.listeObjectifs)-1:
                        self.listeObjectifs[j],self.listeObjectifs[j+1] = self.listeObjectifs[j+1],self.listeObjectifs[j]
                        i-=1
                        break"""
            i+=1

        #on parcours chaque objectif Echoue
        i=0
        while i < len(listeObjectifEchoue) and self.robot.getRunningTime() < self.matchDuration:
            objectif = listeObjectifEchoue[i]
            print "\n-------",objectif.nom,"-------"
            while not objectif.isFini() and self.robot.getRunningTime() < self.matchDuration:
                succes = objectif.executerActionSuivante(self.robot)
                if not succes:                                          #en cas d'echec, on met l'objectif en pause
                    print "\t!!!warning: action impossible pour le moment, mise en pause de l'objectif"
                    #objectif.enPause()
                    objectif.reset()
                    listeObjectifEchoue.remove(objectif)
                    listeObjectifEchoue.append(objectif) #on le met a la fin de la liste
                    i=-1
                    break

        print "Attente de la fin du match"
        """for objectif in self.listeObjectifs:
            if objectif.nom == "Funny Action":
                while self.robot.getRunningTime() < self.matchDuration:
                    pass
                objectif.executer(self.robot)"""


    def afficherObjectifs(self):
        print "Objectifs de", self.fichierObjectifs
        i=0
        for objectif in self.listeObjectifs:
            i=i+1
            print i,":",objectif.nom
