class Objectif:

    def __init__(self,nom,point,temp,dependDe,tabActions):
        self.nom = nom
        self.points = point
        self.temp = temp
        self.dependDe = dependDe
        self.tabActions = tabActions
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
