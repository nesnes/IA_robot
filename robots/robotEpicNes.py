from intelligence.robot import Robot
from robots.cubeDetector import CubeDetector
import time

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
        if not self.brasRobotTheo or not self.brasRobotTheo.isConnected():
            print "ERROR: BrasRobotTheo not detected"
            self.isSimulated = True
        #if not self.ballGatherAlex or not self.ballGatherAlex.isConnected():
        #    print "ERROR: BallGatherAlex not detected"
        #    self.isSimulated = True
        print "init cube detection"
        self.cubeDetector = CubeDetector()

    def identifyCubeOrder(self):
        self.targetCubeOrder = ['green','orange','yellow']
        return True

    def _getTargetCubeFromList(self, cubeList):
        selectedCube = None
        availableCubes = []
        reachable = True
        colorMatch = False
        print "listCube: ", len(cubeList)
        for cube in cubeList:
            print ">", cube["color"], cube["position"][0], cube["position"][1]
            if cube["position"][0] >= 0 and cube["position"][0] <= 100 and cube["position"][1] >= 0 and cube["position"][1] <= 100:
                availableCubes.append(cube)
        if len(self.targetCubeOrder) > 0 and len(self.currentCubeOrder) < 3:
            targetColor = self.targetCubeOrder[len(self.currentCubeOrder)]
            for cube in availableCubes:
                if cube["color"] == targetColor:
                    selectedCube = cube
                    colorMatch = True
                    break
            if not selectedCube:
                for cube in cubeList:
                    if cube["color"] == targetColor:
                        selectedCube = cube
                        reachable = False
                        colorMatch = True
                        break
        if not selectedCube and len(availableCubes) > 0:
            selectedCube = availableCubes[0]
        elif not selectedCube and len(cubeList)>0:
            selectedCube = cubeList[0]
            reachable = False
        if selectedCube and selectedCube["position"][1] <= 35:
            self.reculer(30, 0.4)
        return selectedCube, reachable, colorMatch

    def releaseCubes(self):
        if self.brasRobotTheo:
            self.brasRobotTheo.openTower()
            self.currentCubeOrder = []
            cubeNB = self.getVariable("tourCubes").get()
            score = 0
            if cubeNB == 1:
                score = 1
            if cubeNB == 2:
                score = 3
            if cubeNB == 3:
                score = 6
            if cubeNB == 4:
                score = 10
            if cubeNB == 5:
                score = 15
            if self.objectifEnCours is not None:
                self.objectifEnCours.points = score
            self.resetVariable("tourCubes")
            if not self.reculer(200,0.4):
                return False
            self.brasRobotTheo.closeTower()
        return True


    def homologationAddGoldenCube1(self):
        if self.isSimulated:
            self.incrementerVariable("tourCubes")
            self.decrementerVariable("goldenCube1")
            return True
        if self.brasRobotTheo:
            if self.brasRobotTheo.addGolden1():
                self.incrementerVariable("tourCubes")
                self.decrementerVariable("goldenCube1")
                return True
        return False

    def homologationAddGoldenCube2(self):
        if self.isSimulated:
            self.incrementerVariable("tourCubes")
            self.decrementerVariable("goldenCube2")
            return True
        if self.brasRobotTheo:
            if self.brasRobotTheo.addGolden2():
                self.incrementerVariable("tourCubes")
                self.decrementerVariable("goldenCube2")
                return True
        return False

    def gatherCubes(self):
        goldenAdded = False
        if self.isSimulated:
            self.getVariable("tourCubes").set(5)
            return True
        if self.brasRobotTheo:
            tryingRecovery=False
            while not self.getVariable("tourCubes").isMax():
                self.brasRobotTheo.setFindCubePosition()
                cubeList = self.cubeDetector.getCubeList()
                selectedCube, reachable, colorMatch = self._getTargetCubeFromList(cubeList)
                #Found the perfect cube
                if selectedCube and reachable and colorMatch:
                    print "1 Getting", selectedCube["color"], "at", selectedCube["position"][0], selectedCube["position"][1]
                    if self.brasRobotTheo.grabCube(selectedCube["position"][0], selectedCube["position"][1], selectedCube["rotation"]):
                        self.incrementerVariable("tourCubes")
                        self.currentCubeOrder.append(selectedCube["color"])
                        tryingRecovery = False

                elif selectedCube and not reachable and colorMatch:
                    print "1.5 Getting", selectedCube["color"], "at", selectedCube["position"][0], \
                    selectedCube["position"][1]
                    if tryingRecovery:
                        return False
                    tryingRecovery=True
                    angle = 0
                    distance = 0
                    if selectedCube["position"][0] < 0:
                        angle = -20
                    if selectedCube["position"][0] > 100:
                        angle = 20
                    if selectedCube["position"][1] > 100:
                        distance += 80
                        if selectedCube["position"][1] > 200:
                            distance += 80
                    self.seDeplacerDistanceAngle(distance, angle, 1)
                #add golden one
                elif not goldenAdded and len(cubeList) > 0 and len(self.currentCubeOrder) < 3 and not colorMatch and self.getVariable("goldenCube1").get()>0:
                    print "2 Getting golden 1"
                    if not self.reculer(150, 0.4):
                        return False
                    if self.brasRobotTheo.addGolden1():
                        self.decrementerVariable("goldenCube1")
                        self.incrementerVariable("tourCubes")
                        self.currentCubeOrder.append("*")
                        tryingRecovery = False
                        goldenAdded = True
                    if not self.avancer(150, 0.4):
                        return False
                #add golden 2
                elif not goldenAdded and len(cubeList) > 0 and len(self.currentCubeOrder) < 3 and not colorMatch and self.getVariable("goldenCube2").get()>0:
                    print "3 Getting golden 2"
                    if not self.reculer(150, 0.4):
                        return False
                    if self.brasRobotTheo.addGolden2():
                        self.decrementerVariable("goldenCube2")
                        self.incrementerVariable("tourCubes")
                        self.currentCubeOrder.append("*")
                        tryingRecovery = False
                        goldenAdded = True
                    if not self.avancer(150, 0.4):
                        return False
                #Add available cube
                elif selectedCube and reachable:
                    print "4 Getting", selectedCube["color"], "at", selectedCube["position"][0], selectedCube["position"][1]
                    if self.brasRobotTheo.grabCube(selectedCube["position"][0], selectedCube["position"][1], selectedCube["rotation"]):
                        self.incrementerVariable("tourCubes")
                        self.currentCubeOrder.append(selectedCube["color"])
                        tryingRecovery = False
                #Need to move to the cube
                elif selectedCube:
                    print "5 Moving to", selectedCube["color"], "at", selectedCube["position"][0], selectedCube["position"][1]
                    if tryingRecovery:
                        return False
                    tryingRecovery=True
                    angle = 0
                    distance = 0
                    if selectedCube["position"][0] < 0:
                        angle = -20
                    if selectedCube["position"][0] > 100:
                        angle = 20
                    if selectedCube["position"][1] > 100:
                        distance += 80
                        if selectedCube["position"][1] > 200:
                            distance += 80
                    self.seDeplacerDistanceAngle(distance, angle, 1)
                else:
                    break
        return True

    def lowerBallsBac(self):
        if self.isSimulated:
            return True
        if self.ballGatherAlex:
            return self.ballGatherAlex.bacOpen()

    def closeBallsBac(self):
        if self.isSimulated:
            return True
        if self.ballGatherAlex:
            return self.ballGatherAlex.bacClose()

    def emptyBallsBac(self):
        if self.isSimulated:
            return True
        if self.ballGatherAlex:
            return self.ballGatherAlex.bacEmpty()

    def activerInterrupteur(self):
        if self.isSimulated:
            return True
        if self.brasRobotTheo:
            return self.brasRobotTheo.pushInterrupteur()


    def abeillePrepare(self):
        if self.isSimulated:
            return True
        if self.brasRobotTheo:
            if self.couleur == "green":
                return self.brasRobotTheo.abeillePrepareGreen()
            else:
                return self.brasRobotTheo.abeillePrepare()

    def abeilleFinal(self):
        if self.isSimulated:
            return True
        if self.brasRobotTheo:
            if self.couleur == "green":
                return self.brasRobotTheo.abeilleFinalGreen()
            else:
                return self.brasRobotTheo.abeilleFinal()

    def abeilleClose(self):
        if self.isSimulated:
            return True
        if self.brasRobotTheo:
            return self.brasRobotTheo.abeilleClose()

    def resetArm(self):
        if self.isSimulated:
            return True
        if self.brasRobotTheo:
            return self.brasRobotTheo.setDefaultPosition()

    def armDistributeurPrepare(self):
        if self.isSimulated:
            return True
        if self.brasRobotTheo:
            return self.brasRobotTheo.distributeurPrepare()

    def armDistributeurFinal(self):
        if self.isSimulated:
            return True
        if self.brasRobotTheo:
            return self.brasRobotTheo.distributeurFinal()

    def resetdistributeurPrepare(self):
        if self.isSimulated:
            return True
        if self.brasRobotTheo:
            return self.brasRobotTheo.setDefaultPosition()

    def gatherBalls(self):
        if self.isSimulated:
            self.getVariable("roueBallesValides").set(8)
            return True
        if self.brasRobotTheo and self.ballGatherAlex:
            #self.brasRobotTheo.openBall()
            self.seDeplacerDistanceAngle(0,-40)
            self.ballGatherAlex.bacGather()
            self.seDeplacerDistanceAngle(0,80)
            self.seDeplacerDistanceAngle(0,-40)
            self.ballGatherAlex.bacEmpty()
            return True
            #self.brasRobotTheo.openBallRetract()
            for i in range(0,int(self.getVariable("roueBallesValides").getMax()-2)):
                if not self.getVariable("roueBallesValides").isMax():
                    self.ballGatherAlex.bacGather()
                    if i == self.getVariable("roueBallesValides").getMax()-1:
                        self.ballGatherAlex.bacEmpty()
                    time.sleep(0.8)
                    self.ballGatherAlex.bacOpen()
                    self.ballGatherAlex.stepperGather()
                    gatherColor = self.ballGatherAlex.getGatherColor()
                    if (self.couleur == "green" and gatherColor == 0) \
                    or (self.couleur == "orange" and gatherColor == 1):
                        self.incrementerVariable("roueBallesValides")
                    elif (self.couleur == "green" and gatherColor == 1) \
                    or (self.couleur == "orange" and gatherColor == 0):
                        self.incrementerVariable("roueBallesInvalides")

        return True

    def shouldWeGatherBalls(self):
        return self.getVariable("roueBallesValides").get() + self.getVariable("roueBallesInvalides").get() < 4

    def throwBalls(self):
        if self.isSimulated:
            self.getVariable("roueBallesValides").set(0)
            return True
        if self.brasRobotTheo and self.ballGatherAlex:
            if self.couleur == "green":
                self.ballGatherAlex.setCannonSpeed(230)
            else:
                self.ballGatherAlex.setCannonSpeed(220)
            for i in range(0, int(self.getVariable("roueBallesValides").getMax())):
                if (self.couleur == "green"  and self.ballGatherAlex.getCannonColor() == 0)\
                or (self.couleur == "orange" and self.ballGatherAlex.getCannonColor() == 1):
                    self.ballGatherAlex.cannonOpen()
                    time.sleep(1)
                    self.ballGatherAlex.cannonClose()
                    self.decrementerVariable("roueBallesValides")
                self.ballGatherAlex.stepperSlot()
            self.ballGatherAlex.setCannonSpeed(0)

    def releaseBalls(self):
        if self.isSimulated:
            self.getVariable("roueBallesInvalides").set(0)
            return True
        if self.brasRobotTheo and self.ballGatherAlex:
            for i in range(0, int(self.getVariable("roueBallesInvalides").getMax())):
                if (self.couleur == "green"  and self.ballGatherAlex.getCannonColor() == 1)\
                or (self.couleur == "orange" and self.ballGatherAlex.getCannonColor() == 0):
                    self.ballGatherAlex.trapOpen()
                    time.sleep(1)
                    self.ballGatherAlex.trapClose()
                    self.decrementerVariable("roueBallesInvalides")
                self.ballGatherAlex.stepperSlot()