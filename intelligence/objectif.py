class Objectif:

    def __init__(self,nom,point,temp,repetitions,tabActions,tabConditions):
        self.nom = nom
        self.points = point
        self.temp = temp
        self.repetitions = repetitions
        self.tabActions = tabActions
        self.tabConditions = tabConditions
        self.actionCourante = 0
        self.etat = 0

    def getActions(self):
        return self.tabActions

    def enCours(self):
        self.etat=1
    def isEnCours(self):
        return self.etat == 1

#    def enPause(self):
 #       self.etat=0

    def reset(self):
        self.etat=0
        self.actionCourante=0
    def isEnPause(self):
        return self.etat == 0
    def fini(self):
        self.etat=2
    def isFini(self):
        return self.etat == 2

    def executerActionSuivante(self,robot):
        if self.actionCourante == len(self.tabActions):
            self.fini()
            return True
        else:
            self.enCours()
            succes = self.tabActions[self.actionCourante].executer(robot)
            if succes:
                self.actionCourante += 1
                return True
            else:
                return False


    def executer(self,robot):
        print "===!===",self.nom,"===!==="
        for action in self.tabActions:
            action.executer(robot)

    def getPoints(self):
        return self.points

    def getDuration(self):
        return self.temp

    def estimateValue(self):
        if float(self.getDuration()) == 0 or float(self.getPoints()) == 0:
            return 0.0
        return float(self.getDuration()) / float(self.getPoints())

    def isPossible(self):
        for condition in self.tabConditions:
            if not condition.isTrue():
                return False
        return True
