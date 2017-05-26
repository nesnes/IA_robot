import time
import os
from cartographie.lecteurCarte import LecteurCarte
from cartographie.chercheurChemin import ChercheurChemin
from intelligence.robot import Robot
from intelligence.lecteurRobot import LecteurRobot
from intelligence.executeurObjectif import ExecuteurObjectif

#X;SERVO;ANGINIT;ANGFIN;TEMPSSecondesFloat
def main():
    #Detection du rapsberry
    isRaspberry = os.popen("uname -m").read().__contains__("arm")

    if(isRaspberry): # raspberry
        screen = False
        robotConnected = True
    else:
        screen = True
        robotConnected = False

    fichierCarte = "cartes/carte_2017.xml"
    fichierObjectif = "objectifs/2017/objectifsPrincipalSolo.xml"
    fichierRobot = "robots/robotPrincipal2017Solo.xml"
    #fichierObjectif = "objectifs/2017/objectifsSecondaireTest.xml"
    #fichierRobot = "robots/robotSecondaire2017.xml"

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
    if(screen):
        print "Creating map view"
        from affichage.afficheurCarte import AfficheurCarte
        from affichage.fenetre import Fenetre
        affichage = AfficheurCarte(fichierCarte,listePointInteret,0.25, 300)
        fenetre = affichage.fenetre
        affichage.afficherCarte() # affichage de la carte

    # creation du pathfinding
    print "Initializing pathfinding"
    chercher = ChercheurChemin(carte.getTaille(), carte.getHash(), listePointInteret, fenetre)
    #chercher.graph.dessiner(fenetre)

    if(fenetre):
        fenetre.win.redraw()

    if not isRaspberry and robotConnected:
        if screen:
            robot.port = '/dev/tty.usbmodem1412'
            #robot.port = '/dev/tty.usbmodem1412'
            #robot.port2 = '/dev/tty.usbmodem1423'
    elif not isRaspberry and not robotConnected:
        robot.port = ''
        robot.port2 = ''

    if not isRaspberry:
        robot.port2=""

    print "Initializing robot"
    robot.initialiser(chercher, listePointInteret, fenetre)

    print "Creating IA"
    IA = ExecuteurObjectif(robot,fichierObjectif,fichierCarte, chercher, fenetre) #creation de l'IA


    #if(robotConnected):
    IA.afficherObjectifs()
    print "Running IA"
    IA.executerObjectifs() # execution de l'IA

    # Pour tester le pathfinding, cliquez a deux endroits sur la carte
    if(screen):
        while True:
            click1=fenetre.win.getMouse()
            click2=fenetre.win.getMouse()
            x1=(click1.getX())/fenetre.ratio-fenetre.offset
            y1=(click1.getY())/fenetre.ratio-fenetre.offset
            x2=(click2.getX())/fenetre.ratio-fenetre.offset
            y2=(click2.getY())/fenetre.ratio-fenetre.offset
            print "(",x1,y1,")","(",x2,y2,")"
            listMouvement = chercher.trouverChemin(x1,y1,x2,y2,listePointInteret)
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
