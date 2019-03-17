from intelligence.robot import Robot
#from robots.cubeDetector import CubeDetector
#import time

class RobotEpicNes(Robot):

    def __init__(self, nom, largeur):
        Robot.__init__(self, nom, largeur)
        self.targetCubeOrder = []
        self.currentCubeOrder = []

    def initialiser(self, chercher, listPointInteret, fenetre=None, simulate=False):
        Robot.initialiser(self, chercher, listPointInteret, fenetre, simulate)
        if simulate != self.isSimulated:
            self.isSimulated = True
            return self.isSimulated
        for board in self.listBoard:
            if board.nom == "BrasRobotTheo":
                self.brasRobotTheo = board
            elif board.nom == "BallGatherAlex":
                self.ballGatherAlex = board
        #if not self.brasRobotTheo or not self.brasRobotTheo.isConnected():
        #    print "ERROR: BrasRobotTheo not detected"
        #    self.isSimulated = True
        #if not self.ballGatherAlex or not self.ballGatherAlex.isConnected():
        #    print "ERROR: BallGatherAlex not detected"
        #    self.isSimulated = True
        #print "init cube detection"
        #self.cubeDetector = CubeDetector()


