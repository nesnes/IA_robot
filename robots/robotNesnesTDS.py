from intelligence.robot import Robot
from webInterface.interface import RunningState
from webInterface.interface import functionUI
import webInterface
import time
from threading import Thread

from websocket import create_connection

def departDepositThread(robot):
    while robot.getRemainingTime()>0 and (robot.getVariable("paletsLeft").get()>0 or robot.getVariable("paletsMiddle").get()>0 or robot.getVariable("paletsRight").get()>0) :
        robot.brasRobotTheo.armDepositPrepare("A");
        time.sleep(0.4)
                
        if robot.getVariable("paletsLeft").get()>0:
            if robot.brasRobotTheo:
                robot.brasRobotTheo.armStock("L", robot.getDepositPosition("paletsLeft"))
                robot.brasRobotTheo.pumpOn("L");
            robot.decrementerVariable("paletsLeft")
            if robot.objectifEnCours is not None:
                robot.objectifEnCours.points += 1;
        if robot.getVariable("paletsMiddle").get()>0 and robot.getVariable("gold").get() == 0:
            if robot.brasRobotTheo:
                robot.brasRobotTheo.armStock("M", robot.getDepositPosition("paletsMiddle"))
                robot.brasRobotTheo.pumpOn("M");
            robot.decrementerVariable("paletsMiddle")
            if robot.objectifEnCours is not None:
                robot.objectifEnCours.points += 3;
        if robot.getVariable("paletsRight").get()>0:
            if robot.brasRobotTheo:
                robot.brasRobotTheo.armStock("R", robot.getDepositPosition("paletsRight"))
                robot.brasRobotTheo.pumpOn("R");
            robot.decrementerVariable("paletsRight")
            if robot.objectifEnCours is not None:
                robot.objectifEnCours.points += 1;
        
        if robot.brasRobotTheo:
            time.sleep(0.4)
            #robot.brasRobotTheo.armFloorGrabPrepare("A");
            #time.sleep(0.1)
            robot.brasRobotTheo.armWallGrab("A");
            time.sleep(0.3)
        
        if robot.brasRobotTheo:
            robot.brasRobotTheo.pumpOff("A");
            time.sleep(0.6)
    if robot.brasRobotTheo:
        robot.brasRobotTheo.armDefault("A");
    return True
    
def experience_thread_A(robot):
    if robot.isSimulated:
        return True
    try:
        ws2 = create_connection("ws://192.168.42.101:81") #Experience
        ws2.send('''{
        "frequency": 20,
        "loop":1,
        "animation": [
        {"servoId":0,"origin":30, "target":100, "startTime":0, "endTime":500},
        {"servoId":0,"origin":100, "target":30, "startTime":500, "endTime":1250},
        {"servoId":0,"origin":30, "target":170, "startTime":1250, "endTime":2000},
        {"servoId":0,"origin":170, "target":30, "startTime":2000, "endTime":2500},
        {"servoId":1,"origin":0, "target":10, "startTime":0, "endTime":0},
        {"servoId":1,"origin":10, "target":0, "startTime":100, "endTime":100},
        {"servoId":1,"origin":0, "target":10, "startTime":200, "endTime":200},
        {"servoId":1,"origin":10, "target":0, "startTime":250, "endTime":250},
        {"servoId":1,"origin":0, "target":10, "startTime":500, "endTime":500},
        {"servoId":1,"origin":10, "target":0, "startTime":600, "endTime":600},
        {"servoId":1,"origin":0, "target":10, "startTime":625, "endTime":625},
        {"servoId":1,"origin":10, "target":0, "startTime":650, "endTime":650},
        {"servoId":1,"origin":0, "target":10, "startTime":675, "endTime":675},
        {"servoId":1,"origin":10, "target":0, "startTime":700, "endTime":700},
        {"servoId":1,"origin":0, "target":10, "startTime":900, "endTime":900},
        {"servoId":1,"origin":10, "target":0, "startTime":2000, "endTime":2000}
        ]}''')
        ws2.close()
    except:
        return False
    return True
    
def electron_thread_A(robot):
    if robot.isSimulated:
        return True
    try:
        ws1 = create_connection("ws://192.168.42.100:81") #Electron
        direction = 30
        if robot.couleur == 'violet':
            direction = 150
        ws1.send('''{
        "frequency": 20,
        "loop":1,
        "animation": [
        {"servoId":0, "origin":'''+str(direction)+''', "target":'''+str(direction)+''', "startTime":4500, "endTime":4500},
        {"servoId":0, "origin":90, "target":90, "startTime":15000, "endTime":15000},
        {"servoId":1, "origin":90, "target":90, "startTime":0, "endTime":0},

        {"servoId":3, "origin":76, "target":76, "startTime":0, "endTime":0},
        {"servoId":4, "origin":100, "target":100, "startTime":0, "endTime":0},
        
        {"servoId":5, "origin":1, "target":1, "startTime":0, "endTime":0},
        {"servoId":5, "origin":0, "target":0, "startTime":900, "endTime":900},
        {"servoId":5, "origin":1, "target":1, "startTime":1000, "endTime":1000},
        {"servoId":5, "origin":0, "target":0, "startTime":3500, "endTime":3500},
        {"servoId":5, "origin":1, "target":1, "startTime":3600, "endTime":3600},
        {"servoId":5, "origin":0, "target":0, "startTime":4750, "endTime":4750},
        {"servoId":5, "origin":1, "target":1, "startTime":4850, "endTime":4850},
        
        {"servoId":2, "origin":85, "target":85, "startTime":0, "endTime":0},
        {"servoId":2, "origin":95, "target":95, "startTime":1000, "endTime":1000},
        {"servoId":2, "origin":80, "target":80, "startTime":2750, "endTime":2750},
        {"servoId":2, "origin":87, "target":87, "startTime":4500, "endTime":4500},
        {"servoId":2, "origin":85, "target":85, "startTime":15000, "endTime":15000},
        
        
        {"servoId":3, "origin":76, "target":60, "startTime":250, "endTime":500},
        {"servoId":3, "origin":76, "target":90, "startTime":2000, "endTime":2500},
        {"servoId":3, "origin":90, "target":76, "startTime":3750, "endTime":4500},
        
        {"servoId":4, "origin":100, "target":75, "startTime":250, "endTime":500},
        {"servoId":4, "origin":75, "target":75, "startTime":2000, "endTime":2500},
        {"servoId":4, "origin":75, "target":100, "startTime":3000, "endTime":4500},
        
        {"servoId":1, "origin":90, "target":120, "startTime":0, "endTime":500},
        {"servoId":1, "origin":120, "target":70, "startTime":2000, "endTime":2500},
        {"servoId":1, "origin":70, "target":90, "startTime":3750, "endTime":4500}
        ]}''')
        ws1.close()
    except:
        return False
    return True
    
def wallGrab_thread_A_func(robot):
    print("Thread Running")
    if robot.brasRobotTheo:
        print("Thread If")
        robot.brasRobotTheo.armDepositPrepare("A");
        print("Deposit OK")
        leftPos = robot.getStockPosition("paletsLeft")
        middlePos = robot.getStockPosition("paletsMiddle")
        rightPos = robot.getStockPosition("paletsRight")
        print("Thread pos {} {} {}".format(leftPos, middlePos, rightPos))
        if leftPos == middlePos and middlePos == rightPos:
            robot.brasRobotTheo.armStock("A", middlePos)
        else:
            robot.brasRobotTheo.armStock("L", leftPos)
            robot.brasRobotTheo.armStock("M", middlePos)
            robot.brasRobotTheo.armStock("R", rightPos)
        robot.brasRobotTheo.pumpOff("A");
        time.sleep(0.6)
        robot.brasRobotTheo.armDefault("A");
    print("Thread Done")
    
def depositBalance_thread_A_func(robot):
    print("Thread Running")
    if robot.brasRobotTheo:
        robot.brasRobotTheo.armDepositPrepare("A");
        time.sleep(0.3)
        
        print("{} Palets R {}  M {}  L {}".format(robot.couleur, robot.getVariable("paletsRight").get(), robot.getVariable("paletsMiddle").get(), robot.getVariable("paletsLeft").get() ))
        
        if robot.getVariable("gold").get() >0:
            if robot.brasRobotTheo:
                robot.brasRobotTheo.armStock("M", 2);
                robot.brasRobotTheo.pumpOn("M");
            robot.decrementerVariable("paletsMiddle")
            robot.decrementerVariable("paletsMiddle")
            robot.decrementerVariable("gold")
            robot.incrementerVariable("balance")
            if robot.objectifEnCours is not None:
                robot.objectifEnCours.points += 24;
            if robot.brasRobotTheo:
                robot.brasRobotTheo.armWallDeposit("M");
        else:
            if robot.getVariable("paletsLeft").get()>0 and robot.couleur == "violet":
                if robot.brasRobotTheo:
                    print "TakeLeft"
                    robot.brasRobotTheo.pumpOn("L");
                    robot.brasRobotTheo.armStock("L", robot.getDepositPosition("paletsLeft"))
                robot.decrementerVariable("paletsLeft")
                robot.incrementerVariable("balance")
                if robot.objectifEnCours is not None:
                    robot.objectifEnCours.points += 10;#8(green) 12(blue)
            if robot.getVariable("paletsMiddle").get()>0 :
                print "TakeMiddle"
                if robot.brasRobotTheo:
                    robot.brasRobotTheo.pumpOn("M");
                    robot.brasRobotTheo.armStock("M", robot.getDepositPosition("paletsMiddle"))
                robot.decrementerVariable("paletsMiddle")
                robot.incrementerVariable("balance")
                if robot.objectifEnCours is not None:
                    robot.objectifEnCours.points += 10;#8(green) 12(blue)
            if robot.getVariable("paletsRight").get()>0 and robot.couleur == "orange":
                print "TakeRight"
                if robot.brasRobotTheo:
                    robot.brasRobotTheo.pumpOn("R");
                    robot.brasRobotTheo.armStock("R", robot.getDepositPosition("paletsRight"))
                robot.decrementerVariable("paletsRight")
                robot.incrementerVariable("balance")
                if robot.objectifEnCours is not None:
                    robot.objectifEnCours.points += 10;#8(green) 12(blue)
        
            if robot.brasRobotTheo:
                time.sleep(0.3)
                if robot.couleur == "orange":
                    robot.brasRobotTheo.armFloorGrabPrepare("R");
                    robot.brasRobotTheo.armFloorGrabPrepare("M");
                    robot.brasRobotTheo.armWallDeposit("R");
                    robot.brasRobotTheo.armWallDeposit("M");
                elif robot.couleur == "violet":
                    robot.brasRobotTheo.armFloorGrabPrepare("L");
                    robot.brasRobotTheo.armFloorGrabPrepare("M");
                    robot.brasRobotTheo.armWallDeposit("L");
                    robot.brasRobotTheo.armWallDeposit("M");
    print("Thread Done")


def floorGrabPrepare_thread_A(robot):
    robot.brasRobotTheo.pumpOn("A");
    robot.brasRobotTheo.armFloorGrabPrepare("A");
    time.sleep(0.4)
    
def floorGrab_thread_A(robot):
    if robot.brasRobotTheo:
        time.sleep(0.25)
        leftPos = robot.getStockPosition("paletsLeft")
        rightPos = robot.getStockPosition("paletsRight")
        if leftPos == rightPos:
            robot.brasRobotTheo.armStock("A", leftPos)
        else:
            robot.brasRobotTheo.armStock("L", leftPos)
            robot.brasRobotTheo.armStock("R", rightPos)
        time.sleep(0.25)
        robot.brasRobotTheo.pumpOff("A");
        time.sleep(0.5)
        robot.brasRobotTheo.armDefault("A");
    robot.retirerElementCarte("atomeBas", robot.couleur)
    robot.retirerElementCarte("atomeMilieu", robot.couleur)

class RobotNesnesTDS(Robot):

    def __init__(self, nom, largeur):
        Robot.__init__(self, nom, largeur)
        self.brasRobotTheo = None
        self.targetCubeOrder = []
        self.currentCubeOrder = []

    def initialiser(self, chercher, listPointInteret, fenetre=None, simulate=False):
        Robot.initialiser(self, chercher, listPointInteret, fenetre, simulate)
        if simulate != self.isSimulated:
            self.isSimulated = True
            return self.isSimulated
        if not self.isSimulated:
            for board in self.listBoard:
                if board.nom == "BrasRobotTheo":
                    self.brasRobotTheo = board
            #elif board.nom == "BallGatherAlex":
            #    self.ballGatherAlex = board
        if not self.brasRobotTheo or not self.brasRobotTheo.isConnected():
            print("ERROR: No brasRobotTheo found")
            self.isSimulated = True
        elif webInterface.instance and self.brasRobotTheo:
            webInterface.instance.addCallableObject(self.brasRobotTheo)

        #print "init cube detection"
        #self.cubeDetector = CubeDetector()
        
    def startElectron(self):
        self.electron_thread_A = Thread(target=electron_thread_A, args=(self,))
        self.electron_thread_A.start()
        return True
        
    
    def startExperience(self):
        self.experience_thread_A = Thread(target=experience_thread_A, args=(self,))
        self.experience_thread_A.start()
        return True
        
    def addPointsSecondRobot(self):
        if self.objectifEnCours is not None:
            self.objectifEnCours.points += 6;
        return True
    
    def getStockPosition(self, variable):
        count = self.getVariable(variable).get();
        if count >= self.getVariable(variable).getMax():
            return -1
        else:
            return count+1
            
    @functionUI(u'{"controls":['
    '{"arg":"a0","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a1","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a2","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a3","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a4","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a5","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"duration","type":"range","min":0,"max":999,"val":0}'
    ']}')
    def armTestUI(self, a0, a1, a2, a3, a4, a5, duration=0):
        print("got", a0, a1, a2, a3, a4, a5, duration)
        return True
        
    def getDepositPosition(self, variable):
        count = self.getVariable(variable).get();
        return count
        
    def floorGrabPrepare(self):
        #self.floorGrabPrepare_thread_A = Thread(target=floorGrabPrepare_thread_A, args=(self,))
        #self.floorGrabPrepare_thread_A.start()
        floorGrabPrepare_thread_A(self)
        return True
            
    
    def floorGrab(self):
        if self.brasRobotTheo:
            self.brasRobotTheo.armFloorGrab("A");
            time.sleep(0.4)
            self.brasRobotTheo.armDepositPrepare("A");
            time.sleep(0.1)
        
        self.floorGrab_thread_A = Thread(target=floorGrab_thread_A, args=(self,))
        self.floorGrab_thread_A.start()
        self.incrementerVariable("paletsLeft")
        self.incrementerVariable("paletsRight")
        return True
            
    
    def wallGrab(self):
        if not self.recaler(250, "Y", 1403, 90, 0.6, None, True): #self.avancer(100, 0.4):
            if self.brasRobotTheo:
                self.brasRobotTheo.pumpOff("A");
                self.brasRobotTheo.armDefault("A");
                print("Error during wallgrab racalage")
            return False
        self.reculer(100, 0.7)
        if self.brasRobotTheo:
            self.brasRobotTheo.armWallGrab("A");
            self.brasRobotTheo.pumpOn("A");
        if not self.recaler(150, "Y", 1403-55, 90, 0.7, None, True): #self.avancer(100, 0.4):
            if self.brasRobotTheo:
                self.brasRobotTheo.pumpOff("A");
                self.brasRobotTheo.armDefault("A");
                print("Error during wallgrab racalage")
            return False
        self.reculer(200, 0.4) #ignore fails as palets are probably OK
        
        self.wallGrab_thread_A = Thread(target=wallGrab_thread_A_func, args=(self,))
        self.wallGrab_thread_A.start()
        
        self.incrementerVariable("paletsLeft")
        self.incrementerVariable("paletsMiddle")
        self.incrementerVariable("paletsRight")
        return True
            
    
    def grabAcceleratorPalet(self):
        if self.brasRobotTheo:
            self.brasRobotTheo.armWallGrab("M");
            self.brasRobotTheo.pumpOn("M");
        if not self.recaler(150, "Y", 167, -90, 0.6, None, True): #self.avancer(100, 0.4):
            if self.brasRobotTheo:
                self.brasRobotTheo.pumpOff("A");
                self.brasRobotTheo.armDefault("A");
                print("Error during startAccelerator racalage")
            return False
        self.reculer(100, 0.4) #ignore fails as palet is probably OK
        if self.brasRobotTheo:
            self.brasRobotTheo.armDepositPrepare("M");
            middlePos = self.getStockPosition("paletsMiddle")
            self.brasRobotTheo.armStock("M", middlePos)
            self.brasRobotTheo.pumpOff("A");
            time.sleep(0.6)
            self.brasRobotTheo.armDefault("A");
        self.incrementerVariable("paletsMiddle")
        return True
    
    def startDepositDepart(self):
        self.departDepositThread = Thread(target=departDepositThread, args=(self,))
        self.departDepositThread.start()
        return True
        
    def depositDepart(self):
        if self.couleur == "violet":
            self.recaler(350, "X", 2850, 0, 0.6, None, True)
        if self.couleur == "orange":
            self.recaler(350, "X", 150, 180, 0.6, None, True)
        self.reculer(200, 0.6)
        #self.tournerAbsolue(-90)
        return True
            
    
    def depositAccelerator(self):
        if not self.recaler(350, "Y", 167, -90, 0.6, None, True): #self.avancer(100, 0.4):
            if self.brasRobotTheo:
                self.brasRobotTheo.pumpOff("A");
                self.brasRobotTheo.armDepositPrepare("A");
                print("Error during depositAccelerator racalage")
            return False
        self.reculer(100, 0.4) #ignore fails as palet is probably OK
        while self.getRemainingTime()>0 and (not self.getVariable("accelerateur").isMax()) and (self.getVariable("paletsLeft").get()>0 or self.getVariable("paletsMiddle").get()>0 or self.getVariable("paletsRight").get()>0) :
            
            self.brasRobotTheo.armDepositPrepare("A");
            time.sleep(0.8)
            if self.getVariable("accelerateur").get() == 0:
                if self.objectifEnCours is not None:
                    self.objectifEnCours.points += 10;
                    
            if self.getVariable("paletsLeft").get()>0:
                if self.brasRobotTheo:
                    self.brasRobotTheo.armStock("L", self.getDepositPosition("paletsLeft"))
                    self.brasRobotTheo.pumpOn("L");
                self.decrementerVariable("paletsLeft")
                self.incrementerVariable("accelerateur")
                if self.objectifEnCours is not None:
                    self.objectifEnCours.points += 10;
            if self.getVariable("paletsMiddle").get()>0 and self.getVariable("gold").get() == 0:
                if self.brasRobotTheo:
                    self.brasRobotTheo.armStock("M", self.getDepositPosition("paletsMiddle"))
                    self.brasRobotTheo.pumpOn("M");
                self.decrementerVariable("paletsMiddle")
                self.incrementerVariable("accelerateur")
                if self.objectifEnCours is not None:
                    self.objectifEnCours.points += 10;
            if self.getVariable("paletsRight").get()>0:
                if self.brasRobotTheo:
                    self.brasRobotTheo.armStock("R", self.getDepositPosition("paletsRight"))
                    self.brasRobotTheo.pumpOn("R");
                self.decrementerVariable("paletsRight")
                self.incrementerVariable("accelerateur")
                if self.objectifEnCours is not None:
                    self.objectifEnCours.points += 10;
            
            if self.brasRobotTheo:
                time.sleep(0.8)
                self.brasRobotTheo.armFloorGrabPrepare("A");
                time.sleep(0.6)
                self.brasRobotTheo.armWallDeposit("A");
            
            self.recaler(250, "Y", 167, -90, 0.6, None, True)
            if self.brasRobotTheo:
                self.brasRobotTheo.armWallDepositLow("A");
                time.sleep(0.3)
                self.brasRobotTheo.pumpOff("A");
                time.sleep(0.6)
                self.brasRobotTheo.armWallDeposit("A");
            self.reculer(100, 0.4) #ignore fails as palet is probably OK
        if self.brasRobotTheo:
            self.brasRobotTheo.pumpOff("A");
            time.sleep(0.6)
            self.brasRobotTheo.armDefault("A");
        return True
            
    
    def grabGoldPalet(self):
        if self.brasRobotTheo:
            self.brasRobotTheo.armWallGrab("M");
            self.brasRobotTheo.pumpOn("M");
        if not self.recaler(150, "Y", 167, -90, 0.4, None, True): #self.avancer(100, 0.4):
            if self.brasRobotTheo:
                self.brasRobotTheo.pumpOff("A");
                self.brasRobotTheo.armDefault("A");
                print("Error during startAccelerator racalage")
            return False
        self.reculer(100, 0.4) #ignore fails as palet is probably OK
        if self.brasRobotTheo:
            self.brasRobotTheo.armDepositPrepare("M");
            middlePos = 2
            self.brasRobotTheo.armStock("M", middlePos)
            self.brasRobotTheo.pumpOff("A");
            time.sleep(0.6)
            self.brasRobotTheo.armDefault("A");
        self.incrementerVariable("paletsMiddle")
        self.incrementerVariable("paletsMiddle")
        self.incrementerVariable("gold")
        return True
            
    
    def depositBalance(self):
        self.avancer(300,0.4)
        if self.couleur == "orange":
            self.tournerAbsolue(75)
            self.recaler(300, "Y", 1433, 90, 0.6, None, True)
        elif self.couleur == "violet":
            self.tournerAbsolue(105)
            self.recaler(300, "Y", 1433, 90, 0.6, None, True)
        while self.getRemainingTime()>0:
            print("--->recule")
            self.reculer(150, 0.4)
            
            violetRule = (self.getVariable("paletsLeft").get()>0 or self.getVariable("paletsMiddle").get()>0)
            orangeRule = (self.getVariable("paletsRight").get()>0 or self.getVariable("paletsMiddle").get()>0)
            spinLoop = False
            if self.couleur == "orange":
                spinLoop = (not self.getVariable("balance").isMax()) and orangeRule
            else:
                spinLoop = (not self.getVariable("balance").isMax()) and violetRule
            print("--->spinLoop", spinLoop)
            if not spinLoop:
                break
        
            self.depositBalance_thread_A = Thread(target=depositBalance_thread_A_func, args=(self,))
            self.depositBalance_thread_A.start();
            
            time.sleep(4)
            print("--->recaler")
            self.recaler(250, "Y", 1433, 90, 0.6, None, True)
            if self.couleur == "orange":
                self.brasRobotTheo.armWallDepositLow("R");
                self.brasRobotTheo.armWallDepositLow("M");
            elif self.couleur == "violet":
                self.brasRobotTheo.armWallDepositLow("L");
                self.brasRobotTheo.armWallDepositLow("M");
            if self.brasRobotTheo:
                self.brasRobotTheo.pumpOff("A");
                time.sleep(0.6)
            #self.reculer(100, 0.7) #ignore fails as palet is probably OK
        if self.brasRobotTheo:
            self.brasRobotTheo.pumpOff("A");
        self.reculer(250, 0.4) #ignore fails as palet is probably OK
        if self.brasRobotTheo:
            self.brasRobotTheo.armDefault("A");
        return True
        
    
    
    def throw(self):
        while (self.getVariable("paletsLeft").get()>0 or self.getVariable("paletsMiddle").get()>0 or self.getVariable("paletsRight").get()>0) :
            self.brasRobotTheo.armDepositPrepare("A");
            time.sleep(0.4)
            
            side = ""
            if self.getVariable("paletsLeft").get()>0:
                if self.brasRobotTheo:
                    self.brasRobotTheo.armStock("L", self.getDepositPosition("paletsLeft"))
                    self.brasRobotTheo.pumpOn("L");
                    self.decrementerVariable("paletsLeft")
                side = "L"
            elif self.getVariable("paletsRight").get()>0:
                if self.brasRobotTheo:
                    self.brasRobotTheo.armStock("R", self.getDepositPosition("paletsRight"))
                    self.brasRobotTheo.pumpOn("R");
                    self.decrementerVariable("paletsRight")
                side = "R"
            elif self.getVariable("paletsMiddle").get()>0 and self.getVariable("gold").get() == 0:
                if self.brasRobotTheo:
                    self.brasRobotTheo.armStock("M", self.getDepositPosition("paletsMiddle"))
                    self.brasRobotTheo.pumpOn("M");
                    self.decrementerVariable("paletsMiddle")
                side = "M"
            
            if self.brasRobotTheo:
                time.sleep(0.01)
                self.brasRobotTheo.armFloorGrabPrepare("A");
                #time.sleep(0.1)
                self.brasRobotTheo.pumpOff(side);
                #time.sleep(0.3)
                #self.brasRobotTheo.armThrow(side);
                #self.brasRobotTheo.pumpOff(side);
                time.sleep(0.6)
        if self.brasRobotTheo:
            self.brasRobotTheo.armDefault("A");
        return True
    
    def funnyAction(self):
        if self.brasRobotTheo:
            self.brasRobotTheo.pumpOff("A");
            time.sleep(0.6)
            self.brasRobotTheo.armDefault("A");
        


