import time
import math
from intelligence.communicationRobot import CommunicationRobot
from cartographie.ligne import Ligne
from cartographie.cercle import Cercle
from intelligence.position import Position

class Robot:

    def __init__(self,nom, port,largeur):
        self.communication = None
        self.communication2 = None
        self.nom = nom
        self.port = port
        self.port2 = "" #Commande W pour ID:"carte2"
        self.fenetre = None
        self.largeur = largeur
        self.chercher = None
        self.listPointInteret = None
        self.listVariables = []
        self.listPosition = []
        self.listTelemetre = []
        self.couleur=""
        self.startTime = time.time()

    def initialiser(self, chercher, listPointInteret, fenetre=None):
        self.communication = CommunicationRobot(self.port)
        if self.port2:
            self.communication2 = CommunicationRobot(self.port2)
            self.communication2.envoyer("W\r\n")
            rcv2 = self.communication2.recevoir()
            print("Port2 "+self.port2+" ID:"+rcv2)
            self.communication.envoyer("W\r\n")
            rcv1 = self.communication.recevoir()
            print("Port1 "+self.port+" ID:"+rcv1)
            if rcv2.__contains__("1"):
                print("Switching serial ports")
                tmp = self.communication
                self.communication = self.communication2
                self.communication2 = tmp
                tmp = self.port
                self.port = self.port2
                self.port2 = tmp
        else:
            print("Only one card")
        self.fenetre = fenetre
        self.chercher = chercher
        self.listPointInteret = listPointInteret

    def dessiner(self):
        from cartographie.cercle import Cercle
        circle = Cercle(self.nom, self.x, self.y, self.largeur, "grey")
        circle.dessiner(self.fenetre)
        line = Ligne("", self.x, self.y, self.x + self.largeur, self.y, "blue")
        line.rotate(self.angle)
        line.dessiner(self.fenetre)
        for telemetre in self.listTelemetre:
            line = Ligne("", self.x, self.y, self.x - telemetre.x, self.y + telemetre.y, "green")
            line.rotate(line.getAngle()+self.angle-90)
            line.dessiner(self.fenetre)
            circle = Cercle(telemetre.nom, line.x2, line.y2, 10, "green")
            circle.dessiner(self.fenetre)
            lineTarget = Ligne("", line.x2, line.y2, line.x2*2, line.y2*2, "orange")
            lineTarget.resize(20);
            lineTarget.rotate(self.angle+telemetre.angle)
            lineTarget.dessiner(self.fenetre)
        self.telemetreDetectAdversaire()

    def attendreDepart(self):
        if self.communication.portserie == '':
            self.startTime = time.time()
            defaultValues = self.listPosition[1]
            if self.couleur != "":
                if self.couleur == self.listPosition[0].couleur:
                    defaultValues = self.listPosition[0]
                elif self.couleur == self.listPosition[1].couleur:
                    defaultValues = self.listPosition[1]
            self.couleur = defaultValues.couleur
            self.x = defaultValues.x
            self.y = defaultValues.y
            self.angle = defaultValues.angle #0 degres =3 heures
            self.startX = self.x
            self.startY = self.y
            if self.fenetre != None:
                self.dessiner()
            print("Le robot virtuel est " + self.couleur + " a la position x:" + str(self.x) + " y:" + str(self.y) + " angle:" + str(self.angle))
            return True
        rcv = self.communication.recevoir()
        print rcv
        while(not rcv.__contains__("GO")):
            self.startTime = time.time()
            rcv = self.communication.recevoir()
            print rcv
            #check if we recieved the color
            if(rcv.__contains__("BLEU")): #COLOR A
                self.couleur=self.listPosition[0].couleur
                print("Le robot est "+self.couleur)
            if(rcv.__contains__("JAUNE")): #COLOR B
                self.couleur=self.listPosition[1].couleur
                print("Le robot est "+self.couleur)

        #Set the initial positions
        if(self.couleur==self.listPosition[0].couleur):
            self.x = self.listPosition[0].x
            self.y = self.listPosition[0].y
            self.angle = self.listPosition[0].angle #0=3h

        else:
            self.x = self.listPosition[1].x
            self.y = self.listPosition[1].y
            self.angle = self.listPosition[1].angle #180=9h
        #self.retirerElementCarte("depart", self.couleur)
        print("Le robot est " + self.couleur + " a la position x:" + str(self.x) + " y:" + str(self.y) + " angle:" + str(self.angle))
        self.startTime = time.time()
        self.communication.envoyer("G\r\n") #Go to the robot
        goEcho = self.communication.recevoir()
        if self.communication2:
            self.communication2.envoyer("G\r\n") #Go to the robot
        self.startX = self.x
        self.startY = self.y
        return True

    def getRunningTime(self):
        return time.time() - self.startTime

    def attendreMilliseconde(self,duree):
        time.sleep(float(duree)/1000.0);
        return True

    def getVariable(self, nom):
        for variable in self.listVariables:
            if variable.nom == nom:
                return variable
        return None

    def telemetreDetectAdversaire(self):
        for telemetre in self.listTelemetre:
            if telemetre.value == 0:
                continue
            line = Ligne("", self.x, self.y, self.x - telemetre.x, self.y + telemetre.y, "green")
            line.rotate(line.getAngle()+self.angle-90)
            lineTarget = Ligne("", line.x2, line.y2, line.x2*2, line.y2*2, "purple")
            lineTarget.resize(telemetre.value)
            lineTarget.rotate(self.angle+telemetre.angle)
            lineTarget.dessiner(self.fenetre)
            if lineTarget.getlongeur() > 5:
                containingElements = self.chercher.pointContenuListe(lineTarget.x1, lineTarget.y1, self.listPointInteret)
                listPointDetection = list(self.listPointInteret)
                for point in containingElements:
                    listPointDetection.remove(point)
                collision = self.chercher.enCollisionCarte(lineTarget, listPointDetection, True)
                if not collision:
                    circle = Cercle(telemetre.nom, line.x2, line.y2, 20, "purple")
                    circle.dessiner(self.fenetre)
                    lineTarget.dessiner(self.fenetre)
                    print("/!\\ Telemeter("+telemetre.nom+") detected Unkown object. Position "+str(lineTarget.x1)+","+str(lineTarget.x2)+", angle "+str(lineTarget.getAngle())+ " at distance "+str(telemetre.value))
                    return [lineTarget.x2, lineTarget.y2]
                else:
                    print("Telemeter detected " + collision.nom)
        return False

    def aveugler(self):
         time.sleep(500/1000.0);
         self.communication.envoyer("U\r\n")
         time.sleep(500/1000.0);
         return True

    def rendreVue(self):
         time.sleep(500/1000.0);
         self.communication.envoyer("V\r\n")
         time.sleep(500/1000.0);
         return True

    def executer(self,action):
        tabParam=[]
        for param in action.tabParametres:
            tabParam.append(param.getValue())
        if hasattr(self,action.methode):
            return getattr(self,action.methode)(*tabParam) #Run the requested method
        else:
            print "ERREUR: La methode",action.methode,"n'existe pas!!!"
            return False

    def positionAtteinte(self,x,y,x1,y1,erreur):
        if( (abs(x-x1) <= erreur) and (abs(y-y1) <= erreur) ):
            return True
        return False

    def distanceAtteinte(self,dist1, angle1, dist2, angle2 , erreurDist, erreurAngle):
        if( (abs(dist1-dist2) <= erreurDist) and (abs(angle1-angle2) <= erreurAngle) ):
            return True
        return False


    def getAngleToDo(self,angle):
        res = angle - self.angle
        if res > 180:
            res = -360 + res
        if res < -180:
            res = 360 + res
        return res

    def seDeplacerXY(self,x,y,angle, vitesse=1.0):
        print "\t \t Deplacement: x:",x," y:",y," angle:",angle
        chemin = self.chercher.trouverChemin(self.x,self.y,x,y,self.listPointInteret)
        if chemin == None:
            print "\t \t Chemin non trouve"
            return False
        for ligne in chemin:
            if not self.seDeplacerDistanceAngle(ligne.getlongeur(),self.getAngleToDo(ligne.getAngle())):
                return False
            #print "\t \tDeplacement: distance:",str(ligne.getlongeur())," angle:",str(ligne.getAngle())
        if not self.seDeplacerDistanceAngle(0,self.getAngleToDo(angle),vitesse):
            return False
        if self.communication.portserie != '':
            return self.positionAtteinte(x, y, self.x, self.y,50)
        else:
            return True

    def updatePositionRelative(self,distance,angle):
        print("Update Pos")
        angleDiff=(angle+self.angle)*0.0174532925 #rad
        xprev=self.x
        yprev=self.y
        self.x += distance*math.cos(angleDiff)
        self.y += distance*math.sin(angleDiff)
        self.angle += angle
        if self.angle > 180:
            self.angle = -360 + self.angle
        if self.angle < -180:
            self.angle = 360 + self.angle
        if self.fenetre != None:
            ligne = Ligne("",xprev,yprev,self.x,self.y,"green")
            ligne.dessiner(self.fenetre)
            self.fenetre.win.redraw()

    def seDeplacerDistanceAngle(self,distance,angle,vitesse=0.3, retry=1, recalage = 0):
        print "\t \tDeplacement: distance:",str(distance)," angle:",str(angle)
        errorObstacle=False
        errorStatic=False
        if self.communication.portserie != '':
            self.communication.envoyer("M;"+str(distance)+";"+str(angle)+";"+str(vitesse)+";1\r\n")
            ok = self.communication.recevoir() # "OK"
            print ok
            message = ""
            while not message.__contains__("mouvement"):
                message = self.communication.recevoir()
                """res = self.interrogerCapteurIR()
                if not type(res) == bool:
                    print("test telemetre bool")
                    message = res
                else:
                    print("test telemetre")
                    collision = self.telemetreDetectAdversaire()
                    if not collision:
                        print "Stopping robot"
                        self.communication.envoyer("H\r\n")
                        errorObstacle = True
                        break"""
            if message.__contains__("immobile"):
                errorStatic=True
            if message.__contains__("obstacle"):
                errorObstacle = True
            encodeur = self.communication.recevoir()

        if self.communication.portserie != '':
            while not encodeur.__contains__("EG") and not encodeur.__contains__("Orientation"):
                encodeur = self.communication.recevoir()
                print encodeur

            if encodeur.__contains__("EG"):
                encodeur = self.communication.recevoir()

            #Update Position / Angle
            distanceDone = float(encodeur.split(";")[0].split("=")[1])
            angleDone = float(encodeur.split(";")[1].split("=")[1])
            self.updatePositionRelative(distanceDone,angleDone)
            if(recalage == 1):
                print "recalage"
                return True
            if errorObstacle or errorStatic:
                if errorObstacle:
                    print "Error obstacle"
                else:
                    #self.communication.recevoir() #need to read telemeter message
                    print "Error static robot"
                return self.distanceAtteinte(distance, angle, distanceDone, angleDone, 30, 5)
            print "\t \tMouvement Fini: "+encodeur
            if(encodeur.__len__() != 0):
                if not self.distanceAtteinte(distance, angle, distanceDone, angleDone, 50, 5):
                    pass
                    if(retry):
                        self.seDeplacerDistanceAngle(distance, angle, vitesse, 0)
                    else:
                        return False
                else:
                    return True
            else:
                return False
        else:
            self.updatePositionRelative(distance, angle)
            return True
        return False

    def seDeplacerVersUnElement(self,type,vitesse=1,couleur=None):
        element = None
        if couleur==None:
            couleur = self.couleur
        #recherche de l'objet
        for obj in self.listPointInteret:
            if obj.type == type and (obj.couleur == couleur or obj.couleur not in [self.listPosition[0].couleur, self.listPosition[1].couleur]):
                element = obj
                break
        if element == None:
            print "\t \tElement non trouve!!!!" + type
            return False
        zoneAcces = element.zoneAcces
        if zoneAcces == None:
            print "\t \tL'element \""+element.nom+"\" n'a pas de zone d'acces"
            return False
        return self.seDeplacerXY(zoneAcces.x, zoneAcces.y, zoneAcces.angle, vitesse)


    def retirerElementCarte(self,type,couleur=None):
        element = None
        if couleur==None:
            couleur = self.couleur
        #recherche de l'objet
        for obj in self.listPointInteret:
            if obj.type == type and (obj.couleur == couleur or obj.couleur not in [self.listPosition[0].couleur, self.listPosition[1].couleur]):
                element = obj
                break
        if element == None:
            print "Element non trouve!!!!"
            return False
        self.chercher.updateNodesRemovingElement(element, self.listPointInteret)
        self.listPointInteret.remove(element)
        print("Points: "+str(len(self.listPointInteret)))
        #self.chercher.createGraph(self.listPointInteret)
        if self.fenetre:
            element.zoneEvitement.forme.couleur = "white"
            element.zoneEvitement.dessiner(self.fenetre)
            self.fenetre.win.redraw()
        return True

    def avancer(self,distance,vitesse=0.5):
        return self.seDeplacerDistanceAngle(distance,0,vitesse)

    def reculer(self,distance,vitesse=0.5):
        return self.seDeplacerDistanceAngle(-distance,0,vitesse)

    def recaler(self,distance,vitesse=0.5):
        return self.seDeplacerDistanceAngle(distance,0,vitesse, 1, 1)

    def setServomoteur(self, idServo, angle):
        if self.communication.portserie != '':
            self.communication.envoyer("S;"+str(idServo)+";0;"+str(angle)+"\r\n")
            valid = ""
            #OK
            while(not valid.__contains__("K")):
                valid = self.communication.recevoir()
                #PB
                if(valid.__contains__("B")):
                    return False
        return True

    def setProgressiveServomoteur(self, idServo, startAngle, endAngle, seconds, blocking=True):
        #Methode not tested, not sure we need to wait for OK or PB, ask fabrice AND check in the Mbed code
        if self.communication.portserie != '':
            self.communication.envoyer("X;"+str(idServo)+";"+str(startAngle)+";"+str(endAngle)+";"+str(seconds)+"\r\n")
            if(blocking):
                time.sleep(seconds)
            valid = ""
            #OK
            while(not valid.__contains__("K")):
                valid = self.communication.recevoir()
                #PB
                if(valid.__contains__("B")):
                    return False
        return True

#Special methods for each year has to be wrote under there

    def recolterModule(self):
        #do the thing to store the module

        reserveGauche = self.getVariable("reserveModuleGauche")
        if reserveGauche.isMax():
            reserveDroite = self.getVariable("reserveModuleDroite")
            if reserveDroite.isMax():
                print("Can't store more modules")
                return False
            else:
                #store the module here
                reserveDroite.incrementer()
        else:
            #store the module here
            reserveGauche.incrementer()
        return True

    def recolterRoche(self):
        #do the thing
        bacRoche = self.getVariable("bacRoche")
        bacRoche.incrementer()
        return True

    def deposerRoche(self):
        #do the thing

        bacRoche = self.getVariable("bacRoche")
        bacRoche.valeur = 0
        return True

    def deposerModule(self):
        #do the thing to store the module

        reserveGauche = self.getVariable("reserveModuleGauche")
        reserveGauche.valeur = 0
        reserveDroite = self.getVariable("reserveModuleDroite")
        reserveDroite.valeur = 0
        return True

#SPECIAL 2016 METHODS (Can be suppressed for another year)
    def lireMessagesMbed(self):
        if self.communication.portserie == '':
            self.startTime = time.time()
            return True
        rcv = self.communication.recevoir()
        print rcv
        while(True):
            rcv = self.communication.recevoir()
            print rcv
        return True

    def interrogerCapteurIR(self):
        self.communication.envoyer("I\r\n")
        if self.communication.portserie == '':
           return True
        rcv = self.communication.recevoir()
        if not rcv.__contains__("I;"):
            return rcv #Probably the end of the movment message
        values = rcv.split(";")
        for telemetre in self.listTelemetre:
            telemetre.value = int(values[telemetre.id+1])
        print rcv
        return True

    def tournerBrosse(self):

        time.sleep(0.3)
        if self.communication.portserie != '':
            self.communication.envoyer("B\r\n")
        time.sleep(0.3)
        return True

    def arreterBrosse(self):
        time.sleep(0.3)
        if self.communication.portserie != '':
            self.communication.envoyer("A\r\n")
        time.sleep(0.3)
        return True

    def allumerExpulseurBalle(self):
        if self.communication2:
            self.communication2.envoyer("B\r\n")
        return True

    def eteindreExpulseurBalle(self):
        if self.communication2:
            self.communication2.envoyer("A\r\n")
        return True

    def monterPanier(self):
        if self.communication2:
            self.communication2.envoyer("M\r\n")
            valid = ""
            while (not valid.__contains__("haut")):
                valid = self.communication2.recevoir()
        return True

    def descendrePanier(self):
        if self.communication2:
            self.communication2.envoyer("D\r\n")
            valid = ""
            while (not valid.__contains__("bas")):
                valid = self.communication2.recevoir()
        return True

    def funnyAction(self):
        if self.communication2:
            self.communication2.envoyer("F\r\n")
        return True

    def leverBras(self):
        self.aveugler()
        time.sleep(0.1)
        if self.communication.portserie != '':
            self.communication.envoyer("Z\r\n")
        time.sleep(0.3)
        self.arreterBrosse()
        time.sleep(0.1)
        self.rendreVue()
        time.sleep(0.1)
        return True

    def baisserBras(self):
        self.aveugler()
        time.sleep(0.1)
        self.tournerBrosse()
        time.sleep(0.3)
        if self.communication.portserie != '':
            self.communication.envoyer("F\r\n")
        time.sleep(0.3)
        self.rendreVue()
        time.sleep(0.1)
        return True

    def incrementerBac(self):
        bacRoche = self.getVariable("bacRoche")
        bacRoche.incrementer()
        return True

    def viderBac(self):
        bacRoche = self.getVariable("bacRoche")
        bacRoche.set(0)
        print("Bac roche" + str(bacRoche.get()))
        return True


    #SPECIAL 2016 METHODS