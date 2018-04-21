import time
import os
from cartographie.lecteurCarte import LecteurCarte
from cartographie.chercheurChemin import ChercheurChemin
from intelligence.robot import Robot
from intelligence.lecteurRobot import LecteurRobot
from intelligence.executeurObjectif import ExecuteurObjectif

def main():
    global isRaspberry
    #Detection du rapsberry
    isRaspberry = "arm" in os.popen("uname -m").read()
    #isRaspberry = "arm" in os.uname()[4]

    if isRaspberry:  # raspberry
        screen = False
        robotConnected = True
        drawGraph = False and screen
    else:
        screen = True
        robotConnected = False
        drawGraph = False and screen

    fichierCarte = "cartes/carte_2018_EpicNes.xml"
    fichierObjectif = "objectifs/2018/objectifsEpicNesTests.xml"
    fichierRobot = "robots/robotEpicNes.xml"

    fenetre = None

    # creation du robot
    print "Reading robot file"
    lecteurRobot = LecteurRobot(fichierRobot)
    robot = lecteurRobot.lire()
    # creation du lecteur de carte
    print "Reading map file"
    carte = LecteurCarte(fichierCarte, robot.largeur)
    listePointInteret = carte.lire()   # chargement de la carte

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
    if simulation:
        print("ERROR: The program is in SIMULATION mode! Some boards can't be detected.")
        print("Statring in 2s.")
        time.sleep(2)

    print "Creating IA"
    IA = ExecuteurObjectif(robot, fichierObjectif, fichierCarte, chercher, fenetre)  # creation de l'IA

    IA.afficherObjectifs()
    print "Running IA"
    IA.executerObjectifs()  # execution de l'IA

    print("End of the match")
    #Don't close connexions to keep score displayed
    #robot.closeConnections()

    # Pour tester le pathfinding, cliquez a deux endroits sur la carte
    if screen:
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
    time.sleep(5)


if __name__ == "__main__":
    main()
