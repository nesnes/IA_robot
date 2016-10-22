import time



from cartographie.collison import Collision
from cartographie.lecteurCarte import LecteurCarte
from cartographie.chercheurChemin import ChercheurChemin
from intelligence.lecteurObjectif import LecteurObjectif
from intelligence.robot import Robot
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

    largeurRobot = 150.0 # son rayon en mm, pour eviter de cogner contre des elements de la table
    fichierCarte = "cartes/carte_2016.xml"
    fichierObjectif = "objectifs/2016/objectifsMatch1.xml"
    #fichierObjectif = "intelligence/objectifsCoquillages3.xml"
    fenetre = None
    robot = None

    chercher = ChercheurChemin() # initialisation du PathFinder
    carte = LecteurCarte(fichierCarte, largeurRobot) # creation du lecteur de carte
    listePointInteret = carte.lire()   # chargement de la carte

    if(screen):
        from affichage.afficheurCarte import AfficheurCarte
        from affichage.fenetre import Fenetre
        affichage = AfficheurCarte(fichierCarte,listePointInteret,0.25, 300)
        fenetre = affichage.fenetre
        affichage.afficherCarte() # affichage de la carte

    if(robotConnected):
        if screen:
            robot = Robot('/dev/ttyACM0',largeurRobot,chercher,listePointInteret,fenetre)
        else:
            #robot = Robot('/dev/ttyACM0',largeurRobot,chercher,listePointInteret)
            #robot = Robot('/dev/ttyAMA0',largeurRobot,chercher,listePointInteret) #connection au robot
            #robot = Robot('/dev/tty.usbmodem1422',largeurRobot,chercher,listePointInteret)
            robot = Robot('/dev/ttyACM0',largeurRobot,chercher,listePointInteret)
            pass
    else:
    	robot = Robot('',largeurRobot,chercher,listePointInteret,fenetre)
    IA = ExecuteurObjectif(robot,fichierObjectif,fichierCarte) #creation de l'IA


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
            if listMouvement == None:
                print "WARNING Path Not Found"
            else:
                for ligne in listMouvement:
                    ligne.setCouleur("green")
                    ligne.dessiner(fenetre)

    time.sleep(5)

main()
