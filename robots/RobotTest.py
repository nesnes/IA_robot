from intelligence.robot import Robot


class RobotTest(Robot):

    def __init__(self, nom, largeur):
        Robot.__init__(self, nom, largeur)

    def dummyAction(self):
        print("Dummy")
        return True
