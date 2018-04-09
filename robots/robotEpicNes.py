from intelligence.robot import Robot
from robots.cubeDetector import CubeDetector

class RobotEpicNes(Robot):

    def __init__(self, nom, largeur):
        Robot.__init__(self, nom, largeur)

    def initialiser(self, chercher, listPointInteret, fenetre=None, simulate=False):
        Robot.initialiser(self, chercher, listPointInteret, fenetre, simulate)
        for board in self.listBoard:
            if board.nom == "BrasRobotTheo":
                self.brasRobotTheo = board
            elif board.nom == "BallGatherAlex":
                self.ballGatherAlex = board
        if not self.brasRobotTheo or not self.brasRobotTheo.isConnected():
            print "ERROR: BrasRobotTheo not detected"
            self.isSimulated = True
        if not self.ballGatherAlex or not self.ballGatherAlex.isConnected():
            print "ERROR: BallGatherAlex not detected"
            self.isSimulated = True
        print "init cube detection"
        self.cubeDetector = CubeDetector()


    def gatherCube(self):
        print "gather cube"
        if self.brasRobotTheo:
            self.brasRobotTheo.setFindCubePosition()
            cubeList = self.cubeDetector.getCubeList()
            selectedCube = None
            for cube in cubeList:
                if cube["position"][0] >= 0 and cube["position"][0] <= 100 and cube["position"][1] >= 0 and cube["position"][1] <= 100:
                    selectedCube = cube
            if selectedCube:
                print "Getting", selectedCube["color"], "cube at",selectedCube["position"][0], selectedCube["position"][1], selectedCube["rotation"]
                if self.brasRobotTheo.grabCube(selectedCube["position"][0], selectedCube["position"][1], selectedCube["rotation"]):
                    self.incrementerVariable("tourCubes")

        return True
