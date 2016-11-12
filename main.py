import time
from cartographie.lecteurCarte import LecteurCarte
from cartographie.chercheurChemin import ChercheurChemin
from intelligence.robot import Robot
from intelligence.lecteurRobot import LecteurRobot
from intelligence.executeurObjectif import ExecuteurObjectif

#X;SERVO;ANGINIT;ANGFIN;TEMPSSecondesFloat
def main():
    isRaspberry = False

    if(isRaspberry): # raspberry
        screen = False
        robotConnected = True
    else:
        screen = True
        robotConnected = False

    fichierCarte = "cartes/carte_2017.xml"
    fichierObjectif = "objectifs/2017/objectifsMatch.xml"
    fichierRobot = "robots/robotTest.xml"

    fenetre = None

    # creation du robot
    lecteurRobot = LecteurRobot(fichierRobot)
    robot = lecteurRobot.lire()
    # creation du lecteur de carte
    carte = LecteurCarte(fichierCarte, robot.largeur)
    listePointInteret = carte.lire()   # chargement de la carte

    # creation de l'afficihage de la carte
    if(screen):
        from affichage.afficheurCarte import AfficheurCarte
        from affichage.fenetre import Fenetre
        affichage = AfficheurCarte(fichierCarte,listePointInteret,0.25, 300)
        fenetre = affichage.fenetre
        affichage.afficherCarte() # affichage de la carte

    # creation du pathfinding
    chercher = ChercheurChemin(carte.getTaille(), listePointInteret, fenetre)
    #chercher.graph.dessiner(fenetre)

    fenetre.win.redraw()

    if(robotConnected):
        if screen:
            robot.port = '/dev/tty.usbmodem1422'
    else:
        robot.port = ''
    robot.initialiser(chercher, listePointInteret, fenetre)

    IA = ExecuteurObjectif(robot,fichierObjectif,fichierCarte, chercher, fenetre) #creation de l'IA


    #if(robotConnected):
    IA.afficherObjectifs()
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
            listMouvement = chercher.trouverChemin(x1,y1,x2,y2,listePointInteret,fenetre)
            if listMouvement == None or len(listMouvement) == 0:
                print "WARNING Path Not Found"
            else:
                for ligne in listMouvement:
                    ligne.setCouleur("green")
                    ligne.dessiner(fenetre)
            fenetre.win.redraw()
    time.sleep(5)

main()
