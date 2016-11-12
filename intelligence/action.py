class Action:

    def __init__(self,methode,couleur,tabParametres,actionsOnError):
        self.methode = methode
        self.tabParametres = tabParametres
        self.couleur = couleur
        self.actionsOnError = actionsOnError


    def executer(self,robot):
        if self.couleur == '' or self.couleur == robot.couleur:
            print "\t->", self.methode
            success = robot.executer(self)
            if(success):
                return True
            for errorAction in self.actionsOnError: #For each action on error, try to execute them
                print "\t\t  ", self.methode, "a echouee, onError: ", errorAction.methode
                subSuccess = robot.executer(errorAction)
                if(not subSuccess):
                    break
            return False
        else:
            return True