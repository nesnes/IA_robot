from intelligence.robot import Robot
from webInterface.interface import RunningState
import webInterface
import time

class RobotGoodEnough(Robot):

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
    
    def __getStockPosition(self, variable):
        count = self.getVariable(variable).get();
        if count >= self.getVariable(variable).getMax():
            return -1
        else:
            return count+1
            
    
    def wallGrab(self):
        #if self.brasRobotTheo:
        #    self.brasRobotTheo.armWallGrab("A");
        #    self.brasRobotTheo.pumpOn("A");
        if not self.avancer(100, 0.4):
            if self.brasRobotTheo:
                self.brasRobotTheo.pumpOff("A");
                self.brasRobotTheo.armDefault("A");
            return False
        self.reculer(100, 0.4) #ignore fails as palets are probably OK
        #if self.brasRobotTheo:
        #    self.brasRobotTheo.armDepositPrepare("A");
        #    self.brasRobotTheo.armStock("L", self.__getStockPosition("paletsLeft"))
        #    self.brasRobotTheo.armStock("M", self.__getStockPosition("paletsMiddle"))
        #    self.brasRobotTheo.armStock("R", self.__getStockPosition("paletsRight"))
        #    self.brasRobotTheo.pumpOff("A");
        #    self.brasRobotTheo.armDefault("A");
        self.incrementerVariable("paletsLeft")
        self.incrementerVariable("paletsMiddle")
        self.incrementerVariable("paletsRight")
        return True


