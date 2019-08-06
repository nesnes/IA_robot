import time
import os
import sys
import signal
import __builtin__
import webInterface
from webInterface.interface import Interface
from webInterface.interface import RunningState

def clearModule(mod):
    deleteList = []
    for modName in sys.modules:
        if mod in modName:
            deleteList.append(modName)
    for modName in deleteList:
        del (sys.modules[modName])

def startIA():
    #Re-import modules to handle source modification
    clearModule("affichage")
    clearModule("boards")
    clearModule("cartographie")
    clearModule("intelligence")
    clearModule("robots")
    import affichage
    import boards
    import cartographie
    import intelligence
    import robots

    from cartographie.lecteurCarte import LecteurCarte
    from cartographie.chercheurChemin import ChercheurChemin
    from intelligence.robot import Robot
    from intelligence.lecteurRobot import LecteurRobot
    from intelligence.executeurObjectif import ExecuteurObjectif

    global isRaspberry
    # Detection du rapsberry
    isRaspberry = "arm" in os.popen("uname -m").read()
    # isRaspberry = "arm" in os.uname()[4]

    if isRaspberry:  # raspberry
        screen = False
        robotConnected = True
        drawGraph = False and screen
    else:
        screen = False
        robotConnected = False
        drawGraph = False and screen

    fichierCarte = ""
    fichierObjectif = ""
    fichierRobot = ""
    if webInterface.instance and webInterface.instance.runningParameters:
        fichierCarte = webInterface.instance.runningParameters.mapFile
        fichierObjectif = webInterface.instance.runningParameters.objectiveFile
        fichierRobot = webInterface.instance.runningParameters.robotFile
        robotConnected = webInterface.instance.runningParameters.robotConnected

    fenetre = None

    # creation du robot
    print "Reading robot file"
    lecteurRobot = LecteurRobot(fichierRobot)
    if lecteurRobot.tree is None:
        print "ERROR: Can't find robot file"
        return
    robot = lecteurRobot.lire()
    if webInterface.instance:
        webInterface.instance.addCallableObject(robot)

    # creation du lecteur de carte
    print "Reading map file"
    carte = LecteurCarte(fichierCarte, robot.largeur)
    listePointInteret = carte.lire()  # chargement de la carte
    if len(listePointInteret) == 0:
        print "ERROR: Empty map"
        return
    if webInterface.instance and webInterface.instance.mapBackground is None :
        webInterface.instance.mapBackground = carte.getFond()

    # creation de l'afficihage de la carte
    if screen:
        print "Creating map view"
        from affichage.afficheurCarte import AfficheurCarte
        affichage = AfficheurCarte(fichierCarte, listePointInteret, 0.25, 300)
        fenetre = affichage.fenetre
        affichage.afficherCarte()  # affichage de la carte


    # creation du pathfinding
    print "Initializing pathfinding"
    chercher = ChercheurChemin(carte.getTaille(), carte.getHash(), listePointInteret, fenetre)
    if drawGraph:
        chercher.graph.dessiner(fenetre)

    if fenetre:
        fenetre.win.redraw()

    print "Initializing robot"
    simulation = robot.initialiser(chercher, listePointInteret, fenetre, not robotConnected)
    if simulation and robotConnected:
        return

    if simulation:
        print("ERROR: The program is in SIMULATION mode! Some boards can't be detected.")
        print("Statring in 2s.")
        time.sleep(2)

    if not webInterface.instance or (webInterface.instance and webInterface.instance.runningState == RunningState.PLAY):
        print "Creating IA"
        IA = ExecuteurObjectif(robot, fichierObjectif, fichierCarte, chercher, fenetre)  # creation de l'IA
        if len(IA.listeObjectifs) == 0:
            print "ERROR: Empty objective list"
            return
        IA.afficherObjectifs()
        print "Running IA"
        IA.executerObjectifs()  # execution de l'IA
    elif webInterface.instance and webInterface.instance.runningState == RunningState.MANUAL:
        print "Running MANUAL mode"
        robot.matchDuration = 999999
        robot.attendreDepart()
        while webInterface.instance.runningState != RunningState.STOP:
            time.sleep(1)


    print("End of the match, waiting")
    while True:
        if webInterface.instance and webInterface.instance.runningState != RunningState.PLAY:
            return
        time.sleep(1)
    # Don't close connexions to keep score displayed
    # robot.closeConnections()

    # Pour tester le pathfinding, cliquez a deux endroits sur la carte
    """if screen:
        while True:
            click1 = fenetre.win.getMouse()
            click2 = fenetre.win.getMouse()
            x1 = click1.getX() / fenetre.ratio - fenetre.offset
            y1 = click1.getY() / fenetre.ratio - fenetre.offset
            x2 = click2.getX() / fenetre.ratio - fenetre.offset
            y2 = click2.getY() / fenetre.ratio - fenetre.offset
            print "({} {}) ({}, {})".format(x1, y1, x2, y2)
            listMouvement = chercher.trouverChemin(x1, y1, x2, y2, listePointInteret)
            if listMouvement is None or len(listMouvement) == 0:
                print "WARNING Path Not Found"
            else:
                for ligne in listMouvement:
                    ligne.setCouleur("green")
                    ligne.dessiner(fenetre)
            fenetre.win.redraw()
    """
    time.sleep(5)



__builtin__.stopThread=False
def signal_handler(signal, frame):
    __builtin__.stopThread=True
    print("Exit requested, stopping IA...")
    time.sleep(0.5)
    print("Done.")
    exit()
import traceback
def main():
    signal.signal(signal.SIGINT, signal_handler)
    # create web interface
    interface = Interface()
    if webInterface.instance:
        while True:
            while webInterface.instance.runningState == RunningState.STOP:
                time.sleep(0.5)
            try:
                startIA()
            except Exception as e:
                print "Execution error: {} \n {}".format(e.args, traceback.format_exc())

            webInterface.instance.runningState = RunningState.STOP
            webInterface.instance.clearCallableObjectList()


if __name__ == "__main__":
    main()
